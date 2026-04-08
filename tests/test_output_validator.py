from __future__ import annotations

import unittest


class OutputValidatorTests(unittest.TestCase):
    def test_validate_output_passes_for_complete_structure(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output

        markdown = "\n".join(
            [
                "## Executive Summary",
                "## Engagement Context",
                "Project Posture: brownfield",
                "Delivery Model: Agile",
                "System Type: API-first",
                "## Quality Objectives And Risk Priorities",
                "## Lifecycle Posture",
                "## Layered Test Strategy",
                "## Test Types And Coverage Focus",
                "## Automation Strategy",
                "Current Automation State: partial",
                "Target Automation State: phased expansion",
                "## CI/CD And Quality Gates",
                "Current CI/CD Maturity: partial",
                "Target CI/CD Posture: progressive_gates",
                "## Test Data Strategy",
                "## Environment Strategy",
                "## Defect, Triage, And Reporting Model",
                "## AI Usage Model",
                "AI Adoption Posture: cautious",
                "Human Review Boundaries: QE lead review required",
                "## Assumptions, Gaps, And Open Questions",
                "Missing Information: architecture details",
                "## Recommended Next Steps",
                "Recommended Immediate Actions: validate current-state evidence",
            ]
        )

        result = validate_output(markdown)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_validate_output_fails_when_heading_missing(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output

        markdown = "## Executive Summary\nProject Posture: brownfield\n"

        result = validate_output(markdown)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("Missing required heading" in error for error in result.errors))

    def test_validate_output_fails_when_label_missing(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output

        markdown = "\n".join(
            [
                "## Executive Summary",
                "## Engagement Context",
                "Project Posture: brownfield",
                "Delivery Model: Agile",
                "System Type: API-first",
                "## Quality Objectives And Risk Priorities",
                "## Lifecycle Posture",
                "## Layered Test Strategy",
                "## Test Types And Coverage Focus",
                "## Automation Strategy",
                "Current Automation State: partial",
                "## CI/CD And Quality Gates",
                "Current CI/CD Maturity: partial",
                "Target CI/CD Posture: progressive_gates",
                "## Test Data Strategy",
                "## Environment Strategy",
                "## Defect, Triage, And Reporting Model",
                "## AI Usage Model",
                "AI Adoption Posture: cautious",
                "Human Review Boundaries: QE lead review required",
                "## Assumptions, Gaps, And Open Questions",
                "Missing Information: architecture details",
                "## Recommended Next Steps",
                "Recommended Immediate Actions: validate current-state evidence",
            ]
        )

        result = validate_output(markdown)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("Target Automation State:" in error for error in result.errors))

    def test_validate_output_flags_missing_information_when_expected(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output

        markdown = "\n".join(
            [
                "## Executive Summary",
                "## Engagement Context",
                "Project Posture: brownfield",
                "Delivery Model: Agile",
                "System Type: API-first",
                "## Quality Objectives And Risk Priorities",
                "## Lifecycle Posture",
                "## Layered Test Strategy",
                "## Test Types And Coverage Focus",
                "## Automation Strategy",
                "Current Automation State: partial",
                "Target Automation State: phased expansion",
                "## CI/CD And Quality Gates",
                "Current CI/CD Maturity: partial",
                "Target CI/CD Posture: progressive_gates",
                "## Test Data Strategy",
                "## Environment Strategy",
                "## Defect, Triage, And Reporting Model",
                "## AI Usage Model",
                "AI Adoption Posture: cautious",
                "Human Review Boundaries: QE lead review required",
                "## Assumptions, Gaps, And Open Questions",
                "## Recommended Next Steps",
                "Recommended Immediate Actions: validate current-state evidence",
            ]
        )

        result = validate_output(markdown)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("Missing Information:" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
