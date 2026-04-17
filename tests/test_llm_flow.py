from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from ai_test_strategy_generator.llm_client import (
    FakeLLMClient,
    GenerationRequest,
    GenerationResponse,
)
from ai_test_strategy_generator.models import LLMConfig, ValidationResult


def _output_dir() -> Path:
    temp_dir = Path("tests") / ".tmp" / "llm-flow"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def _out() -> Path:
    return _output_dir() / f"strategy-{uuid4()}.md"


# ---------------------------------------------------------------------------
# Slice 6.4 — Mocked LLM flow (FakeLLMClient, happy path)
# ---------------------------------------------------------------------------

class LLMBenchmarkFlowTests(unittest.TestCase):
    def test_run_llm_benchmark_flow_succeeds_with_fake_client(self) -> None:
        from ai_test_strategy_generator.llm_flow import run_llm_benchmark_flow

        result = run_llm_benchmark_flow(
            Path("benchmarks/brownfield-partial-automation.input.yaml"),
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            _out(),
            LLMConfig(model="fake"),
            FakeLLMClient(),
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["validation_errors"], [])
        self.assertEqual(result["assertion_errors"], [])

    def test_run_llm_benchmark_flow_writes_output_file(self) -> None:
        from ai_test_strategy_generator.llm_flow import run_llm_benchmark_flow

        output_path = _out()
        run_llm_benchmark_flow(
            Path("benchmarks/brownfield-partial-automation.input.yaml"),
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            output_path,
            LLMConfig(model="fake"),
            FakeLLMClient(),
        )

        self.assertTrue(output_path.exists())
        content = output_path.read_text(encoding="utf-8")
        self.assertIn("## Executive Summary", content)

    def test_run_llm_benchmark_flow_fails_with_exit_code_1_for_missing_input(self) -> None:
        from ai_test_strategy_generator.llm_flow import run_llm_benchmark_flow

        result = run_llm_benchmark_flow(
            Path("benchmarks/does_not_exist.yaml"),
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            _out(),
            LLMConfig(model="fake"),
            FakeLLMClient(),
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["exit_code"], 1)
        self.assertTrue(len(result["validation_errors"]) > 0)

    def test_run_llm_input_package_flow_fails_with_exit_code_2_for_invalid_input(self) -> None:
        from ai_test_strategy_generator.llm_flow import run_llm_input_package_flow
        from ai_test_strategy_generator.models import InputPackage

        bad_package = InputPackage(
            source_path=Path("bad.yaml"),
            raw={},
            normalized={},  # empty normalized data -> validation fails
        )

        result = run_llm_input_package_flow(
            bad_package,
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            _out(),
            LLMConfig(model="fake"),
            FakeLLMClient(),
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["exit_code"], 2)
        self.assertTrue(len(result["validation_errors"]) > 0)


# ---------------------------------------------------------------------------
# Slice 6.5 — Structural validation and constrained repair
# ---------------------------------------------------------------------------

class LLMOutputRepairTests(unittest.TestCase):
    def test_repair_output_adds_all_missing_headings(self) -> None:
        from ai_test_strategy_generator.llm_flow import _repair_output
        from ai_test_strategy_generator.output_validator import validate_output

        partial = "## Executive Summary\nSome incomplete content."
        repaired, _ = _repair_output(partial)
        result = validate_output(repaired)

        self.assertTrue(
            result.is_valid,
            f"Repair did not fix all missing headings/labels: {result.errors}",
        )

    def test_repair_output_adds_missing_labels(self) -> None:
        from ai_test_strategy_generator.llm_flow import _repair_output
        from ai_test_strategy_generator.output_validator import REQUIRED_LABELS

        partial = "## Executive Summary"
        repaired, _ = _repair_output(partial)

        for label in REQUIRED_LABELS:
            self.assertIn(label, repaired, f"Repair did not add missing label: {label}")

    def test_repair_output_does_not_duplicate_present_headings(self) -> None:
        from ai_test_strategy_generator.llm_flow import _repair_output
        from ai_test_strategy_generator.output_validator import REQUIRED_HEADINGS
        from ai_test_strategy_generator.llm_client import FakeLLMClient, GenerationRequest

        client = FakeLLMClient()
        resp = client.generate(GenerationRequest(prompt="x", model="fake"))
        already_valid = resp.text

        repaired, _ = _repair_output(already_valid)

        for heading in REQUIRED_HEADINGS:
            count_before = already_valid.count(heading)
            count_after = repaired.count(heading)
            self.assertEqual(
                count_before,
                count_after,
                f"Repair duplicated heading {heading!r}: before={count_before}, after={count_after}",
            )

    def test_invalid_llm_output_triggers_repair_and_flow_succeeds(self) -> None:
        """End-to-end: structurally invalid LLM output is repaired and validation passes."""
        from ai_test_strategy_generator.llm_flow import run_llm_input_package_flow
        from ai_test_strategy_generator.input_loader import load_input

        class PartialOutputClient:
            def generate(self, req: GenerationRequest) -> GenerationResponse:
                return GenerationResponse(
                    text="## Executive Summary\nIncomplete output with no other sections.",
                    model=req.model,
                )

        input_package = load_input(
            Path("benchmarks/brownfield-partial-automation.input.yaml")
        )
        output_path = _out()

        result = run_llm_input_package_flow(
            input_package,
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            output_path,
            LLMConfig(model="fake"),
            PartialOutputClient(),
        )

        # Validation must pass (repair fixed structural issues)
        self.assertEqual(
            result["validation_errors"],
            [],
            f"Validation errors remain after repair: {result['validation_errors']}",
        )

    def test_deterministic_fallback_is_used_when_repair_validation_still_fails(self) -> None:
        """If validate_output is stubbed to fail for LLM + repair but pass for deterministic,
        the flow must still succeed via the deterministic fallback path."""
        from ai_test_strategy_generator.llm_flow import run_llm_input_package_flow
        from ai_test_strategy_generator.input_loader import load_input

        class BrokenClient:
            def generate(self, req: GenerationRequest) -> GenerationResponse:
                return GenerationResponse(text="not valid", model=req.model)

        call_count: list[int] = [0]

        def mock_validate(markdown: str) -> ValidationResult:
            call_count[0] += 1
            if call_count[0] <= 2:
                # First two calls (LLM output + after repair) simulate persistent failure
                return ValidationResult(is_valid=False, errors=["Stubbed failure"])
            # Third call (deterministic fallback output) passes
            return ValidationResult(is_valid=True, errors=[])

        input_package = load_input(
            Path("benchmarks/brownfield-partial-automation.input.yaml")
        )

        with patch("ai_test_strategy_generator.llm_flow.validate_output", mock_validate):
            result = run_llm_input_package_flow(
                input_package,
                Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
                _out(),
                LLMConfig(model="fake"),
                BrokenClient(),
            )

        self.assertEqual(result["validation_errors"], [])
        # validate_output was called at least 3 times (LLM, repair, deterministic fallback)
        self.assertGreaterEqual(call_count[0], 3)

    def test_flow_returns_exit_code_3_when_all_fallbacks_exhausted(self) -> None:
        """If every validate_output call fails (even deterministic output), exit_code is 3."""
        from ai_test_strategy_generator.llm_flow import run_llm_input_package_flow
        from ai_test_strategy_generator.input_loader import load_input

        class BrokenClient:
            def generate(self, req: GenerationRequest) -> GenerationResponse:
                return GenerationResponse(text="not valid", model=req.model)

        def always_invalid(markdown: str) -> ValidationResult:
            return ValidationResult(is_valid=False, errors=["Always invalid"])

        input_package = load_input(
            Path("benchmarks/brownfield-partial-automation.input.yaml")
        )

        with patch("ai_test_strategy_generator.llm_flow.validate_output", always_invalid):
            result = run_llm_input_package_flow(
                input_package,
                Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
                _out(),
                LLMConfig(model="fake"),
                BrokenClient(),
            )

        self.assertFalse(result["success"])
        self.assertEqual(result["exit_code"], 3)
        self.assertTrue(len(result["validation_errors"]) > 0)


# ---------------------------------------------------------------------------
# Slice 6.6 — Benchmark compatibility
# ---------------------------------------------------------------------------

class LLMBenchmarkCompatibilityTests(unittest.TestCase):
    def test_llm_path_passes_brownfield_benchmark_structural_validation(self) -> None:
        from ai_test_strategy_generator.llm_flow import run_llm_benchmark_flow
        from ai_test_strategy_generator.output_validator import validate_output

        output_path = _out()
        result = run_llm_benchmark_flow(
            Path("benchmarks/brownfield-partial-automation.input.yaml"),
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            output_path,
            LLMConfig(model="fake"),
            FakeLLMClient(),
        )

        content = output_path.read_text(encoding="utf-8")
        validation = validate_output(content)
        self.assertTrue(
            validation.is_valid,
            f"LLM path output failed structural validation: {validation.errors}",
        )

    def test_llm_path_and_deterministic_path_produce_same_required_headings(self) -> None:
        from ai_test_strategy_generator.llm_flow import run_llm_benchmark_flow
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow
        from ai_test_strategy_generator.output_validator import REQUIRED_HEADINGS

        llm_output = _out()
        det_output = _out()

        run_llm_benchmark_flow(
            Path("benchmarks/brownfield-partial-automation.input.yaml"),
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            llm_output,
            LLMConfig(model="fake"),
            FakeLLMClient(),
        )
        run_benchmark_flow(
            Path("benchmarks/brownfield-partial-automation.input.yaml"),
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            det_output,
        )

        llm_content = llm_output.read_text(encoding="utf-8")
        det_content = det_output.read_text(encoding="utf-8")

        for heading in REQUIRED_HEADINGS:
            self.assertIn(heading, llm_content, f"LLM path missing heading: {heading}")
            self.assertIn(heading, det_content, f"Deterministic path missing heading: {heading}")

    def test_llm_path_passes_full_brownfield_benchmark_assertions(self) -> None:
        from ai_test_strategy_generator.llm_flow import run_llm_benchmark_flow

        result = run_llm_benchmark_flow(
            Path("benchmarks/brownfield-partial-automation.input.yaml"),
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            _out(),
            LLMConfig(model="fake"),
            FakeLLMClient(),
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["assertion_errors"], [])


# ---------------------------------------------------------------------------
# Slice 6.7 — Hardening (negative and edge cases)
# ---------------------------------------------------------------------------

class LLMFlowHardeningTests(unittest.TestCase):
    def test_missing_assertions_file_raises_for_llm_path(self) -> None:
        from ai_test_strategy_generator.llm_flow import run_llm_benchmark_flow
        from ai_test_strategy_generator.benchmark_runner import AssertionLoadError

        with self.assertRaises(AssertionLoadError):
            run_llm_benchmark_flow(
                Path("benchmarks/brownfield-partial-automation.input.yaml"),
                Path("benchmarks/nonexistent.assertions.yaml"),
                _out(),
                LLMConfig(model="fake"),
                FakeLLMClient(),
            )

    def test_llm_client_exception_triggers_deterministic_fallback(self) -> None:
        """When the LLM provider raises RuntimeError, the flow must fall back to
        deterministic rendering rather than propagating the exception."""
        from ai_test_strategy_generator.llm_flow import run_llm_input_package_flow
        from ai_test_strategy_generator.input_loader import load_input

        class ErrorClient:
            def generate(self, req: GenerationRequest) -> GenerationResponse:
                raise RuntimeError("Simulated LLM provider failure")

        input_package = load_input(
            Path("benchmarks/brownfield-partial-automation.input.yaml")
        )

        result = run_llm_input_package_flow(
            input_package,
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            _out(),
            LLMConfig(model="fake"),
            ErrorClient(),
        )
        # Must not raise; fallback produces a valid result dict
        self.assertIn(result["exit_code"], (0, 4),
                      msg=f"Expected exit 0 or 4 after fallback, got {result}")

    def test_fake_client_benchmark_fails_assertions_for_greenfield_scenario(self) -> None:
        """FakeLLMClient returns brownfield content; greenfield benchmark must fail assertions
        (demonstrates content specificity — FakeLLMClient is for structural testing only)."""
        from ai_test_strategy_generator.llm_flow import run_llm_benchmark_flow

        result = run_llm_benchmark_flow(
            Path("benchmarks/greenfield-low-automation.input.yaml"),
            Path("benchmarks/greenfield-low-automation.assertions.yaml"),
            _out(),
            LLMConfig(model="fake"),
            FakeLLMClient(),
        )

        # The fake client returns brownfield content, so greenfield-specific assertions fail
        # This proves benchmark assertions are content-sensitive
        self.assertFalse(result["success"])
        self.assertEqual(result["exit_code"], 4)

    def test_llm_flow_output_does_not_contain_forbidden_substrings_from_assertions(self) -> None:
        from ai_test_strategy_generator.llm_flow import run_llm_benchmark_flow

        output_path = _out()
        run_llm_benchmark_flow(
            Path("benchmarks/brownfield-partial-automation.input.yaml"),
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            output_path,
            LLMConfig(model="fake"),
            FakeLLMClient(),
        )

        content = output_path.read_text(encoding="utf-8")
        self.assertNotIn("Project Posture: greenfield", content)
        self.assertNotIn("Current Automation State: none", content)

    def test_llm_config_with_valid_model_name_variants(self) -> None:
        """Confirms LLMConfig accepts typical provider model names."""
        for model in ["gpt-5.4", "gemini-2.0-pro", "glm4:7b", "llama3.1:8b"]:
            config = LLMConfig(model=model)
            self.assertEqual(config.model, model)


class LLMFlowRuntimeErrorFallbackTests(unittest.TestCase):
    """When llm_client.generate() raises RuntimeError, the flow must fall back
    to deterministic rendering and still produce a valid output file."""

    def _make_input_package(self) -> object:
        from pathlib import Path
        from ai_test_strategy_generator.input_loader import load_input
        benchmarks = Path(__file__).parent.parent / "benchmarks"
        return load_input(benchmarks / "brownfield-partial-automation.input.yaml")

    def test_runtime_error_triggers_deterministic_fallback(self) -> None:
        import tempfile
        from pathlib import Path
        from ai_test_strategy_generator.llm_client import GenerationRequest, GenerationResponse
        from ai_test_strategy_generator.llm_flow import run_llm_input_package_flow
        from ai_test_strategy_generator.models import LLMConfig
        from ai_test_strategy_generator.output_validator import validate_output

        class ErroringClient:
            def generate(self, request: GenerationRequest) -> GenerationResponse:
                raise RuntimeError("simulated provider timeout")

        input_package = self._make_input_package()
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            output_path = Path(f.name)
        try:
            result = run_llm_input_package_flow(
                input_package,
                Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
                output_path,
                LLMConfig(model="any-model"),
                ErroringClient(),
            )
            # Fallback must produce a valid strategy, not crash
            self.assertIn(result["exit_code"], (0, 4),
                          msg=f"Expected exit 0 or 4, got {result['exit_code']}: {result}")
            if output_path.exists() and output_path.stat().st_size > 0:
                validation = validate_output(output_path.read_text(encoding="utf-8"))
                self.assertTrue(validation.is_valid,
                                msg=f"Fallback output invalid: {validation.errors}")
        finally:
            output_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Phase 9: Repair edge case tests (B.3 line-anchored fix)
# ---------------------------------------------------------------------------

class LLMRepairEdgeCaseTests(unittest.TestCase):
    """Tests for _repair_output() edge cases introduced with the line-anchored fix."""

    def test_wrong_heading_level_is_not_mistaken_for_valid_heading(self) -> None:
        """### Executive Summary must NOT satisfy the ## Executive Summary requirement."""
        from ai_test_strategy_generator.llm_flow import _repair_output
        from ai_test_strategy_generator.output_validator import validate_output

        # LLM returned H3 for every heading instead of H2
        fake_output = "\n".join(
            f"### {heading.lstrip('# ')}" for heading in [
                "Executive Summary", "Engagement Context",
                "Quality Objectives And Risk Priorities", "Lifecycle Posture",
                "Layered Test Strategy", "Test Types And Coverage Focus",
                "Automation Strategy", "CI/CD And Quality Gates",
                "Test Data Strategy", "Environment Strategy",
                "Defect, Triage, And Reporting Model", "AI Usage Model",
                "Assumptions, Gaps, And Open Questions", "Recommended Next Steps",
            ]
        )
        repaired, _ = _repair_output(fake_output)

        # After repair, all required headings must be present (line-level match)
        result = validate_output(repaired)
        self.assertTrue(
            result.is_valid,
            f"Repair failed to fix wrong heading level. Errors: {result.errors}",
        )

    def test_repair_does_not_overwrite_existing_label_values(self) -> None:
        """If a label is already present (even with a value), repair must NOT append a duplicate."""
        from ai_test_strategy_generator.llm_flow import _repair_output
        from ai_test_strategy_generator.output_validator import REQUIRED_LABELS

        # Build content that has every required label already present
        label_lines = "\n".join(f"{label} already-set-value" for label in REQUIRED_LABELS)
        full_content = _build_minimal_valid_content() + "\n" + label_lines

        repaired, _ = _repair_output(full_content)

        for label in REQUIRED_LABELS:
            count = sum(1 for line in repaired.splitlines() if line.strip().startswith(label))
            self.assertEqual(count, 1, f"Label {label!r} was duplicated after repair (count={count})")

    def test_empty_llm_response_repair_produces_all_headings_and_labels(self) -> None:
        """Completely empty LLM output → repair must inject ALL required headings and labels."""
        from ai_test_strategy_generator.llm_flow import _repair_output
        from ai_test_strategy_generator.output_validator import (
            REQUIRED_HEADINGS,
            REQUIRED_LABELS,
            validate_output,
        )

        repaired, _ = _repair_output("")

        result = validate_output(repaired)
        self.assertTrue(result.is_valid, f"Repair of empty string is still invalid: {result.errors}")
        for heading in REQUIRED_HEADINGS:
            self.assertIn(heading, repaired, f"Missing heading after repair: {heading!r}")
        for label in REQUIRED_LABELS:
            self.assertTrue(
                any(line.strip().startswith(label) for line in repaired.splitlines()),
                f"Missing label after repair: {label!r}",
            )

    def test_content_wrapped_in_code_fence_still_gets_missing_headings_appended(self) -> None:
        """Output wrapped in a markdown code fence should still receive missing headings."""
        from ai_test_strategy_generator.llm_flow import _repair_output
        from ai_test_strategy_generator.output_validator import validate_output

        fenced = "```markdown\n## Executive Summary\nSome content.\n```"
        repaired, _ = _repair_output(fenced)

        # Repair appends outside the fence; validate_output uses substring search, so it passes
        result = validate_output(repaired)
        self.assertTrue(result.is_valid, f"After repair: {result.errors}")


def _build_minimal_valid_content() -> str:
    """Return markdown with all required headings but no label lines."""
    from ai_test_strategy_generator.output_validator import REQUIRED_HEADINGS
    return "\n\n".join(f"{h}\nContent." for h in REQUIRED_HEADINGS)


# ------------------------------------------------------------------
# Phase 11B5 — NFR benchmark through LLM flow
# ------------------------------------------------------------------

class NFRBenchmarkLLMFlowTests(unittest.TestCase):
    def test_nfr_benchmark_llm_flow_output_contains_nfr_label(self) -> None:
        """NFR benchmark flow should produce output with Non-Functional Priorities: label."""
        from ai_test_strategy_generator.llm_flow import run_llm_benchmark_flow
        from ai_test_strategy_generator.models import LLMConfig

        # Use a minimal assertions file that only checks the NFR label presence
        assertions_path = Path("tests/.tmp/llm-flow") / "nfr-minimal.assertions.yaml"
        assertions_path.parent.mkdir(parents=True, exist_ok=True)
        assertions_path.write_text(
            "must_include_substrings:\n  - \"Non-Functional Priorities:\"\n",
            encoding="utf-8",
        )

        result = run_llm_benchmark_flow(
            Path("benchmarks/nfr-heavy-api.input.yaml"),
            assertions_path,
            _out(),
            LLMConfig(model="fake"),
            FakeLLMClient(),
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["assertion_errors"], [])


# ------------------------------------------------------------------
# Phase 11C — QEStrategyForge self-benchmark LLM flow
# ------------------------------------------------------------------

class SelfBenchmarkLLMFlowTests(unittest.TestCase):
    def test_self_benchmark_fake_llm_exits_4_proving_domain_specificity(self) -> None:
        """FakeLLMClient returns brownfield-insurance content.
        Self-benchmark requires developer-tooling terms → assertions fail → exit 4.
        This proves the system is NOT generating generic content.
        """
        from ai_test_strategy_generator.llm_flow import run_llm_benchmark_flow
        from ai_test_strategy_generator.models import LLMConfig

        result = run_llm_benchmark_flow(
            Path("benchmarks/qestrategyforge-self.input.yaml"),
            Path("benchmarks/qestrategyforge-self.assertions.yaml"),
            _out(),
            LLMConfig(model="fake"),
            FakeLLMClient(),
        )

        # FakeLLMClient does not produce developer-tooling content →
        # assertions for "prompt optimization", "benchmark" etc. must fail
        self.assertFalse(result["success"])
        self.assertEqual(result["exit_code"], 4)
        self.assertTrue(len(result["assertion_errors"]) > 0)


if __name__ == "__main__":
    unittest.main()
