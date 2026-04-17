from __future__ import annotations

import unittest
from pathlib import Path

from ai_test_strategy_generator.models import InputPackage
from ai_test_strategy_generator.prompt_builder import _select_scenario


def _make_brownfield_package() -> InputPackage:
    return InputPackage(
        source_path=Path("test.yaml"),
        raw={},
        normalized={
            "project_posture": "brownfield",
            "delivery_model": "Agile",
            "system_type": "microservices",
            "domain": "insurance",
            "quality_goal": "regression stability",
            "business_goal": "reduce defect escape rate",
            "existing_automation_state": "partial",
            "target_automation_state": "phased expansion",
            "ci_cd_maturity": "partial",
            "ai_adoption_posture": "cautious",
            "regulatory_or_compliance_needs": ["GDPR", "PCI-DSS"],
            "critical_business_flows": ["claim filing", "payment processing"],
            "known_constraints": ["legacy backend"],
            "delivery_risks": ["tight timeline"],
            "key_integrations": ["payment gateway"],
            "missing_information": [],
            "human_review_expectations": ["QE lead sign-off"],
            "environment_maturity": "partial",
            "test_data_maturity": "partial",
        },
    )


class PromptBuilderTests(unittest.TestCase):
    def _build(self) -> str:
        from ai_test_strategy_generator.prompt_builder import build_prompt
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        pkg = _make_brownfield_package()
        cls = classify_context(pkg)
        dec = apply_rules(cls)
        return build_prompt(pkg, cls, dec)

    def test_prompt_includes_all_required_output_headings(self) -> None:
        from ai_test_strategy_generator.output_validator import REQUIRED_HEADINGS

        prompt = self._build()

        for heading in REQUIRED_HEADINGS:
            self.assertIn(heading, prompt, f"Prompt missing required heading: {heading}")

    def test_prompt_includes_all_required_output_labels(self) -> None:
        from ai_test_strategy_generator.output_validator import REQUIRED_LABELS

        prompt = self._build()

        for label in REQUIRED_LABELS:
            self.assertIn(label, prompt, f"Prompt missing required label: {label}")

    def test_prompt_includes_no_invention_instruction(self) -> None:
        prompt = self._build()

        self.assertIn("Do not invent", prompt)

    def test_prompt_includes_assumption_surfacing_instruction(self) -> None:
        prompt = self._build()

        self.assertIn("assumption", prompt.lower())

    def test_prompt_includes_engagement_posture(self) -> None:
        prompt = self._build()

        self.assertIn("brownfield", prompt)

    def test_prompt_includes_engagement_domain(self) -> None:
        prompt = self._build()

        self.assertIn("insurance", prompt)

    def test_prompt_includes_automation_state(self) -> None:
        prompt = self._build()

        self.assertIn("partial", prompt)

    def test_prompt_includes_classification_system_profile(self) -> None:
        prompt = self._build()

        # microservices -> api_first in classify_context
        self.assertIn("api_first", prompt)

    def test_prompt_includes_classification_regulatory_sensitivity(self) -> None:
        prompt = self._build()

        # insurance domain -> high
        self.assertIn("high", prompt)

    def test_prompt_includes_deterministic_rule_for_brownfield_transition(self) -> None:
        prompt = self._build()

        self.assertIn("assess_reuse_stabilize_retire_replace", prompt)

    def test_prompt_includes_scenario_specific_instructions(self) -> None:
        prompt = self._build()

        # Insurance domain triggers compliance_heavy scenario via regulatory_sensitivity=high
        self.assertIn("compliance", prompt.lower())

    def test_prompt_is_non_empty_string(self) -> None:
        prompt = self._build()

        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 100)

    def test_prompt_does_not_contradict_deterministic_decisions_instruction(self) -> None:
        prompt = self._build()

        self.assertIn("not modify", prompt.lower())


class ScenarioSelectionTests(unittest.TestCase):
    def test_brownfield_posture_selects_brownfield(self) -> None:
        cls = {
            "project_posture": "brownfield",
            "automation_maturity": "partial",
            "ci_cd_maturity": "partial",
            "system_profile": "api_first",
            "regulatory_sensitivity": "low",
            "information_completeness": "sufficient",
        }
        self.assertEqual(_select_scenario(cls), "brownfield")

    def test_greenfield_posture_selects_greenfield(self) -> None:
        cls = {
            "project_posture": "greenfield",
            "automation_maturity": "none",
            "ci_cd_maturity": "none",
            "system_profile": "general",
            "regulatory_sensitivity": "low",
            "information_completeness": "sufficient",
        }
        self.assertEqual(_select_scenario(cls), "greenfield")

    def test_incomplete_context_overrides_all(self) -> None:
        cls = {
            "project_posture": "greenfield",
            "automation_maturity": "unknown",
            "ci_cd_maturity": "unknown",
            "system_profile": "general",
            "regulatory_sensitivity": "high",
            "information_completeness": "incomplete",
        }
        self.assertEqual(_select_scenario(cls), "incomplete_context")

    def test_compliance_heavy_overrides_greenfield(self) -> None:
        cls = {
            "project_posture": "greenfield",
            "automation_maturity": "none",
            "ci_cd_maturity": "none",
            "system_profile": "general",
            "regulatory_sensitivity": "high",
            "information_completeness": "sufficient",
        }
        self.assertEqual(_select_scenario(cls), "compliance_heavy")

    def test_compliance_heavy_overrides_brownfield(self) -> None:
        cls = {
            "project_posture": "brownfield",
            "automation_maturity": "partial",
            "ci_cd_maturity": "partial",
            "system_profile": "api_first",
            "regulatory_sensitivity": "high",
            "information_completeness": "sufficient",
        }
        self.assertEqual(_select_scenario(cls), "compliance_heavy")

    def test_unknown_posture_defaults_to_brownfield(self) -> None:
        cls = {
            "project_posture": "",
            "automation_maturity": "unknown",
            "ci_cd_maturity": "unknown",
            "system_profile": "general",
            "regulatory_sensitivity": "low",
            "information_completeness": "sufficient",
        }
        self.assertEqual(_select_scenario(cls), "brownfield")


class ScenarioContentInPromptTests(unittest.TestCase):
    def _build_with_posture(self, posture: str, domain: str = "retail") -> str:
        from ai_test_strategy_generator.prompt_builder import build_prompt
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        pkg = InputPackage(
            source_path=Path("test.yaml"),
            raw={},
            normalized={
                "project_posture": posture,
                "delivery_model": "Agile",
                "system_type": "web",
                "domain": domain,
                "quality_goal": "quality",
                "business_goal": "delivery",
                "existing_automation_state": "none",
                "target_automation_state": "full",
                "ci_cd_maturity": "none",
                "ai_adoption_posture": "cautious",
                "regulatory_or_compliance_needs": [],
                "critical_business_flows": [],
                "known_constraints": [],
                "delivery_risks": [],
                "key_integrations": [],
                "missing_information": [],
                "human_review_expectations": [],
                "environment_maturity": "none",
                "test_data_maturity": "none",
            },
        )
        cls = classify_context(pkg)
        dec = apply_rules(cls)
        return build_prompt(pkg, cls, dec)

    def test_greenfield_prompt_contains_greenfield_instructions(self) -> None:
        prompt = self._build_with_posture("greenfield")

        self.assertIn("shift-left", prompt)
        self.assertIn("test pyramid", prompt.lower())

    def test_brownfield_prompt_contains_brownfield_instructions(self) -> None:
        prompt = self._build_with_posture("brownfield")

        self.assertIn("stabilization", prompt.lower())
        self.assertIn("regression", prompt.lower())

    def test_compliance_heavy_prompt_contains_compliance_instructions(self) -> None:
        prompt = self._build_with_posture("brownfield", domain="insurance")

        self.assertIn("traceability", prompt.lower())
        self.assertIn("audit", prompt.lower())


# ------------------------------------------------------------------
# Phase 11B4 — NFR context line in prompt
# ------------------------------------------------------------------

class NFRPromptContextTests(unittest.TestCase):
    def _make_package_with_nfr(self, nfr_priorities: list[str]) -> InputPackage:
        return InputPackage(
            source_path=Path("test.yaml"),
            raw={},
            normalized={
                "project_posture": "brownfield",
                "delivery_model": "Agile",
                "system_type": "API",
                "domain": "fintech",
                "quality_goal": "stability",
                "business_goal": "reduce risk",
                "existing_automation_state": "partial",
                "target_automation_state": "full",
                "ci_cd_maturity": "partial",
                "ai_adoption_posture": "cautious",
                "regulatory_or_compliance_needs": [],
                "critical_business_flows": [],
                "known_constraints": [],
                "delivery_risks": [],
                "key_integrations": [],
                "missing_information": [],
                "human_review_expectations": [],
                "environment_maturity": "partial",
                "test_data_maturity": "partial",
                "nfr_priorities": nfr_priorities,
            },
        )

    def test_prompt_context_includes_nfr_line_when_priorities_provided(self) -> None:
        from ai_test_strategy_generator.prompt_builder import build_prompt
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        pkg = self._make_package_with_nfr(["performance", "security", "compliance"])
        cls = classify_context(pkg)
        dec = apply_rules(cls)
        prompt = build_prompt(pkg, cls, dec)

        self.assertIn("Non-Functional Priorities: performance, security, compliance", prompt)

    def test_prompt_context_omits_nfr_line_when_no_priorities(self) -> None:
        from ai_test_strategy_generator.prompt_builder import build_prompt
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        pkg = self._make_package_with_nfr([])
        cls = classify_context(pkg)
        dec = apply_rules(cls)
        prompt = build_prompt(pkg, cls, dec)

        # The label appears in the required output schema section but NOT in the engagement context block
        # We verify the engagement context block does not contain the specific NFR values
        self.assertNotIn("Non-Functional Priorities: ", prompt.split("## Required Output Contract")[0])


# ------------------------------------------------------------------
# P12 field coverage — prompt_builder must pass all new schema fields
# ------------------------------------------------------------------

class P12PromptFieldCoverageTests(unittest.TestCase):
    """Regression guard: every P12 input schema field must appear in the LLM prompt.

    If a new input field is added to the schema but forgotten in prompt_builder,
    the LLM cannot produce context-correct output for that field — this class
    catches any such omission.
    """

    def _build_with_p12_fields(self) -> str:
        from ai_test_strategy_generator.prompt_builder import build_prompt
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        pkg = InputPackage(
            source_path=Path("test.yaml"),
            raw={},
            normalized={
                "project_posture": "brownfield",
                "delivery_model": "Agile",
                "system_type": "API",
                "domain": "fintech",
                "quality_goal": "stability",
                "business_goal": "reduce risk",
                "existing_automation_state": "partial",
                "target_automation_state": "full",
                "ci_cd_maturity": "partial",
                "ai_adoption_posture": "cautious",
                "regulatory_or_compliance_needs": [],
                "critical_business_flows": [],
                "known_constraints": [],
                "delivery_risks": [],
                "key_integrations": [],
                "missing_information": [],
                "human_review_expectations": [],
                "environment_maturity": "partial",
                "test_data_maturity": "partial",
                "nfr_priorities": [],
                # P12 fields
                "release_cadence": "monthly",
                "qe_capacity": "medium",
                "team_topology": "embedded-qe",
                "reporting_audience": "executive",
                "environment_constraints": ["no prod access"],
                "data_privacy_constraints": ["GDPR"],
                "target_quality_gates": ["smoke gate", "regression gate"],
            },
        )
        cls = classify_context(pkg)
        dec = apply_rules(cls)
        return build_prompt(pkg, cls, dec)

    def test_prompt_includes_release_cadence(self) -> None:
        prompt = self._build_with_p12_fields()
        self.assertIn("Release Cadence: monthly", prompt)

    def test_prompt_includes_qe_capacity(self) -> None:
        prompt = self._build_with_p12_fields()
        self.assertIn("QE Capacity: medium", prompt)

    def test_prompt_includes_team_topology(self) -> None:
        prompt = self._build_with_p12_fields()
        self.assertIn("Team Topology: embedded-qe", prompt)

    def test_prompt_includes_reporting_audience(self) -> None:
        prompt = self._build_with_p12_fields()
        self.assertIn("Reporting Audience: executive", prompt)

    def test_prompt_includes_environment_constraints(self) -> None:
        prompt = self._build_with_p12_fields()
        self.assertIn("no prod access", prompt)

    def test_prompt_includes_data_privacy_constraints(self) -> None:
        prompt = self._build_with_p12_fields()
        self.assertIn("GDPR", prompt)

    def test_prompt_includes_target_quality_gates(self) -> None:
        prompt = self._build_with_p12_fields()
        self.assertIn("smoke gate", prompt)
        self.assertIn("regression gate", prompt)

    def test_prompt_p12_fields_present_when_empty(self) -> None:
        """Empty P12 fields must still appear as labelled lines, not be silently dropped."""
        from ai_test_strategy_generator.prompt_builder import build_prompt
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        pkg = InputPackage(
            source_path=Path("test.yaml"),
            raw={},
            normalized={
                "project_posture": "brownfield",
                "delivery_model": "Agile",
                "system_type": "API",
                "domain": "retail",
                "quality_goal": "quality",
                "business_goal": "delivery",
                "existing_automation_state": "partial",
                "target_automation_state": "full",
                "ci_cd_maturity": "partial",
                "ai_adoption_posture": "cautious",
                "regulatory_or_compliance_needs": [],
                "critical_business_flows": [],
                "known_constraints": [],
                "delivery_risks": [],
                "key_integrations": [],
                "missing_information": [],
                "human_review_expectations": [],
                "environment_maturity": "partial",
                "test_data_maturity": "partial",
                "nfr_priorities": [],
                "release_cadence": "",
                "qe_capacity": "",
                "team_topology": "",
                "reporting_audience": "",
                "environment_constraints": [],
                "data_privacy_constraints": [],
                "target_quality_gates": [],
            },
        )
        cls = classify_context(pkg)
        dec = apply_rules(cls)
        prompt = build_prompt(pkg, cls, dec)
        # Labels must still appear as keys even with empty values
        self.assertIn("Release Cadence:", prompt)
        self.assertIn("QE Capacity:", prompt)
        self.assertIn("Reporting Audience:", prompt)


# ------------------------------------------------------------------
# Heading validation — line-anchored, not substring
# ------------------------------------------------------------------

class HeadingValidationLineAnchorTests(unittest.TestCase):
    """validate_output must reject headings that appear only inside prose or
    code blocks and not as standalone section lines.
    """

    def _good_output(self) -> str:
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy

        pkg = load_input(Path("benchmarks/brownfield-partial-automation.input.yaml"))
        return render_strategy(pkg, classify_context(pkg), apply_rules(classify_context(pkg)))

    def test_heading_embedded_in_prose_does_not_satisfy_heading_check(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output

        # Build a document that mentions ## Executive Summary inside a paragraph,
        # then removes the standalone heading line.
        good = self._good_output()
        # Document starts with "## Executive Summary" at line 1 (no leading newline)
        # Replace only the standalone first-line heading with a prose embedding.
        tampered = good.replace(
            "## Executive Summary\n",
            "This section expands on ## Executive Summary context.\n",
            1,  # first occurrence only
        )
        assert "## Executive Summary" in tampered  # still present in prose
        result = validate_output(tampered)
        self.assertFalse(
            result.is_valid,
            "Heading embedded in prose should NOT satisfy required heading check",
        )
        self.assertTrue(
            any("Executive Summary" in e for e in result.errors),
            f"Expected heading error for Executive Summary; got: {result.errors}",
        )

    def test_heading_with_leading_spaces_does_not_satisfy_check(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output

        good = self._good_output()
        # Indent the heading by 4 spaces (common LLM mistake, e.g. inside a code block prose)
        # rstrip-only check means leading spaces cause the line NOT to match the heading
        tampered = good.replace(
            "## Executive Summary\n",
            "    ## Executive Summary\n",
            1,
        )
        result = validate_output(tampered)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Executive Summary" in e for e in result.errors))

    def test_valid_headings_at_line_start_still_pass(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output

        good = self._good_output()
        result = validate_output(good)
        self.assertTrue(result.is_valid, result.errors)


# ------------------------------------------------------------------
# optimize_and_govern layering — rule engine and renderer
# ------------------------------------------------------------------

class OptimizeAndGovernLayeringTests(unittest.TestCase):
    """strong automation_maturity must produce layering_priority=optimize_and_govern
    for non-greenfield postures, and the renderer must take the specialized branch.
    """

    def test_strong_automation_brownfield_sets_optimize_and_govern_layering(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules

        d = apply_rules({
            "automation_maturity": "strong",
            "project_posture": "brownfield",
            **{k: "unknown" for k in [
                "ci_cd_maturity", "system_profile", "regulatory_sensitivity",
                "information_completeness", "release_frequency", "nfr_priority",
            ]}
        })
        self.assertEqual(d["layering_priority"], "optimize_and_govern")

    def test_strong_automation_greenfield_keeps_lower_layers_first(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules

        d = apply_rules({
            "automation_maturity": "strong",
            "project_posture": "greenfield",
            **{k: "unknown" for k in [
                "ci_cd_maturity", "system_profile", "regulatory_sensitivity",
                "information_completeness", "release_frequency", "nfr_priority",
            ]}
        })
        self.assertEqual(d["layering_priority"], "lower_layers_first")

    def test_strong_automation_legacy_overridden_by_system_profile(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules

        d = apply_rules({
            "automation_maturity": "strong",
            "project_posture": "brownfield",
            "system_profile": "legacy",
            **{k: "unknown" for k in [
                "ci_cd_maturity", "regulatory_sensitivity",
                "information_completeness", "release_frequency", "nfr_priority",
            ]}
        })
        # legacy overrides optimize_and_govern
        self.assertEqual(d["layering_priority"], "stabilize_lower_layers_then_ui")

    def test_strong_automation_renderer_takes_optimize_branch(self) -> None:
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy

        pkg = load_input(Path("benchmarks/strong-automation-weak-governance.input.yaml"))
        c = classify_context(pkg)
        d = apply_rules(c)
        assert d["layering_priority"] == "optimize_and_govern", (
            f"Precondition: strong-automation benchmark must produce optimize_and_govern; got {d['layering_priority']}"
        )
        md = render_strategy(pkg, c, d)
        self.assertIn(
            "maintain existing pyramid",
            md,
            "Strong automation must render 'maintain existing pyramid' coverage layer guidance",
        )
        self.assertIn("retire stale tests", md)

    def test_partial_automation_does_not_set_optimize_and_govern_layering(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules

        d = apply_rules({
            "automation_maturity": "partial",
            "project_posture": "brownfield",
            **{k: "unknown" for k in [
                "ci_cd_maturity", "system_profile", "regulatory_sensitivity",
                "information_completeness", "release_frequency", "nfr_priority",
            ]}
        })
        self.assertNotEqual(d["layering_priority"], "optimize_and_govern")


if __name__ == "__main__":
    unittest.main()
