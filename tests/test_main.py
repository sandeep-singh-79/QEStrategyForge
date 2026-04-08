from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from uuid import uuid4

from ai_test_strategy_generator.main import run_validation


class MainTests(unittest.TestCase):
    def make_workspace_file(self) -> Path:
        temp_dir = Path("tests") / ".tmp" / str(uuid4())
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir / "input.yaml"

    def test_run_validation_returns_zero_for_valid_input(self) -> None:
        input_file = self.make_workspace_file()
        input_file.write_text(
            "\n".join(
                [
                    "engagement_name: Example",
                    "project_posture: brownfield",
                    "system_type: legacy enterprise",
                    "existing_automation_state: partial",
                    "ci_cd_maturity: partial",
                    "environment_maturity: moderate",
                    "test_data_maturity: moderate",
                    "ai_adoption_posture: cautious",
                    "strategy_depth: standard",
                    "business_goal: Improve quality",
                    "known_constraints:",
                    "  - limited QE capacity",
                ]
            ),
            encoding="utf-8",
        )

        output = StringIO()
        with redirect_stdout(output):
            rc = run_validation(input_file)

        self.assertEqual(rc, 0)
        self.assertIn("VALIDATION PASS", output.getvalue())

    def test_run_validation_returns_two_for_invalid_input(self) -> None:
        input_file = self.make_workspace_file()
        input_file.write_text("engagement_name: Example\n", encoding="utf-8")

        output = StringIO()
        with redirect_stdout(output):
            rc = run_validation(input_file)

        self.assertEqual(rc, 2)
        self.assertIn("VALIDATION FAIL", output.getvalue())

    def test_run_validation_returns_one_for_missing_file(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            rc = run_validation("missing-file.yaml")

        self.assertEqual(rc, 1)
        self.assertIn("LOAD FAIL", output.getvalue())

    def test_run_validation_returns_one_for_invalid_yaml(self) -> None:
        input_file = self.make_workspace_file()
        input_file.write_text("engagement_name: [broken\n", encoding="utf-8")

        output = StringIO()
        with redirect_stdout(output):
            rc = run_validation(input_file)

        self.assertEqual(rc, 1)
        self.assertIn("LOAD FAIL", output.getvalue())


if __name__ == "__main__":
    unittest.main()
