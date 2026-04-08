from __future__ import annotations

import unittest
from pathlib import Path

from ai_test_strategy_generator.models import InputPackage


class RendererTests(unittest.TestCase):
    def make_package(self, **overrides: object) -> InputPackage:
        normalized = {
            "engagement_name": "Claims Modernization QE Strategy",
            "domain": "Insurance",
            "delivery_model": "Agile",
            "project_posture": "brownfield",
            "timeline_pressure": "high",
            "business_goal": "Modernize claims processing without increasing regression risk",
            "quality_goal": "Improve release confidence and reduce leakage",
            "release_expectation": "Bi-weekly release readiness with quality gates",
            "critical_business_flows": ["claim creation", "claim adjudication"],
            "system_type": "API-first with supporting UI",
            "applications_in_scope": ["claims portal", "claims service layer"],
            "key_integrations": ["policy platform", "payment gateway"],
            "platform_notes": "Legacy UI still exists around a partly modernized service layer",
            "existing_test_process": "Manual-heavy with some automation support",
            "existing_automation_state": "partial",
            "ci_cd_maturity": "partial",
            "environment_maturity": "moderate",
            "test_data_maturity": "weak",
            "known_constraints": ["incomplete documentation", "limited QE capacity"],
            "regulatory_or_compliance_needs": ["auditability", "privacy-sensitive test data handling"],
            "delivery_risks": ["integration instability", "weak regression confidence"],
            "missing_information": ["production defect leakage trend", "full API coverage baseline"],
            "requirements_available": "yes - feature summaries available",
            "api_docs_available": "yes - partial OpenAPI coverage",
            "existing_test_cases_available": "yes - manual regression pack available",
            "automation_assets_available": "yes - partial API and UI automation exists",
            "production_or_operational_feedback_available": "no - not yet collected",
            "ai_adoption_posture": "cautious",
            "ai_governance_constraints": ["human approval required for final strategy sign-off"],
            "human_review_expectations": ["QE lead review required for all AI-generated strategy sections"],
            "strategy_depth": "standard",
            "primary_audience": "QE lead and delivery leadership",
            "desired_output_format": "markdown",
        }
        normalized.update(overrides)
        return InputPackage(source_path=Path("input.yaml"), raw={}, normalized=normalized)

    def test_render_strategy_contains_required_headings_and_labels(self) -> None:
        from ai_test_strategy_generator.renderer import render_strategy

        package = self.make_package()
        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "partial",
            "ci_cd_maturity": "partial",
            "system_profile": "api_first",
            "regulatory_sensitivity": "high",
            "information_completeness": "partial",
        }
        decisions = {
            "shift_left_stance": "moderate",
            "layering_priority": "api_and_integration_first",
            "brownfield_transition_strategy": "assess_reuse_stabilize_retire_replace",
            "automation_adoption_path": "phased_expansion",
            "ci_cd_posture": "progressive_gates",
            "governance_depth": "high",
            "reporting_emphasis": "medium",
            "assumption_mode": "explicit",
            "strategy_confidence": "standard",
        }

        output = render_strategy(package, classifications, decisions)

        required_headings = [
            "## Executive Summary",
            "## Engagement Context",
            "## Quality Objectives And Risk Priorities",
            "## Lifecycle Posture",
            "## Layered Test Strategy",
            "## Test Types And Coverage Focus",
            "## Automation Strategy",
            "## CI/CD And Quality Gates",
            "## Test Data Strategy",
            "## Environment Strategy",
            "## Defect, Triage, And Reporting Model",
            "## AI Usage Model",
            "## Assumptions, Gaps, And Open Questions",
            "## Recommended Next Steps",
        ]
        required_labels = [
            "Project Posture:",
            "Delivery Model:",
            "System Type:",
            "Current Automation State:",
            "Target Automation State:",
            "Current CI/CD Maturity:",
            "Target CI/CD Posture:",
            "AI Adoption Posture:",
            "Human Review Boundaries:",
            "Missing Information:",
            "Recommended Immediate Actions:",
        ]

        for heading in required_headings:
            self.assertIn(heading, output)
        for label in required_labels:
            self.assertIn(label, output)

    def test_build_strategy_document_returns_structured_sections(self) -> None:
        from ai_test_strategy_generator.renderer import build_strategy_document

        package = self.make_package()
        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "partial",
            "ci_cd_maturity": "partial",
            "system_profile": "api_first",
            "regulatory_sensitivity": "high",
            "information_completeness": "partial",
        }
        decisions = {
            "shift_left_stance": "moderate",
            "layering_priority": "api_and_integration_first",
            "brownfield_transition_strategy": "assess_reuse_stabilize_retire_replace",
            "automation_adoption_path": "phased_expansion",
            "ci_cd_posture": "progressive_gates",
            "governance_depth": "high",
            "reporting_emphasis": "medium",
            "assumption_mode": "explicit",
            "strategy_confidence": "standard",
        }

        document = build_strategy_document(package, classifications, decisions)

        self.assertEqual(document.sections[0].heading, "## Executive Summary")
        self.assertEqual(document.sections[-1].heading, "## Recommended Next Steps")
        self.assertTrue(any(line.startswith("Project Posture:") for line in document.sections[1].lines))

    def test_render_strategy_reflects_rule_outputs(self) -> None:
        from ai_test_strategy_generator.renderer import render_strategy

        package = self.make_package(project_posture="greenfield", existing_automation_state="none", ci_cd_maturity="manual")
        classifications = {
            "project_posture": "greenfield",
            "automation_maturity": "none",
            "ci_cd_maturity": "manual",
            "system_profile": "api_first",
            "regulatory_sensitivity": "low",
            "information_completeness": "partial",
        }
        decisions = {
            "shift_left_stance": "strong",
            "layering_priority": "lower_layers_first",
            "brownfield_transition_strategy": "not_applicable",
            "automation_adoption_path": "foundation_first",
            "ci_cd_posture": "staged_enablement",
            "governance_depth": "light",
            "reporting_emphasis": "medium",
            "assumption_mode": "explicit",
            "strategy_confidence": "standard",
        }

        output = render_strategy(package, classifications, decisions)

        self.assertIn("Project Posture: greenfield", output)
        self.assertIn("Shift-Left Stance: strong", output)
        self.assertIn("Layering Priority: lower_layers_first", output)
        self.assertIn("Automation Adoption Path: foundation_first", output)
        self.assertIn("Target CI/CD Posture: staged_enablement", output)
        self.assertNotIn("Brownfield Transition Strategy:", output)

    def test_render_strategy_uses_brownfield_line_only_when_applicable(self) -> None:
        from ai_test_strategy_generator.renderer import render_strategy

        package = self.make_package(existing_automation_state="strong", ci_cd_maturity="mature")
        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "strong",
            "ci_cd_maturity": "mature",
            "system_profile": "ui_heavy",
            "regulatory_sensitivity": "low",
            "information_completeness": "partial",
        }
        decisions = {
            "shift_left_stance": "moderate",
            "layering_priority": "balanced",
            "brownfield_transition_strategy": "assess_reuse_stabilize_retire_replace",
            "automation_adoption_path": "optimize_and_govern",
            "ci_cd_posture": "pipeline_native",
            "governance_depth": "light",
            "reporting_emphasis": "high",
            "assumption_mode": "explicit",
            "strategy_confidence": "standard",
        }

        output = render_strategy(package, classifications, decisions)

        self.assertIn(
            "Brownfield Transition Strategy: assess_reuse_stabilize_retire_replace",
            output,
        )

    def test_render_strategy_includes_quality_gate_release_and_reporting_language(self) -> None:
        from ai_test_strategy_generator.renderer import render_strategy

        package = self.make_package(existing_automation_state="strong", ci_cd_maturity="mature")
        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "strong",
            "ci_cd_maturity": "mature",
            "system_profile": "ui_heavy",
            "regulatory_sensitivity": "low",
            "information_completeness": "partial",
        }
        decisions = {
            "shift_left_stance": "moderate",
            "layering_priority": "balanced",
            "brownfield_transition_strategy": "assess_reuse_stabilize_retire_replace",
            "automation_adoption_path": "optimize_and_govern",
            "ci_cd_posture": "pipeline_native",
            "governance_depth": "light",
            "reporting_emphasis": "high",
            "assumption_mode": "explicit",
            "strategy_confidence": "standard",
        }

        output = render_strategy(package, classifications, decisions)

        self.assertIn("quality gate", output)
        self.assertIn("release", output)
        self.assertIn("reporting", output)

    def test_render_strategy_surfaces_missing_information_and_open_questions(self) -> None:
        from ai_test_strategy_generator.renderer import render_strategy

        package = self.make_package(
            missing_information=["architecture details", "ci/cd toolchain"],
            ai_adoption_posture="restricted",
            human_review_expectations=["all recommendations provisional until discovery"],
        )
        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "unknown",
            "ci_cd_maturity": "unknown",
            "system_profile": "legacy",
            "regulatory_sensitivity": "high",
            "information_completeness": "incomplete",
        }
        decisions = {
            "shift_left_stance": "moderate",
            "layering_priority": "stabilize_lower_layers_then_ui",
            "brownfield_transition_strategy": "assess_reuse_stabilize_retire_replace",
            "automation_adoption_path": "phased_expansion",
            "ci_cd_posture": "staged_enablement",
            "governance_depth": "high",
            "reporting_emphasis": "medium",
            "assumption_mode": "explicit",
            "strategy_confidence": "conditional",
        }

        output = render_strategy(package, classifications, decisions)

        self.assertIn("Missing Information: architecture details; ci/cd toolchain", output)
        self.assertIn("Strategy Confidence: conditional", output)
        self.assertIn("Open Questions", output)


if __name__ == "__main__":
    unittest.main()
