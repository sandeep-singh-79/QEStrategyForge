from __future__ import annotations

import unittest


class RuleEngineTests(unittest.TestCase):
    def test_greenfield_rules_push_shift_left_and_foundational_automation(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules

        classifications = {
            "project_posture": "greenfield",
            "automation_maturity": "none",
            "ci_cd_maturity": "manual",
            "system_profile": "api_first",
            "regulatory_sensitivity": "low",
            "information_completeness": "partial",
        }

        result = apply_rules(classifications)

        self.assertEqual(result["shift_left_stance"], "strong")
        self.assertEqual(result["layering_priority"], "lower_layers_first")
        self.assertEqual(result["automation_adoption_path"], "foundation_first")
        self.assertEqual(result["ci_cd_posture"], "staged_enablement")

    def test_brownfield_partial_rules_emphasize_transition_and_phased_growth(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules

        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "partial",
            "ci_cd_maturity": "partial",
            "system_profile": "legacy",
            "regulatory_sensitivity": "high",
            "information_completeness": "partial",
        }

        result = apply_rules(classifications)

        self.assertEqual(result["brownfield_transition_strategy"], "assess_reuse_stabilize_retire_replace")
        self.assertEqual(result["automation_adoption_path"], "phased_expansion")
        self.assertEqual(result["governance_depth"], "high")
        self.assertEqual(result["layering_priority"], "stabilize_lower_layers_then_ui")

    def test_strong_automation_rules_shift_to_optimization(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules

        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "strong",
            "ci_cd_maturity": "mature",
            "system_profile": "ui_heavy",
            "regulatory_sensitivity": "low",
            "information_completeness": "sufficient",
        }

        result = apply_rules(classifications)

        self.assertEqual(result["automation_adoption_path"], "optimize_and_govern")
        self.assertEqual(result["reporting_emphasis"], "high")
        self.assertEqual(result["ci_cd_posture"], "pipeline_native")

    def test_incomplete_context_rules_force_explicit_assumptions(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules

        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "unknown",
            "ci_cd_maturity": "unknown",
            "system_profile": "general",
            "regulatory_sensitivity": "medium",
            "information_completeness": "incomplete",
        }

        result = apply_rules(classifications)

        self.assertEqual(result["assumption_mode"], "explicit")
        self.assertEqual(result["strategy_confidence"], "conditional")


if __name__ == "__main__":
    unittest.main()
