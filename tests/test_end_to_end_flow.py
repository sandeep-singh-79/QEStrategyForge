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


if __name__ == "__main__":
    unittest.main()
