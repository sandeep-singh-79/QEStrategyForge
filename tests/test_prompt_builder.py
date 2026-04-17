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


if __name__ == "__main__":
    unittest.main()
