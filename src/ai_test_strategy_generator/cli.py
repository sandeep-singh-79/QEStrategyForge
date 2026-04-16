from __future__ import annotations

import argparse
import datetime
import os
import sys
import tempfile
from pathlib import Path

import yaml

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
from ai_test_strategy_generator.llm_client import LLMClient
from ai_test_strategy_generator.prompt_optimizer import (
    BenchmarkSpec,
    OptimizationConfig,
    run_optimization_loop,
)


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
    parser.add_argument(
        "--optimize",
        action="store_true",
        default=False,
        help="Run the Karpathy-style prompt optimization loop instead of single generation.",
    )
    parser.add_argument(
        "--optimize-iterations",
        dest="optimize_iterations",
        type=int,
        default=5,
        help="Number of optimization iterations (default: 5). Used with --optimize.",
    )
    parser.add_argument(
        "--optimize-timeout",
        dest="optimize_timeout",
        type=int,
        default=300,
        help="Wall-clock timeout in seconds per iteration (default: 300). Used with --optimize.",
    )
    parser.add_argument(
        "--optimize-output-dir",
        dest="optimize_output_dir",
        default=None,
        metavar="DIR",
        help="Directory to save optimization run artefacts (scoreboard, prompt snapshots).",
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

        if args.optimize:
            raise SystemExit(_run_optimization(args, llm_config, llm_client))

        if has_artifact:
            result = run_llm_artifact_benchmark_flow(
                args.artifact_folder, args.assertions, args.output, llm_config, llm_client
            )
        else:
            result = run_llm_benchmark_flow(
                args.input_file, args.assertions, args.output, llm_config, llm_client
            )

        if args.compare and result["exit_code"] in (0, 4):
            _write_comparison(args, has_artifact, llm_config, result["output_path"], result.get("repair_stats"))
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
    repair_stats: dict[str, object] | None = None,
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
    report = build_comparison_report(input_description, det_markdown, llm_markdown, repair_stats=repair_stats)

    compare_path = Path(args.compare)
    compare_path.parent.mkdir(parents=True, exist_ok=True)
    compare_path.write_text(report, encoding="utf-8")


def _run_optimization(
    args: argparse.Namespace,
    llm_config: LLMConfig,
    llm_client: LLMClient,
) -> int:
    """Run the Karpathy optimization loop and return an exit code."""
    if not args.assertions:
        print("ERROR: --optimize requires --assertions <path>", file=sys.stderr)
        return 1
    if not args.input_file:
        print("ERROR: --optimize requires an input_file", file=sys.stderr)
        return 1

    specs = [BenchmarkSpec(args.input_file, args.assertions)]
    prompt_dir = Path(__file__).parent / "prompts" / "v1"

    output_dir: Path | None = None
    if args.optimize_output_dir:
        ts = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        output_dir = Path(args.optimize_output_dir) / f"run_{ts}"
        output_dir.mkdir(parents=True, exist_ok=True)

    # Use OptimizationConfig default mutations — no need to duplicate them here.
    opt_config = OptimizationConfig(
        prompt_dir=prompt_dir,
        n_iterations=args.optimize_iterations,
        timeout_per_iter=args.optimize_timeout,
    )

    result = run_optimization_loop(specs, llm_config, llm_client, opt_config, output_dir)
    print(result.summary())

    if output_dir:
        # Always write scoreboard for audit, regardless of whether score improved.
        scoreboard = {
            "baseline_aggregate": result.baseline_aggregate,
            "best_aggregate": result.best_aggregate,
            "best_iteration": result.best_iteration,
            "improvement_delta": result.improvement_delta,
            "improved": result.improved(),
            "iterations": [
                {
                    "iteration": r.iteration,
                    "mutation_strategy": r.mutation_strategy,
                    "mutation_description": r.mutation_description,
                    "per_benchmark_scores": r.per_benchmark_scores,
                    "aggregate": r.aggregate,
                    "is_best": r.is_best,
                    "timed_out": r.timed_out,
                }
                for r in result.records
            ],
        }
        (output_dir / "scoreboard.yaml").write_text(
            yaml.dump(scoreboard, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        print(f"Scoreboard saved to {output_dir / 'scoreboard.yaml'}")
        if result.improved():
            print(
                f"\nTo promote the winner, copy {result.best_prompt_dir} to "
                f"src/ai_test_strategy_generator/prompts/v2/ and update "
                f"prompt_builder.py to use version='v2'."
            )

    return 0
