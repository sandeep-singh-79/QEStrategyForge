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

    # ------------------------------------------------------------------
    # P12-B — optional enum field validation
    # ------------------------------------------------------------------

    def _valid_base(self) -> dict:
        return {
            "engagement_name": "Example",
            "project_posture": "brownfield",
            "system_type": "API",
            "existing_automation_state": "partial",
            "ci_cd_maturity": "partial",
            "ai_adoption_posture": "cautious",
            "strategy_depth": "standard",
            "business_goal": "Improve quality",
            "known_constraints": ["time pressure"],
        }

    def test_optional_enum_valid_release_cadence_passes(self) -> None:
        data = {**self._valid_base(), "release_cadence": "continuous"}
        result = validate_input(InputPackage(source_path=Path("x.yaml"), raw={}, normalized=data))
        self.assertTrue(result.is_valid)

    def test_optional_enum_invalid_release_cadence_fails(self) -> None:
        data = {**self._valid_base(), "release_cadence": "daily"}
        result = validate_input(InputPackage(source_path=Path("x.yaml"), raw={}, normalized=data))
        self.assertFalse(result.is_valid)
        self.assertTrue(any("release_cadence" in e for e in result.errors))

    def test_optional_enum_absent_release_cadence_passes(self) -> None:
        """Absent optional field must not trigger a validation error."""
        result = validate_input(InputPackage(source_path=Path("x.yaml"), raw={}, normalized=self._valid_base()))
        self.assertTrue(result.is_valid)

    def test_optional_enum_valid_qe_capacity_passes(self) -> None:
        data = {**self._valid_base(), "qe_capacity": "small"}
        result = validate_input(InputPackage(source_path=Path("x.yaml"), raw={}, normalized=data))
        self.assertTrue(result.is_valid)

    def test_optional_enum_invalid_qe_capacity_fails(self) -> None:
        data = {**self._valid_base(), "qe_capacity": "micro"}
        result = validate_input(InputPackage(source_path=Path("x.yaml"), raw={}, normalized=data))
        self.assertFalse(result.is_valid)
        self.assertTrue(any("qe_capacity" in e for e in result.errors))

    def test_optional_enum_valid_reporting_audience_passes(self) -> None:
        data = {**self._valid_base(), "reporting_audience": "executive"}
        result = validate_input(InputPackage(source_path=Path("x.yaml"), raw={}, normalized=data))
        self.assertTrue(result.is_valid)

    def test_optional_enum_invalid_reporting_audience_fails(self) -> None:
        data = {**self._valid_base(), "reporting_audience": "board"}
        result = validate_input(InputPackage(source_path=Path("x.yaml"), raw={}, normalized=data))
        self.assertFalse(result.is_valid)
        self.assertTrue(any("reporting_audience" in e for e in result.errors))

    def test_new_list_fields_normalized_to_empty_lists_when_absent(self) -> None:
        from ai_test_strategy_generator.input_loader import load_input
        import tempfile, textwrap
        yaml_text = textwrap.dedent("""
            engagement_name: Test
            project_posture: greenfield
            system_type: API
            existing_automation_state: none
            ci_cd_maturity: manual
            ai_adoption_posture: supportive
            strategy_depth: standard
            business_goal: Launch safely
            known_constraints:
              - small team
        """)
        tmp = _TESTS_TMP / "loader_test.yaml"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(yaml_text, encoding="utf-8")
        pkg = load_input(tmp)
        self.assertEqual(pkg.normalized.get("environment_constraints"), [])
        self.assertEqual(pkg.normalized.get("data_privacy_constraints"), [])
        self.assertEqual(pkg.normalized.get("target_quality_gates"), [])
        tmp.unlink()


_TESTS_TMP = Path(__file__).parent / ".tmp"


if __name__ == "__main__":
    unittest.main()
