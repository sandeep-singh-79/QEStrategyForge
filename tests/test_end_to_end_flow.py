from __future__ import annotations

import unittest
from pathlib import Path
from uuid import uuid4


class EndToEndFlowTests(unittest.TestCase):
    def make_output_path(self) -> Path:
        temp_dir = Path("tests") / ".tmp" / "end-to-end"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir / f"strategy-{uuid4()}.md"

    def test_run_benchmark_flow_generates_output_and_passes_assertions(self) -> None:
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow

        input_path = Path("benchmarks/brownfield-partial-automation.input.yaml")
        assertions_path = Path("benchmarks/brownfield-partial-automation.assertions.yaml")
        output_path = self.make_output_path()

        result = run_benchmark_flow(input_path, assertions_path, output_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)
        self.assertTrue(output_path.exists())
        self.assertIn("## Executive Summary", output_path.read_text(encoding="utf-8"))
        self.assertEqual(result["validation_errors"], [])
        self.assertEqual(result["assertion_errors"], [])

    def test_run_benchmark_flow_passes_for_greenfield_scenario(self) -> None:
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow

        input_path = Path("benchmarks/greenfield-low-automation.input.yaml")
        assertions_path = Path("benchmarks/greenfield-low-automation.assertions.yaml")
        output_path = self.make_output_path()

        result = run_benchmark_flow(input_path, assertions_path, output_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)

    def test_run_benchmark_flow_passes_for_incomplete_context_scenario(self) -> None:
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow

        input_path = Path("benchmarks/incomplete-context.input.yaml")
        assertions_path = Path("benchmarks/incomplete-context.assertions.yaml")
        output_path = self.make_output_path()

        result = run_benchmark_flow(input_path, assertions_path, output_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)

    def test_run_benchmark_flow_passes_for_strong_automation_scenario(self) -> None:
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow

        input_path = Path("benchmarks/strong-automation-weak-governance.input.yaml")
        assertions_path = Path("benchmarks/strong-automation-weak-governance.assertions.yaml")
        output_path = self.make_output_path()

        result = run_benchmark_flow(input_path, assertions_path, output_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)

    def test_run_benchmark_flow_fails_when_benchmark_assertions_fail(self) -> None:
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow

        assertions_path = Path("tests/.tmp/end-to-end-fail.assertions.yaml")
        assertions_path.parent.mkdir(parents=True, exist_ok=True)
        assertions_path.write_text(
            "\n".join(
                [
                    "must_include_substrings:",
                    '  - "This string should not exist"',
                ]
            ),
            encoding="utf-8",
        )

        input_path = Path("benchmarks/brownfield-partial-automation.input.yaml")
        output_path = self.make_output_path()

        result = run_benchmark_flow(input_path, assertions_path, output_path)

        self.assertFalse(result["success"])
        self.assertEqual(result["exit_code"], 4)
        self.assertTrue(any("Missing required substring" in error for error in result["assertion_errors"]))

    # ------------------------------------------------------------------
    # Phase 11B5 — NFR heavy benchmark (deterministic)
    # ------------------------------------------------------------------

    def test_run_benchmark_flow_passes_for_nfr_heavy_api_scenario(self) -> None:
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow

        input_path = Path("benchmarks/nfr-heavy-api.input.yaml")
        assertions_path = Path("benchmarks/nfr-heavy-api.assertions.yaml")
        output_path = self.make_output_path()

        result = run_benchmark_flow(input_path, assertions_path, output_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["assertion_errors"], [])

    def test_run_benchmark_flow_nfr_scenario_with_empty_nfr_priorities_falls_back_gracefully(self) -> None:
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow

        # Write a minimal valid input without nfr_priorities
        fallback_input = self.make_output_path().with_suffix(".yaml")
        fallback_input.write_text(
            "\n".join([
                "engagement_name: NFR Fallback Test",
                "domain: fintech",
                "delivery_model: Agile",
                "project_posture: brownfield",
                "system_type: REST API platform",
                "existing_automation_state: partial",
                "ci_cd_maturity: partial",
                "environment_maturity: moderate",
                "test_data_maturity: weak",
                "ai_adoption_posture: cautious",
                "strategy_depth: standard",
                "business_goal: Improve API quality",
                "known_constraints:",
                "  - limited test coverage",
            ]),
            encoding="utf-8",
        )
        # Only assert on structure — not on NFR-specific substrings
        minimal_assertions = self.make_output_path().with_suffix(".assertions.yaml")
        minimal_assertions.write_text(
            "must_include_substrings:\n  - \"Non-Functional Priorities:\"\n",
            encoding="utf-8",
        )
        output_path = self.make_output_path()

        result = run_benchmark_flow(fallback_input, minimal_assertions, output_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)

    # ------------------------------------------------------------------
    # Phase 11C — QEStrategyForge self-benchmark
    # ------------------------------------------------------------------

    def test_run_benchmark_flow_self_benchmark_passes_deterministic_flow(self) -> None:
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow

        input_path = Path("benchmarks/qestrategyforge-self.input.yaml")
        assertions_path = Path("benchmarks/qestrategyforge-self.assertions.yaml")
        output_path = self.make_output_path()

        result = run_benchmark_flow(input_path, assertions_path, output_path)

        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["assertion_errors"], [])

    def test_run_benchmark_flow_self_benchmark_fake_llm_exits_4(self) -> None:
        """FakeLLMClient returns brownfield-insurance content; cannot satisfy developer-tooling assertions."""
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow

        # Use a tight assertions file that requires developer-tooling terms absent from _FAKE_STRATEGY
        tight_assertions = self.make_output_path().with_suffix(".assertions.yaml")
        tight_assertions.write_text(
            "must_include_substrings:\n  - \"prompt optimization\"\n  - \"benchmark\"\n",
            encoding="utf-8",
        )
        # Run against a vanilla brownfield input (not the self-benchmark)
        # The renderer won't include those developer-tooling terms → exit 4 proves specificity
        result = run_benchmark_flow(
            Path("benchmarks/brownfield-partial-automation.input.yaml"),
            tight_assertions,
            self.make_output_path(),
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["exit_code"], 4)


class BenchmarkScenarioTests(unittest.TestCase):
    """P12-F: New benchmark scenarios exercise distinct rendering paths."""

    def make_output_path(self) -> Path:
        out_dir = Path("tests/.tmp/benchmark-scenarios")
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir / f"out-{id(self)}.md"

    def test_regulated_brownfield_manual_release_passes(self) -> None:
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow

        result = run_benchmark_flow(
            Path("benchmarks/regulated-brownfield-manual-release.input.yaml"),
            Path("benchmarks/regulated-brownfield-manual-release.assertions.yaml"),
            self.make_output_path(),
        )

        self.assertTrue(result["success"], result.get("assertion_errors"))
        self.assertEqual(result["exit_code"], 0)

    def test_regulated_brownfield_does_not_claim_automated_release_gating(self) -> None:
        """Manual CI/CD + restricted AI must not produce automated gate release guidance."""
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow

        assertions_path = Path("tests/.tmp/benchmark-scenarios/regulated-no-gate.assertions.yaml")
        assertions_path.parent.mkdir(parents=True, exist_ok=True)
        assertions_path.write_text(
            "must_not_include_substrings:\n  - \"automated gate results are the primary release signal\"\n",
            encoding="utf-8",
        )
        result = run_benchmark_flow(
            Path("benchmarks/regulated-brownfield-manual-release.input.yaml"),
            assertions_path,
            self.make_output_path(),
        )

        self.assertTrue(result["success"], result.get("assertion_errors"))

    def test_greenfield_aggressive_timeline_passes(self) -> None:
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow

        result = run_benchmark_flow(
            Path("benchmarks/greenfield-aggressive-timeline.input.yaml"),
            Path("benchmarks/greenfield-aggressive-timeline.assertions.yaml"),
            self.make_output_path(),
        )

        self.assertTrue(result["success"], result.get("assertion_errors"))
        self.assertEqual(result["exit_code"], 0)

    def test_multi_integration_unstable_dependencies_passes(self) -> None:
        from ai_test_strategy_generator.end_to_end_flow import run_benchmark_flow

        result = run_benchmark_flow(
            Path("benchmarks/multi-integration-unstable-dependencies.input.yaml"),
            Path("benchmarks/multi-integration-unstable-dependencies.assertions.yaml"),
            self.make_output_path(),
        )

        self.assertTrue(result["success"], result.get("assertion_errors"))
        self.assertEqual(result["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
