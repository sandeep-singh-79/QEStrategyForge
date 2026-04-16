"""Tests for prompt_mutations.py — mutation strategies."""
from __future__ import annotations

import unittest

from ai_test_strategy_generator.prompt_mutations import (
    ALL_MUTATIONS,
    apply_mutation,
    emphasis_removal,
    emphasis_strengthening,
    example_injection,
    example_removal,
    instruction_reordering,
)

_BASE_WITH_MUSTS = """\
You MUST include a risk section.
It must include every test level.
Each section must have exactly one label.
This line is unchanged.
"""

_BASE_WITHOUT_PATTERNS = "This is a plain template with no special keywords.\n"

# instruction_reordering matches "Place each decision in its natural section:\n" header
# with indented bullet lines beneath it.
_BASE_WITH_BULLETS = """\
Introduction paragraph.
Place each decision in its natural section:
  Put scope items in the Scope section.
  Put risk items in the Risk section.
  Put automation items in the Automation section.
Trailing line.
"""

# Use the actual marker that example_injection produces
_EXAMPLE_MARKER = "## EXAMPLE (do not reproduce verbatim)"


class EmphasisStrengtheningTests(unittest.TestCase):

    def test_adds_critical_prefix_to_must_lines(self) -> None:
        text, _desc = emphasis_strengthening(_BASE_WITH_MUSTS)
        self.assertIn("CRITICAL: You MUST include", text)
        self.assertIn("CRITICAL: It must include", text)
        self.assertIn("CRITICAL: Each section must", text)

    def test_unchanged_line_not_prefixed(self) -> None:
        text, _desc = emphasis_strengthening(_BASE_WITH_MUSTS)
        self.assertIn("This line is unchanged.", text)
        self.assertNotIn("CRITICAL: This line", text)

    def test_idempotent(self) -> None:
        once_text, _desc = emphasis_strengthening(_BASE_WITH_MUSTS)
        twice_text, _desc2 = emphasis_strengthening(once_text)
        self.assertEqual(once_text, twice_text)

    def test_no_op_on_plain_template(self) -> None:
        text, _desc = emphasis_strengthening(_BASE_WITHOUT_PATTERNS)
        self.assertEqual(text, _BASE_WITHOUT_PATTERNS)


class EmphasisRemovalTests(unittest.TestCase):

    def test_removes_critical_prefix(self) -> None:
        strengthened_text, _desc = emphasis_strengthening(_BASE_WITH_MUSTS)
        restored_text, _desc2 = emphasis_removal(strengthened_text)
        self.assertNotIn("CRITICAL:", restored_text)

    def test_round_trip(self) -> None:
        strengthened_text, _desc = emphasis_strengthening(_BASE_WITH_MUSTS)
        restored_text, _desc2 = emphasis_removal(strengthened_text)
        self.assertEqual(restored_text, _BASE_WITH_MUSTS)

    def test_no_op_on_plain_template(self) -> None:
        text, _desc = emphasis_removal(_BASE_WITHOUT_PATTERNS)
        self.assertEqual(text, _BASE_WITHOUT_PATTERNS)


class InstructionReorderingTests(unittest.TestCase):

    def test_output_contains_all_bullet_lines(self) -> None:
        text, _desc = instruction_reordering(_BASE_WITH_BULLETS)
        self.assertIn("Put scope items in the Scope section.", text)
        self.assertIn("Put risk items in the Risk section.", text)
        self.assertIn("Put automation items in the Automation section.", text)

    def test_non_bullet_lines_preserved(self) -> None:
        text, _desc = instruction_reordering(_BASE_WITH_BULLETS)
        self.assertIn("Introduction paragraph.", text)
        self.assertIn("Trailing line.", text)

    def test_no_op_on_plain_template(self) -> None:
        text, _desc = instruction_reordering(_BASE_WITHOUT_PATTERNS)
        self.assertEqual(text, _BASE_WITHOUT_PATTERNS)

    def test_returns_string(self) -> None:
        text, _desc = instruction_reordering(_BASE_WITH_BULLETS)
        self.assertIsInstance(text, str)


class ExampleInjectionTests(unittest.TestCase):

    def test_injects_example_block(self) -> None:
        text, _desc = example_injection(_BASE_WITHOUT_PATTERNS)
        self.assertIn(_EXAMPLE_MARKER, text)

    def test_idempotent(self) -> None:
        once_text, _desc = example_injection(_BASE_WITHOUT_PATTERNS)
        twice_text, _desc2 = example_injection(once_text)
        self.assertEqual(once_text, twice_text)

    def test_example_placed_at_end(self) -> None:
        text, _desc = example_injection(_BASE_WITHOUT_PATTERNS)
        idx_example = text.index(_EXAMPLE_MARKER)
        idx_content = text.index(_BASE_WITHOUT_PATTERNS.strip())
        self.assertGreater(idx_example, idx_content)


class ExampleRemovalTests(unittest.TestCase):

    def test_removes_example_block(self) -> None:
        # Build a template that contains the actual marker
        base_with_real_example, _ = example_injection(_BASE_WITHOUT_PATTERNS)
        text, _desc = example_removal(base_with_real_example)
        self.assertNotIn(_EXAMPLE_MARKER, text)

    def test_preserves_non_example_content(self) -> None:
        base_with_real_example, _ = example_injection("Normal content here.\nFinal line.\n")
        text, _desc = example_removal(base_with_real_example)
        self.assertIn("Normal content here.", text)
        self.assertIn("Final line.", text)

    def test_no_op_when_no_example(self) -> None:
        text, _desc = example_removal(_BASE_WITHOUT_PATTERNS)
        self.assertEqual(text, _BASE_WITHOUT_PATTERNS)

    def test_round_trip_with_injection(self) -> None:
        with_example_text, _desc = example_injection(_BASE_WITHOUT_PATTERNS)
        restored_text, _desc2 = example_removal(with_example_text)
        self.assertEqual(restored_text.strip(), _BASE_WITHOUT_PATTERNS.strip())


class AllMutationsRegistryTests(unittest.TestCase):

    def test_all_keys_present(self) -> None:
        expected = {
            "emphasis_strengthening",
            "emphasis_removal",
            "instruction_reordering",
            "example_injection",
            "example_removal",
        }
        self.assertEqual(set(ALL_MUTATIONS.keys()), expected)

    def test_apply_mutation_returns_tuple(self) -> None:
        text, description = apply_mutation(_BASE_WITH_MUSTS, "emphasis_strengthening")
        self.assertIsInstance(text, str)
        self.assertIsInstance(description, str)
        self.assertIn("CRITICAL:", text)

    def test_apply_mutation_unknown_name_raises(self) -> None:
        with self.assertRaises(KeyError):
            apply_mutation(_BASE_WITH_MUSTS, "nonexistent_strategy")


if __name__ == "__main__":
    unittest.main()
