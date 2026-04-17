from __future__ import annotations

import unittest
from pathlib import Path

from ai_test_strategy_generator.models import InputPackage


class ContextClassifierTests(unittest.TestCase):
    def make_package(self, **overrides: object) -> InputPackage:
        normalized = {
            "engagement_name": "Example",
            "project_posture": "brownfield",
            "system_type": "API-first microservices",
            "domain": "Insurance",
            "existing_automation_state": "partial",
            "ci_cd_maturity": "partial",
            "environment_maturity": "moderate",
            "test_data_maturity": "weak",
            "ai_adoption_posture": "cautious",
            "strategy_depth": "standard",
            "business_goal": "Improve quality",
            "known_constraints": ["limited QE capacity"],
            "delivery_risks": ["integration instability"],
            "missing_information": ["test inventory"],
            "regulatory_or_compliance_needs": ["auditability"],
        }
        normalized.update(overrides)
        return InputPackage(source_path=Path("input.yaml"), raw={}, normalized=normalized)

    def test_classify_context_identifies_regulated_context(self) -> None:
        from ai_test_strategy_generator.context_classifier import classify_context

        result = classify_context(self.make_package())

        self.assertEqual(result["project_posture"], "brownfield")
        self.assertEqual(result["automation_maturity"], "partial")
        self.assertEqual(result["ci_cd_maturity"], "partial")
        self.assertEqual(result["system_profile"], "api_first")
        self.assertEqual(result["regulatory_sensitivity"], "high")
        self.assertEqual(result["information_completeness"], "partial")

    def test_classify_context_identifies_greenfield_low_regulation(self) -> None:
        from ai_test_strategy_generator.context_classifier import classify_context

        result = classify_context(
            self.make_package(
                project_posture="greenfield",
                domain="Generic SaaS",
                regulatory_or_compliance_needs=[],
                missing_information=[],
                system_type="UI-heavy product",
                existing_automation_state="none",
                ci_cd_maturity="manual",
            )
        )

        self.assertEqual(result["project_posture"], "greenfield")
        self.assertEqual(result["system_profile"], "ui_heavy")
        self.assertEqual(result["regulatory_sensitivity"], "low")
        self.assertEqual(result["information_completeness"], "sufficient")

    def test_classify_context_marks_unknown_domain_as_medium_regulatory_if_controls_exist(self) -> None:
        from ai_test_strategy_generator.context_classifier import classify_context

        result = classify_context(
            self.make_package(
                domain="Unknown",
                regulatory_or_compliance_needs=["privacy-sensitive test data handling"],
            )
        )

        self.assertEqual(result["regulatory_sensitivity"], "medium")

    def test_classify_context_marks_legacy_system(self) -> None:
        from ai_test_strategy_generator.context_classifier import classify_context

        result = classify_context(self.make_package(system_type="legacy enterprise"))

        self.assertEqual(result["system_profile"], "legacy")

    def test_classify_context_marks_incomplete_when_many_unknowns_exist(self) -> None:
        from ai_test_strategy_generator.context_classifier import classify_context

        result = classify_context(
            self.make_package(
                existing_automation_state="unknown",
                ci_cd_maturity="unknown",
                environment_maturity="unknown",
                test_data_maturity="unknown",
                missing_information=["architecture", "ci/cd", "automation", "test inventory"],
            )
        )

        self.assertEqual(result["information_completeness"], "incomplete")

    # ------------------------------------------------------------------
    # Phase 11B2 — nfr_priority classification
    # ------------------------------------------------------------------

    def test_classify_context_returns_high_nfr_priority_for_three_priorities(self) -> None:
        from ai_test_strategy_generator.context_classifier import classify_context

        result = classify_context(
            self.make_package(nfr_priorities=["performance", "security", "compliance"])
        )

        self.assertEqual(result["nfr_priority"], "high")

    def test_classify_context_returns_high_nfr_priority_for_two_priorities(self) -> None:
        from ai_test_strategy_generator.context_classifier import classify_context

        result = classify_context(
            self.make_package(nfr_priorities=["performance", "security"])
        )

        self.assertEqual(result["nfr_priority"], "high")

    def test_classify_context_returns_standard_nfr_priority_for_zero_priorities(self) -> None:
        from ai_test_strategy_generator.context_classifier import classify_context

        result = classify_context(self.make_package(nfr_priorities=[]))

        self.assertEqual(result["nfr_priority"], "standard")

    def test_classify_context_returns_standard_nfr_priority_for_one_priority(self) -> None:
        from ai_test_strategy_generator.context_classifier import classify_context

        result = classify_context(self.make_package(nfr_priorities=["performance"]))

        self.assertEqual(result["nfr_priority"], "standard")

    def test_classify_context_returns_standard_nfr_priority_when_field_absent(self) -> None:
        from ai_test_strategy_generator.context_classifier import classify_context

        package = self.make_package()
        # Remove nfr_priorities entirely from normalized data
        package.normalized.pop("nfr_priorities", None)

        result = classify_context(package)

        self.assertEqual(result["nfr_priority"], "standard")


if __name__ == "__main__":
    unittest.main()
