from __future__ import annotations

import unittest

from ai_test_strategy_generator.models import StrategyDocument, StrategySection


class StrategyDocumentTests(unittest.TestCase):
    def test_to_markdown_joins_sections_with_single_blank_lines(self) -> None:
        document = StrategyDocument(
            sections=[
                StrategySection("## One", ["Line A", "Line B"]),
                StrategySection("## Two", ["Line C"]),
            ]
        )

        markdown = document.to_markdown()

        self.assertEqual(markdown, "## One\nLine A\nLine B\n\n## Two\nLine C\n")


if __name__ == "__main__":
    unittest.main()
