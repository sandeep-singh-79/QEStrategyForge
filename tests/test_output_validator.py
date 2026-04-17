from __future__ import annotations

import unittest


class OutputValidatorTests(unittest.TestCase):
    def test_validate_output_passes_for_complete_structure(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output

        markdown = "\n".join(
            [
                "## Executive Summary",
                "Strategy Confidence: standard",
                "## Engagement Context",
                "Project Posture: brownfield",
                "Delivery Model: Agile",
                "System Type: API-first",
                "## Quality Objectives And Risk Priorities",
                "## Lifecycle Posture",
                "Shift-Left Stance: moderate",
                "## Layered Test Strategy",
                "Layering Priority: balanced",
                "## Test Types And Coverage Focus",
                "Non-Functional Priorities: performance, security",
                "## Automation Strategy",
                "Current Automation State: partial",
                "Target Automation State: phased expansion",
                "Automation Adoption Path: phased_expansion",
                "## CI/CD And Quality Gates",
                "Current CI/CD Maturity: partial",
                "Target CI/CD Posture: progressive_gates",
                "## Test Data Strategy",
                "## Environment Strategy",
                "## Defect, Triage, And Reporting Model",
                "Governance Depth: medium",
                "Reporting Emphasis: medium",
                "Reporting Audience: engineering",
                "## AI Usage Model",
                "AI Adoption Posture: cautious",
                "Human Review Boundaries: QE lead review required",
                "## Assumptions, Gaps, And Open Questions",
                "Missing Information: architecture details",
                "Assumption Mode: normal",
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
                "Shift-Left Stance: moderate",
                "## Layered Test Strategy",
                "Layering Priority: balanced",
                "## Test Types And Coverage Focus",
                "## Automation Strategy",
                "Current Automation State: partial",
                "Automation Adoption Path: phased_expansion",
                "## CI/CD And Quality Gates",
                "Current CI/CD Maturity: partial",
                "Target CI/CD Posture: progressive_gates",
                "## Test Data Strategy",
                "## Environment Strategy",
                "## Defect, Triage, And Reporting Model",
                "Governance Depth: medium",
                "Reporting Emphasis: medium",
                "## AI Usage Model",
                "AI Adoption Posture: cautious",
                "Human Review Boundaries: QE lead review required",
                "## Assumptions, Gaps, And Open Questions",
                "Missing Information: architecture details",
                "Assumption Mode: normal",
                "Strategy Confidence: standard",
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
                "Shift-Left Stance: moderate",
                "## Layered Test Strategy",
                "Layering Priority: balanced",
                "## Test Types And Coverage Focus",
                "## Automation Strategy",
                "Current Automation State: partial",
                "Target Automation State: phased expansion",
                "Automation Adoption Path: phased_expansion",
                "## CI/CD And Quality Gates",
                "Current CI/CD Maturity: partial",
                "Target CI/CD Posture: progressive_gates",
                "## Test Data Strategy",
                "## Environment Strategy",
                "## Defect, Triage, And Reporting Model",
                "Governance Depth: medium",
                "Reporting Emphasis: medium",
                "## AI Usage Model",
                "AI Adoption Posture: cautious",
                "Human Review Boundaries: QE lead review required",
                "## Assumptions, Gaps, And Open Questions",
                "Assumption Mode: normal",
                "Strategy Confidence: standard",
                "## Recommended Next Steps",
                "Recommended Immediate Actions: validate current-state evidence",
            ]
        )

        result = validate_output(markdown)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("Missing Information:" in error for error in result.errors))

    # ------------------------------------------------------------------
    # Phase 11B4 — Non-Functional Priorities label validation
    # ------------------------------------------------------------------

    def test_validate_output_passes_with_non_functional_priorities_label(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output, REQUIRED_LABELS

        self.assertIn("Non-Functional Priorities:", REQUIRED_LABELS)
        # A complete document (with the label) should be valid
        markdown = "\n".join([
            "## Executive Summary",
            "Strategy Confidence: standard",
            "## Engagement Context",
            "Project Posture: brownfield",
            "Delivery Model: Agile",
            "System Type: API",
            "## Quality Objectives And Risk Priorities",
            "## Lifecycle Posture",
            "Shift-Left Stance: moderate",
            "## Layered Test Strategy",
            "Layering Priority: balanced",
            "## Test Types And Coverage Focus",
            "Non-Functional Priorities: performance, security",
            "## Automation Strategy",
            "Current Automation State: partial",
            "Target Automation State: phased expansion",
            "Automation Adoption Path: phased_expansion",
            "## CI/CD And Quality Gates",
            "Current CI/CD Maturity: partial",
            "Target CI/CD Posture: progressive_gates",
            "## Test Data Strategy",
            "## Environment Strategy",
            "## Defect, Triage, And Reporting Model",
            "Governance Depth: medium",
            "Reporting Emphasis: medium",
            "Reporting Audience: mixed",
            "## AI Usage Model",
            "AI Adoption Posture: cautious",
            "Human Review Boundaries: review required",
            "## Assumptions, Gaps, And Open Questions",
            "Missing Information: none",
            "Assumption Mode: normal",
            "## Recommended Next Steps",
            "Recommended Immediate Actions: begin testing",
        ])

        result = validate_output(markdown)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_validate_output_fails_when_non_functional_priorities_label_missing(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output

        markdown = "\n".join([
            "## Executive Summary",
            "## Engagement Context",
            "Project Posture: brownfield",
            "Delivery Model: Agile",
            "System Type: API",
            "## Quality Objectives And Risk Priorities",
            "## Lifecycle Posture",
            "Shift-Left Stance: moderate",
            "## Layered Test Strategy",
            "Layering Priority: balanced",
            "## Test Types And Coverage Focus",
            # Non-Functional Priorities: label intentionally omitted
            "Functional Coverage: critical flows",
            "## Automation Strategy",
            "Current Automation State: partial",
            "Target Automation State: phased expansion",
            "Automation Adoption Path: phased_expansion",
            "## CI/CD And Quality Gates",
            "Current CI/CD Maturity: partial",
            "Target CI/CD Posture: progressive_gates",
            "## Test Data Strategy",
            "## Environment Strategy",
            "## Defect, Triage, And Reporting Model",
            "Governance Depth: medium",
            "Reporting Emphasis: medium",
            "## AI Usage Model",
            "AI Adoption Posture: cautious",
            "Human Review Boundaries: review required",
            "## Assumptions, Gaps, And Open Questions",
            "Missing Information: none",
            "Assumption Mode: normal",
            "Strategy Confidence: standard",
            "## Recommended Next Steps",
            "Recommended Immediate Actions: begin testing",
        ])

        result = validate_output(markdown)

        self.assertFalse(result.is_valid)
        self.assertTrue(any("Non-Functional Priorities:" in e for e in result.errors))


class SectionAwareValidatorTests(unittest.TestCase):
    """P12-E: section-aware validation — labels must appear in the correct section."""

    _COMPLETE = "\n".join([
        "## Executive Summary",
        "Strategy Confidence: standard",
        "## Engagement Context",
        "Project Posture: brownfield",
        "Delivery Model: Agile",
        "System Type: API",
        "## Quality Objectives And Risk Priorities",
        "## Lifecycle Posture",
        "Shift-Left Stance: moderate",
        "## Layered Test Strategy",
        "Layering Priority: balanced",
        "## Test Types And Coverage Focus",
        "Non-Functional Priorities: performance",
        "## Automation Strategy",
        "Current Automation State: partial",
        "Target Automation State: phased expansion",
        "Automation Adoption Path: phased_expansion",
        "## CI/CD And Quality Gates",
        "Current CI/CD Maturity: partial",
        "Target CI/CD Posture: progressive_gates",
        "## Test Data Strategy",
        "## Environment Strategy",
        "## Defect, Triage, And Reporting Model",
        "Reporting Emphasis: medium",
        "Reporting Audience: engineering",
        "Governance Depth: medium",
        "## AI Usage Model",
        "AI Adoption Posture: cautious",
        "Human Review Boundaries: QE review",
        "## Assumptions, Gaps, And Open Questions",
        "Missing Information: none",
        "Assumption Mode: normal",
        "## Recommended Next Steps",
        "Recommended Immediate Actions: validate baseline",
    ])

    def test_complete_document_is_valid(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output

        result = validate_output(self._COMPLETE)
        self.assertTrue(result.is_valid, result.errors)

    def test_label_in_wrong_section_produces_error(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output

        # Strategy Confidence in Assumptions instead of Executive Summary
        bad = self._COMPLETE.replace(
            "## Executive Summary\nStrategy Confidence: standard",
            "## Executive Summary",
        ).replace(
            "Missing Information: none\nAssumption Mode: normal",
            "Missing Information: none\nAssumption Mode: normal\nStrategy Confidence: standard",
        )
        result = validate_output(bad)
        self.assertFalse(result.is_valid)
        self.assertTrue(
            any("Strategy Confidence" in e and "Executive Summary" in e for e in result.errors),
            msg=f"Expected section-placement error for Strategy Confidence. Errors: {result.errors}",
        )

    def test_duplicate_label_produces_error(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output

        # Repeat Governance Depth in two sections
        duplicate = self._COMPLETE + "\n## Appendix\nGovernance Depth: high"
        result = validate_output(duplicate)
        self.assertFalse(result.is_valid)
        self.assertTrue(
            any("Duplicate" in e and "Governance Depth" in e for e in result.errors),
            msg=f"Expected duplicate label error. Errors: {result.errors}",
        )

    def test_section_map_covers_all_required_labels(self) -> None:
        from ai_test_strategy_generator.output_validator import REQUIRED_LABELS, LABEL_SECTION_MAP

        # Every required label should be tracked for section placement
        for label in REQUIRED_LABELS:
            self.assertIn(
                label,
                LABEL_SECTION_MAP,
                msg=f"Required label '{label}' is missing from LABEL_SECTION_MAP",
            )


if __name__ == "__main__":
    unittest.main()
