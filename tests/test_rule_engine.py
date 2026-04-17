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

    def test_strong_automation_with_manual_cicd_still_stages_enablement(self) -> None:
        """Strong automation maturity but manual CI/CD should not jump to pipeline_native."""
        from ai_test_strategy_generator.rule_engine import apply_rules

        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "strong",
            "ci_cd_maturity": "manual",
            "system_profile": "api_first",
            "regulatory_sensitivity": "low",
            "information_completeness": "sufficient",
        }

        result = apply_rules(classifications)

        self.assertEqual(result["automation_adoption_path"], "optimize_and_govern")
        # CI/CD maturity is manual → must NOT be pipeline_native regardless of automation
        self.assertEqual(result["ci_cd_posture"], "staged_enablement")
        self.assertEqual(result["reporting_emphasis"], "high")

    def test_greenfield_incomplete_context_combines_both_override_sets(self) -> None:
        """Greenfield posture + incomplete information should apply both rule sets."""
        from ai_test_strategy_generator.rule_engine import apply_rules

        classifications = {
            "project_posture": "greenfield",
            "automation_maturity": "none",
            "ci_cd_maturity": "manual",
            "system_profile": "api_first",
            "regulatory_sensitivity": "low",
            "information_completeness": "incomplete",
        }

        result = apply_rules(classifications)

        # Greenfield rules applied
        self.assertEqual(result["shift_left_stance"], "strong")
        self.assertEqual(result["layering_priority"], "lower_layers_first")
        self.assertEqual(result["brownfield_transition_strategy"], "not_applicable")
        # Incomplete context rules applied
        self.assertEqual(result["assumption_mode"], "explicit")
        self.assertEqual(result["strategy_confidence"], "conditional")

    def test_brownfield_high_regulatory_sensitivity_raises_governance(self) -> None:
        """Brownfield with high regulatory sensitivity should set governance_depth=high."""
        from ai_test_strategy_generator.rule_engine import apply_rules

        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "limited",
            "ci_cd_maturity": "partial",
            "system_profile": "api_first",
            "regulatory_sensitivity": "high",
            "information_completeness": "partial",
        }

        result = apply_rules(classifications)

        self.assertEqual(result["governance_depth"], "high")
        self.assertEqual(result["brownfield_transition_strategy"], "assess_reuse_stabilize_retire_replace")
        self.assertEqual(result["automation_adoption_path"], "phased_expansion")

    def test_all_unknown_classifications_produce_safe_defaults(self) -> None:
        """When every classification value is unknown, rules must not raise and defaults hold."""
        from ai_test_strategy_generator.rule_engine import apply_rules

        classifications = {
            "project_posture": "unknown",
            "automation_maturity": "unknown",
            "ci_cd_maturity": "unknown",
            "system_profile": "unknown",
            "regulatory_sensitivity": "unknown",
            "information_completeness": "unknown",
        }

        result = apply_rules(classifications)

        # Should return a complete dict without raising
        self.assertIn("shift_left_stance", result)
        self.assertIn("automation_adoption_path", result)
        self.assertIn("ci_cd_posture", result)
        self.assertIn("governance_depth", result)
        self.assertIn("assumption_mode", result)
        self.assertIn("strategy_confidence", result)

    def test_missing_classification_keys_produce_safe_defaults(self) -> None:
        """apply_rules must not raise when classification keys are absent."""
        from ai_test_strategy_generator.rule_engine import apply_rules

        result = apply_rules({})

        self.assertIn("shift_left_stance", result)
        self.assertIn("brownfield_transition_strategy", result)
        self.assertEqual(result["brownfield_transition_strategy"], "not_applicable")

    # ------------------------------------------------------------------
    # Phase 11B3 — nfr_depth decision (Rule SA-2)
    # ------------------------------------------------------------------

    def test_high_nfr_priority_produces_deep_nfr_depth(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules

        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "partial",
            "ci_cd_maturity": "partial",
            "system_profile": "api_first",
            "regulatory_sensitivity": "high",
            "information_completeness": "sufficient",
            "nfr_priority": "high",
        }

        result = apply_rules(classifications)

        self.assertEqual(result["nfr_depth"], "deep")

    def test_standard_nfr_priority_produces_standard_nfr_depth(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules

        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "partial",
            "ci_cd_maturity": "partial",
            "system_profile": "api_first",
            "regulatory_sensitivity": "low",
            "information_completeness": "sufficient",
            "nfr_priority": "standard",
        }

        result = apply_rules(classifications)

        self.assertEqual(result["nfr_depth"], "standard")

    def test_missing_nfr_priority_defaults_to_standard_nfr_depth(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules

        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "partial",
            "ci_cd_maturity": "partial",
            "system_profile": "api_first",
            "regulatory_sensitivity": "low",
            "information_completeness": "sufficient",
            # nfr_priority deliberately absent
        }

        result = apply_rules(classifications)

        self.assertEqual(result["nfr_depth"], "standard")

    def test_all_unknown_classifications_includes_nfr_depth(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules

        result = apply_rules({})

        self.assertIn("nfr_depth", result)
        self.assertEqual(result["nfr_depth"], "standard")

    def test_decision_keys_total_includes_nfr_depth(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules

        result = apply_rules({
            "project_posture": "brownfield",
            "automation_maturity": "partial",
            "ci_cd_maturity": "partial",
            "system_profile": "api_first",
            "regulatory_sensitivity": "low",
            "information_completeness": "sufficient",
            "nfr_priority": "standard",
        })

        self.assertEqual(len(result), 10)


if __name__ == "__main__":
    unittest.main()
