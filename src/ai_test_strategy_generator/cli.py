from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from ai_test_strategy_generator.artifact_end_to_end_flow import run_artifact_benchmark_flow
from ai_test_strategy_generator.client_factory import create_llm_client
from ai_test_strategy_generator.comparison import build_comparison_report
from ai_test_strategy_generator.config_loader import load_config
from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow
from ai_test_strategy_generator.llm_flow import (
    run_llm_artifact_benchmark_flow,
    run_llm_benchmark_flow,
)
from ai_test_strategy_generator.main import run_validation
from ai_test_strategy_generator.models import LLMConfig, ProviderConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-test-strategy-generator",
        description="AI Test Strategy Generator — input validation and strategy generation.",
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to the v1 YAML input file (omit when using --artifact-folder).",
    )
    parser.add_argument(
        "--mode",
        choices=["deterministic", "llm_assisted"],
        default="deterministic",
        help="Generation mode. Choices: deterministic (default), llm_assisted.",
    )
    parser.add_argument(
        "--assertions",
        default=None,
        help="Path to the assertions YAML file. Required for generation mode.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path for the generated strategy markdown output. Required with --assertions.",
    )
    parser.add_argument(
        "--artifact-folder",
        dest="artifact_folder",
        default=None,
        help="Path to an artifact folder (alternative to input_file).",
    )
    parser.add_argument(
        "--provider",
        default=None,
        help="LLM provider name: ollama | openai | gemini. Required for llm_assisted mode.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="LLM model name (overrides config file and env var).",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to a strategy.config.yaml config file.",
    )
    parser.add_argument(
        "--base-url",
        dest="base_url",
        default=None,
        help="LLM provider base URL (overrides config file and env var).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Sampling temperature 0.0–2.0 (overrides config file and env var).",
    )
    parser.add_argument(
        "--max-tokens",
        dest="max_tokens",
        type=int,
        default=None,
        help="Maximum output tokens (overrides config file and env var).",
    )
    parser.add_argument(
        "--compare",
        default=None,
        metavar="COMPARE_FILE",
        help="Generate a deterministic-vs-LLM comparison report saved to this .md path.",
    )
    return parser


def _build_provider_config(args: argparse.Namespace) -> ProviderConfig:
    """Merge config file, env vars, and CLI flags into a ProviderConfig (layer 4 wins)."""
    config_path = Path(args.config) if args.config else None
    raw = load_config(config_path)

    # Layer 4 — CLI flags override everything
    if args.provider is not None:
        raw["provider"] = args.provider
    if args.model is not None:
        raw["model"] = args.model
    if args.base_url is not None:
        raw["base_url"] = args.base_url
    if args.temperature is not None:
        raw["temperature"] = args.temperature
    if args.max_tokens is not None:
        raw["max_tokens"] = args.max_tokens

    # api_key comes exclusively from the environment (never from config file)
    api_key = os.environ.get("STRATEGY_LLM_API_KEY") or None

    return ProviderConfig(**raw, api_key=api_key)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    has_input = bool(args.input_file)
    has_artifact = bool(args.artifact_folder)

    if not has_input and not has_artifact:
        parser.error("one of input_file or --artifact-folder is required")

    # -------------------------------------------------------------------
    # Backward-compatible validation mode: no --assertions supplied
    # -------------------------------------------------------------------
    if not args.assertions:
        if not has_input:
            parser.error("input_file is required in validation mode (no --assertions given)")
        raise SystemExit(run_validation(args.input_file))

    # -------------------------------------------------------------------
    # Generation mode: --assertions requires --output
    # -------------------------------------------------------------------
    if not args.output:
        parser.error("--output is required when --assertions is specified")

    mode = args.mode

    if mode == "llm_assisted":
        if not args.provider:
            parser.error("--provider is required for --mode llm_assisted")

        try:
            provider_config = _build_provider_config(args)
        except ValueError as exc:
            parser.error(str(exc))
            return  # unreachable; satisfies type checker

        try:
            llm_client = create_llm_client(provider_config)
        except ValueError as exc:
            parser.error(str(exc))
            return

        llm_config = LLMConfig(
            model=provider_config.model,
            max_tokens=provider_config.max_tokens,
            temperature=provider_config.temperature,
        )

        if has_artifact:
            result = run_llm_artifact_benchmark_flow(
                args.artifact_folder, args.assertions, args.output, llm_config, llm_client
            )
        else:
            result = run_llm_benchmark_flow(
                args.input_file, args.assertions, args.output, llm_config, llm_client
            )

        if args.compare and result["exit_code"] in (0, 4):
            _write_comparison(args, has_artifact, llm_config, result["output_path"])
    else:
        # deterministic
        if has_artifact:
            result = run_artifact_benchmark_flow(
                args.artifact_folder, args.assertions, args.output
            )
        else:
            result = run_benchmark_flow(args.input_file, args.assertions, args.output)

    raise SystemExit(result["exit_code"])


def _write_comparison(
    args: argparse.Namespace,
    has_artifact: bool,
    llm_config: LLMConfig,
    llm_output_path: str,
) -> None:
    """Run the deterministic flow and write a side-by-side comparison report."""
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        det_out = Path(f.name)
    try:
        if has_artifact:
            run_artifact_benchmark_flow(args.artifact_folder, args.assertions, str(det_out))
        else:
            run_benchmark_flow(args.input_file, args.assertions, str(det_out))

        det_markdown = det_out.read_text(encoding="utf-8") if det_out.exists() else ""
    finally:
        det_out.unlink(missing_ok=True)

    llm_path = Path(llm_output_path)
    llm_markdown = llm_path.read_text(encoding="utf-8") if llm_path.exists() else ""

    input_description = args.artifact_folder if has_artifact else args.input_file
    report = build_comparison_report(input_description, det_markdown, llm_markdown)

    compare_path = Path(args.compare)
    compare_path.parent.mkdir(parents=True, exist_ok=True)
    compare_path.write_text(report, encoding="utf-8")
