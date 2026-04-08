from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


class BenchmarkRunnerTests(unittest.TestCase):
    def make_assertions_file(self, content: str) -> Path:
        temp_dir = Path("tests") / ".tmp" / "benchmark-runner"
        temp_dir.mkdir(parents=True, exist_ok=True)
        file_path = temp_dir / f"assertions-{len(list(temp_dir.glob('*.yaml')))}.yaml"
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def test_run_assertions_passes_when_all_conditions_met(self) -> None:
        from ai_test_strategy_generator.benchmark_runner import run_assertions

        assertions_file = self.make_assertions_file(
            "\n".join(
                [
                    "must_include_headings:",
                    '  - "## Executive Summary"',
                    "must_include_labels:",
                    '  - "Project Posture: brownfield"',
                    "must_include_substrings:",
                    '  - "Missing Information:"',
                    "must_not_include_substrings:",
                    '  - "Project Posture: greenfield"',
                ]
            )
        )
        markdown = "\n".join(
            [
                "## Executive Summary",
                "Project Posture: brownfield",
                "Missing Information: architecture details",
            ]
        )

        result = run_assertions(markdown, assertions_file)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_run_assertions_fails_for_missing_required_content(self) -> None:
        from ai_test_strategy_generator.benchmark_runner import run_assertions

        assertions_file = self.make_assertions_file(
            "\n".join(
                [
                    "must_include_headings:",
                    '  - "## Executive Summary"',
                    "must_include_labels:",
                    '  - "Project Posture: brownfield"',
                ]
            )
        )
        markdown = "## Something Else\n"

        result = run_assertions(markdown, assertions_file)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("Missing required heading" in error for error in result.errors))
        self.assertTrue(any("Missing required label" in error for error in result.errors))

    def test_run_assertions_fails_for_forbidden_substrings(self) -> None:
        from ai_test_strategy_generator.benchmark_runner import run_assertions

        assertions_file = self.make_assertions_file(
            "\n".join(
                [
                    "must_not_include_substrings:",
                    '  - "Project Posture: greenfield"',
                ]
            )
        )
        markdown = "Project Posture: greenfield\n"

        result = run_assertions(markdown, assertions_file)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("Forbidden substring present" in error for error in result.errors))

    def test_run_assertions_raises_for_invalid_assertions_file(self) -> None:
        from ai_test_strategy_generator.benchmark_runner import AssertionLoadError, run_assertions

        assertions_file = self.make_assertions_file("- not-a-mapping\n")

        with self.assertRaises(AssertionLoadError):
            run_assertions("## Executive Summary\n", assertions_file)


if __name__ == "__main__":
    unittest.main()
