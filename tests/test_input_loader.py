from __future__ import annotations

import unittest
from pathlib import Path
from uuid import uuid4

from ai_test_strategy_generator.input_loader import InputLoadError, load_input


class InputLoaderTests(unittest.TestCase):
    def make_workspace_file(self) -> Path:
        temp_dir = Path("tests") / ".tmp" / str(uuid4())
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir / "input.yaml"

    def test_load_input_normalizes_list_fields(self) -> None:
        input_file = self.make_workspace_file()
        input_file.write_text(
            "\n".join(
                [
                    "engagement_name: Example",
                    "project_posture: brownfield",
                    "system_type: legacy enterprise",
                    "existing_automation_state: partial",
                    "ci_cd_maturity: partial",
                    "ai_adoption_posture: cautious",
                    "strategy_depth: standard",
                    "business_goal: Improve quality",
                    "delivery_risks:",
                    "  - integration instability",
                ]
            ),
            encoding="utf-8",
        )

        package = load_input(input_file)

        self.assertEqual(package.normalized["engagement_name"], "Example")
        self.assertEqual(package.normalized["delivery_risks"], ["integration instability"])
        self.assertEqual(package.normalized["critical_business_flows"], [])
        self.assertEqual(package.normalized["missing_information"], [])

    def test_load_input_raises_for_missing_file(self) -> None:
        with self.assertRaises(InputLoadError):
            load_input("does-not-exist.yaml")

    def test_load_input_raises_for_non_mapping_yaml(self) -> None:
        input_file = self.make_workspace_file()
        input_file.write_text("- not-a-mapping\n", encoding="utf-8")

        with self.assertRaises(InputLoadError):
            load_input(input_file)

    def test_load_input_raises_for_unsupported_extension(self) -> None:
        input_file = self.make_workspace_file().with_suffix(".json")
        input_file.write_text("{}", encoding="utf-8")

        with self.assertRaises(InputLoadError):
            load_input(input_file)

    def test_load_input_raises_for_invalid_yaml(self) -> None:
        input_file = self.make_workspace_file()
        input_file.write_text("engagement_name: [broken\n", encoding="utf-8")

        with self.assertRaises(InputLoadError):
            load_input(input_file)

    def test_load_input_wraps_scalar_list_fields_into_lists(self) -> None:
        input_file = self.make_workspace_file()
        input_file.write_text(
            "\n".join(
                [
                    "engagement_name: Example",
                    "project_posture: brownfield",
                    "system_type: legacy enterprise",
                    "existing_automation_state: partial",
                    "ci_cd_maturity: partial",
                    "ai_adoption_posture: cautious",
                    "strategy_depth: standard",
                    "business_goal: Improve quality",
                    "delivery_risks: integration instability",
                ]
            ),
            encoding="utf-8",
        )

        package = load_input(input_file)

        self.assertEqual(package.normalized["delivery_risks"], ["integration instability"])

    # ------------------------------------------------------------------
    # Phase 11B1 — nfr_priorities as list field
    # ------------------------------------------------------------------

    def test_load_input_preserves_nfr_priorities_as_list(self) -> None:
        input_file = self.make_workspace_file()
        input_file.write_text(
            "\n".join([
                "engagement_name: NFR Test",
                "project_posture: brownfield",
                "system_type: API",
                "existing_automation_state: partial",
                "ci_cd_maturity: partial",
                "ai_adoption_posture: cautious",
                "strategy_depth: standard",
                "nfr_priorities:",
                "  - performance",
                "  - security",
                "  - compliance",
            ]),
            encoding="utf-8",
        )

        package = load_input(input_file)

        self.assertEqual(package.normalized["nfr_priorities"], ["performance", "security", "compliance"])

    def test_load_input_normalizes_nfr_priorities_from_string_to_list(self) -> None:
        input_file = self.make_workspace_file()
        input_file.write_text(
            "\n".join([
                "engagement_name: NFR Test",
                "project_posture: brownfield",
                "system_type: API",
                "existing_automation_state: partial",
                "ci_cd_maturity: partial",
                "ai_adoption_posture: cautious",
                "strategy_depth: standard",
                "nfr_priorities: performance",
            ]),
            encoding="utf-8",
        )

        package = load_input(input_file)

        self.assertEqual(package.normalized["nfr_priorities"], ["performance"])

    def test_load_input_nfr_priorities_absent_normalizes_to_empty_list(self) -> None:
        input_file = self.make_workspace_file()
        input_file.write_text(
            "\n".join([
                "engagement_name: No NFR",
                "project_posture: brownfield",
                "system_type: API",
                "existing_automation_state: partial",
                "ci_cd_maturity: partial",
                "ai_adoption_posture: cautious",
                "strategy_depth: standard",
            ]),
            encoding="utf-8",
        )

        package = load_input(input_file)

        self.assertEqual(package.normalized["nfr_priorities"], [])

if __name__ == "__main__":
    unittest.main()
