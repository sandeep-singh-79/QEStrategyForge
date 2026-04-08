from __future__ import annotations

import unittest
from pathlib import Path

from ai_test_strategy_generator.models import InputPackage
from ai_test_strategy_generator.validators.input_validator import validate_input


class InputValidatorTests(unittest.TestCase):
    def test_validate_input_passes_for_valid_minimum_input(self) -> None:
        package = InputPackage(
            source_path=Path("input.yaml"),
            raw={},
            normalized={
                "engagement_name": "Example",
                "project_posture": "greenfield",
                "system_type": "API-first",
                "existing_automation_state": "none",
                "ci_cd_maturity": "manual",
                "environment_maturity": "moderate",
                "test_data_maturity": "moderate",
                "ai_adoption_posture": "supportive",
                "strategy_depth": "standard",
                "business_goal": "Launch safely",
                "quality_goal": "",
                "known_constraints": ["small team"],
                "delivery_risks": [],
            },
        )

        result = validate_input(package)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_validate_input_fails_for_missing_required_fields(self) -> None:
        package = InputPackage(source_path=Path("input.yaml"), raw={}, normalized={})

        result = validate_input(package)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("engagement_name" in error for error in result.errors))
        self.assertTrue(any("project_posture" in error for error in result.errors))

    def test_validate_input_fails_for_invalid_enum_value(self) -> None:
        package = InputPackage(
            source_path=Path("input.yaml"),
            raw={},
            normalized={
                "engagement_name": "Example",
                "project_posture": "sidefield",
                "system_type": "legacy",
                "existing_automation_state": "partial",
                "ci_cd_maturity": "partial",
                "environment_maturity": "moderate",
                "test_data_maturity": "moderate",
                "ai_adoption_posture": "supportive",
                "strategy_depth": "standard",
                "business_goal": "Improve quality",
                "known_constraints": ["time pressure"],
            },
        )

        result = validate_input(package)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("project_posture" in error for error in result.errors))

    def test_validate_input_requires_goal_and_constraint_or_risk(self) -> None:
        package = InputPackage(
            source_path=Path("input.yaml"),
            raw={},
            normalized={
                "engagement_name": "Example",
                "project_posture": "brownfield",
                "system_type": "legacy",
                "existing_automation_state": "partial",
                "ci_cd_maturity": "partial",
                "environment_maturity": "moderate",
                "test_data_maturity": "moderate",
                "ai_adoption_posture": "cautious",
                "strategy_depth": "standard",
                "business_goal": "",
                "quality_goal": "",
                "known_constraints": [],
                "delivery_risks": [],
            },
        )

        result = validate_input(package)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("business_goal" in error or "quality_goal" in error for error in result.errors))
        self.assertTrue(any("known_constraints" in error or "delivery_risks" in error for error in result.errors))

    def test_validate_input_fails_when_enum_field_is_not_string(self) -> None:
        package = InputPackage(
            source_path=Path("input.yaml"),
            raw={},
            normalized={
                "engagement_name": "Example",
                "project_posture": "brownfield",
                "system_type": "legacy",
                "existing_automation_state": ["partial"],
                "ci_cd_maturity": "partial",
                "environment_maturity": "moderate",
                "test_data_maturity": "moderate",
                "ai_adoption_posture": "cautious",
                "strategy_depth": "standard",
                "business_goal": "Improve quality",
                "known_constraints": ["time pressure"],
            },
        )

        result = validate_input(package)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("existing_automation_state" in error for error in result.errors))

    def test_validate_input_treats_blank_strings_as_missing(self) -> None:
        package = InputPackage(
            source_path=Path("input.yaml"),
            raw={},
            normalized={
                "engagement_name": "   ",
                "project_posture": "brownfield",
                "system_type": "legacy",
                "existing_automation_state": "partial",
                "ci_cd_maturity": "partial",
                "environment_maturity": "moderate",
                "test_data_maturity": "moderate",
                "ai_adoption_posture": "cautious",
                "strategy_depth": "standard",
                "business_goal": "Improve quality",
                "known_constraints": ["time pressure"],
            },
        )

        result = validate_input(package)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("engagement_name" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
