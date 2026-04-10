"""Live Ollama integration test (Slice 7.7).

Requires a local Ollama instance running at http://localhost:11434 with a model
loaded (default: glm4:latest). The test is automatically SKIPPED when Ollama is
not reachable, so it never blocks CI.

Run explicitly:
    pytest tests/test_live_ollama.py -v

Or with a different model:
    STRATEGY_LLM_MODEL=llama3 pytest tests/test_live_ollama.py -v
"""
from __future__ import annotations

import os
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from ai_test_strategy_generator.client_factory import create_llm_client
from ai_test_strategy_generator.config_loader import load_config
from ai_test_strategy_generator.llm_flow import run_llm_benchmark_flow
from ai_test_strategy_generator.models import LLMConfig, ProviderConfig
from ai_test_strategy_generator.output_validator import validate_output

_OLLAMA_BASE_URL = os.environ.get("STRATEGY_LLM_BASE_URL", "http://localhost:11434")
_BENCHMARK_ROOT = Path(__file__).parent.parent / "benchmarks"


def _ollama_reachable() -> bool:
    """Return True if Ollama health endpoint responds within 2 seconds."""
    try:
        with urllib.request.urlopen(
            f"{_OLLAMA_BASE_URL.rstrip('/')}/api/tags", timeout=2
        ):
            return True
    except Exception:
        return False


@unittest.skipUnless(_ollama_reachable(), f"Ollama not reachable at {_OLLAMA_BASE_URL}")
class TestLiveOllamaBenchmark(unittest.TestCase):
    """End-to-end benchmark run through a live Ollama instance.

    Accepts either structural success (exit 0) or clean deterministic fallback
    (output passes validate_output), which is the defined contract for the
    LLM-assisted flow when the LLM produces structurally invalid output.
    """

    def _make_provider_config(self) -> ProviderConfig:
        raw = load_config(None)
        raw["provider"] = "ollama"
        raw["base_url"] = _OLLAMA_BASE_URL
        # Use STRATEGY_LLM_MODEL env var if set; otherwise use glm-5:cloud
        if "STRATEGY_LLM_MODEL" not in os.environ:
            raw["model"] = "glm-5:cloud"
        return ProviderConfig(**raw)

    def test_brownfield_benchmark_produces_valid_output(self) -> None:
        input_path = _BENCHMARK_ROOT / "brownfield-partial-automation.input.yaml"
        assertions_path = _BENCHMARK_ROOT / "brownfield-partial-automation.assertions.yaml"

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            output_path = Path(f.name)
        try:
            provider_config = self._make_provider_config()
            llm_client = create_llm_client(provider_config)
            llm_config = LLMConfig(
                model=provider_config.model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
            result = run_llm_benchmark_flow(
                input_path, assertions_path, output_path, llm_config, llm_client
            )
            # The flow must not crash; output must pass structural validation
            # (LLM success = exit 0; deterministic fallback = exit 0 too after repair)
            self.assertIn(
                result["exit_code"],
                (0, 4),  # 0 = full pass, 4 = assertions not met (structural ok)
                msg=f"Unexpected exit code {result['exit_code']}.\n"
                    f"Validation errors: {result['validation_errors']}\n"
                    f"Assertion errors: {result['assertion_errors']}",
            )
            if output_path.exists() and output_path.stat().st_size > 0:
                markdown = output_path.read_text(encoding="utf-8")
                validation = validate_output(markdown)
                self.assertTrue(
                    validation.is_valid,
                    msg=f"Output failed structural validation: {validation.errors}",
                )
        finally:
            output_path.unlink(missing_ok=True)

    def test_greenfield_artifact_benchmark_via_ollama(self) -> None:
        from ai_test_strategy_generator.artifact_loader import load_artifact_folder
        from ai_test_strategy_generator.artifact_mapping import map_artifact_bundle
        from ai_test_strategy_generator.llm_flow import run_llm_input_package_flow

        artifact_folder = _BENCHMARK_ROOT / "artifact-greenfield"
        assertions_path = _BENCHMARK_ROOT / "artifact-greenfield.assertions.yaml"

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            output_path = Path(f.name)
        try:
            bundle = load_artifact_folder(artifact_folder)
            input_package = map_artifact_bundle(bundle)
            provider_config = self._make_provider_config()
            llm_client = create_llm_client(provider_config)
            llm_config = LLMConfig(
                model=provider_config.model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
            result = run_llm_input_package_flow(
                input_package, assertions_path, output_path, llm_config, llm_client
            )
            self.assertIn(
                result["exit_code"],
                (0, 4),
                msg=f"Unexpected exit code {result['exit_code']}.\n"
                    f"Validation errors: {result['validation_errors']}\n"
                    f"Assertion errors: {result['assertion_errors']}",
            )
        finally:
            output_path.unlink(missing_ok=True)

    def test_greenfield_benchmark_produces_valid_output(self) -> None:
        input_path = _BENCHMARK_ROOT / "greenfield-low-automation.input.yaml"
        assertions_path = _BENCHMARK_ROOT / "greenfield-low-automation.assertions.yaml"

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            output_path = Path(f.name)
        try:
            provider_config = self._make_provider_config()
            llm_client = create_llm_client(provider_config)
            llm_config = LLMConfig(
                model=provider_config.model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
            result = run_llm_benchmark_flow(
                input_path, assertions_path, output_path, llm_config, llm_client
            )
            self.assertIn(
                result["exit_code"],
                (0, 4),
                msg=f"Unexpected exit code {result['exit_code']}.\n"
                    f"Validation errors: {result['validation_errors']}\n"
                    f"Assertion errors: {result['assertion_errors']}",
            )
        finally:
            output_path.unlink(missing_ok=True)

    def test_incomplete_context_benchmark_produces_valid_output(self) -> None:
        input_path = _BENCHMARK_ROOT / "incomplete-context.input.yaml"
        assertions_path = _BENCHMARK_ROOT / "incomplete-context.assertions.yaml"

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            output_path = Path(f.name)
        try:
            provider_config = self._make_provider_config()
            llm_client = create_llm_client(provider_config)
            llm_config = LLMConfig(
                model=provider_config.model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
            result = run_llm_benchmark_flow(
                input_path, assertions_path, output_path, llm_config, llm_client
            )
            self.assertIn(
                result["exit_code"],
                (0, 4),
                msg=f"Unexpected exit code {result['exit_code']}.\n"
                    f"Validation errors: {result['validation_errors']}\n"
                    f"Assertion errors: {result['assertion_errors']}",
            )
        finally:
            output_path.unlink(missing_ok=True)

    def test_strong_automation_benchmark_produces_valid_output(self) -> None:
        input_path = _BENCHMARK_ROOT / "strong-automation-weak-governance.input.yaml"
        assertions_path = _BENCHMARK_ROOT / "strong-automation-weak-governance.assertions.yaml"

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            output_path = Path(f.name)
        try:
            provider_config = self._make_provider_config()
            llm_client = create_llm_client(provider_config)
            llm_config = LLMConfig(
                model=provider_config.model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
            result = run_llm_benchmark_flow(
                input_path, assertions_path, output_path, llm_config, llm_client
            )
            self.assertIn(
                result["exit_code"],
                (0, 4),
                msg=f"Unexpected exit code {result['exit_code']}.\n"
                    f"Validation errors: {result['validation_errors']}\n"
                    f"Assertion errors: {result['assertion_errors']}",
            )
        finally:
            output_path.unlink(missing_ok=True)

    def test_artifact_brownfield_benchmark_via_ollama(self) -> None:
        from ai_test_strategy_generator.llm_flow import run_llm_artifact_benchmark_flow

        artifact_folder = _BENCHMARK_ROOT / "artifact-brownfield"
        assertions_path = _BENCHMARK_ROOT / "artifact-brownfield.assertions.yaml"

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            output_path = Path(f.name)
        try:
            provider_config = self._make_provider_config()
            llm_client = create_llm_client(provider_config)
            llm_config = LLMConfig(
                model=provider_config.model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
            result = run_llm_artifact_benchmark_flow(
                artifact_folder, assertions_path, output_path, llm_config, llm_client
            )
            self.assertIn(
                result["exit_code"],
                (0, 4),
                msg=f"Unexpected exit code {result['exit_code']}.\n"
                    f"Validation errors: {result['validation_errors']}\n"
                    f"Assertion errors: {result['assertion_errors']}",
            )
        finally:
            output_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
