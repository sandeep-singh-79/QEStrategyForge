from __future__ import annotations

import unittest

from ai_test_strategy_generator.models import PromptTemplate
from ai_test_strategy_generator.template_loader import load_template


class TemplateLoaderTests(unittest.TestCase):
    def test_load_base_template_returns_prompt_template(self) -> None:
        result = load_template("base")

        self.assertIsInstance(result, PromptTemplate)
        self.assertEqual(result.name, "base")
        self.assertEqual(result.version, "v1")

    def test_load_base_template_has_expected_placeholders(self) -> None:
        result = load_template("base")

        for placeholder in [
            "{engagement_context}",
            "{classifications}",
            "{decisions}",
            "{required_headings}",
            "{required_labels}",
            "{scenario_instructions}",
        ]:
            self.assertIn(placeholder, result.template_text)

    def test_load_base_template_has_section_headings(self) -> None:
        result = load_template("base")

        for heading in [
            "## Engagement Context",
            "## Context Classification (Deterministic)",
            "## Deterministic Rule Decisions",
            "## Required Output Contract",
            "## Instructions",
        ]:
            self.assertIn(heading, result.template_text)

    def test_load_nonexistent_template_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_template("nonexistent")

    def test_load_nonexistent_version_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_template("base", version="v99")

    def test_template_text_is_non_empty(self) -> None:
        result = load_template("base")

        self.assertGreater(len(result.template_text), 100)

    def test_load_brownfield_scenario_template(self) -> None:
        result = load_template("brownfield")

        self.assertEqual(result.name, "brownfield")
        self.assertIn("brownfield", result.template_text.lower())
        self.assertNotIn("{", result.template_text)

    def test_load_greenfield_scenario_template(self) -> None:
        result = load_template("greenfield")

        self.assertEqual(result.name, "greenfield")
        self.assertIn("greenfield", result.template_text.lower())
        self.assertNotIn("{", result.template_text)

    def test_load_incomplete_context_scenario_template(self) -> None:
        result = load_template("incomplete_context")

        self.assertEqual(result.name, "incomplete_context")
        self.assertIn("assumption", result.template_text.lower())
        self.assertNotIn("{", result.template_text)

    def test_load_compliance_heavy_scenario_template(self) -> None:
        result = load_template("compliance_heavy")

        self.assertEqual(result.name, "compliance_heavy")
        self.assertIn("compliance", result.template_text.lower())
        self.assertNotIn("{", result.template_text)


if __name__ == "__main__":
    unittest.main()
