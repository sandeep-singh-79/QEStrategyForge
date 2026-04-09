from __future__ import annotations

import unittest
from pathlib import Path

from ai_test_strategy_generator.models import InputPackage


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

    def test_prompt_includes_no_greenfield_posture_contamination_instruction(self) -> None:
        prompt = self._build()

        self.assertIn("greenfield", prompt.lower())  # mentioned explicitly to warn against mixing

    def test_prompt_is_non_empty_string(self) -> None:
        prompt = self._build()

        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 100)

    def test_prompt_does_not_contradict_deterministic_decisions_instruction(self) -> None:
        prompt = self._build()

        self.assertIn("not modify", prompt.lower())


if __name__ == "__main__":
    unittest.main()
