from __future__ import annotations

import unittest


class ComparisonReportTests(unittest.TestCase):
    _DET = (
        "## Executive Summary\nStrategy Confidence: standard\n\n"
        "## Engagement Context\nProject Posture: brownfield\n"
    )
    _LLM = (
        "## Executive Summary\nStrategy Confidence: standard\n"
        "This brownfield engagement requires a phased approach.\n\n"
        "## Engagement Context\nProject Posture: brownfield\nDelivery Context: complex\n"
    )

    def test_report_contains_input_description(self) -> None:
        from ai_test_strategy_generator.comparison import build_comparison_report

        report = build_comparison_report("my-input.yaml", self._DET, self._LLM)

        self.assertIn("my-input.yaml", report)

    def test_report_contains_both_section_headers(self) -> None:
        from ai_test_strategy_generator.comparison import build_comparison_report

        report = build_comparison_report("my-input.yaml", self._DET, self._LLM)

        self.assertIn("## Deterministic Strategy", report)
        self.assertIn("## LLM-Assisted Strategy", report)

    def test_report_contains_summary_table(self) -> None:
        from ai_test_strategy_generator.comparison import build_comparison_report

        report = build_comparison_report("my-input.yaml", self._DET, self._LLM)

        self.assertIn("## Summary", report)
        self.assertIn("Output Lines", report)
        self.assertIn("Word Count", report)

    def test_report_embeds_deterministic_content(self) -> None:
        from ai_test_strategy_generator.comparison import build_comparison_report

        report = build_comparison_report("my-input.yaml", self._DET, self._LLM)

        self.assertIn("Strategy Confidence: standard", report)
        self.assertIn("Project Posture: brownfield", report)

    def test_report_embeds_llm_content(self) -> None:
        from ai_test_strategy_generator.comparison import build_comparison_report

        report = build_comparison_report("my-input.yaml", self._DET, self._LLM)

        self.assertIn("phased approach", report)
        self.assertIn("Delivery Context: complex", report)

    def test_report_ends_with_newline(self) -> None:
        from ai_test_strategy_generator.comparison import build_comparison_report

        report = build_comparison_report("my-input.yaml", self._DET, self._LLM)

        self.assertTrue(report.endswith("\n"))

    def test_report_line_counts_are_accurate(self) -> None:
        from ai_test_strategy_generator.comparison import build_comparison_report

        report = build_comparison_report("my-input.yaml", self._DET, self._LLM)

        det_lines = str(len(self._DET.splitlines()))
        llm_lines = str(len(self._LLM.splitlines()))
        self.assertIn(det_lines, report)
        self.assertIn(llm_lines, report)

    def test_quality_indicators_table_present_when_repair_stats_provided(self) -> None:
        from ai_test_strategy_generator.comparison import build_comparison_report

        stats = {
            "total_headings": 10,
            "headings_injected": 2,
            "total_labels": 8,
            "labels_injected": 1,
        }
        report = build_comparison_report("my-input.yaml", self._DET, self._LLM, repair_stats=stats)

        self.assertIn("## Quality Indicators", report)
        self.assertIn("Headings from LLM", report)
        self.assertIn("8 / 10", report)
        self.assertIn("Labels from LLM", report)
        self.assertIn("7 / 8", report)
        self.assertIn("Headings injected by repair", report)
        self.assertIn("Labels injected by repair", report)

    def test_quality_indicators_table_absent_when_repair_stats_omitted(self) -> None:
        from ai_test_strategy_generator.comparison import build_comparison_report

        report = build_comparison_report("my-input.yaml", self._DET, self._LLM)

        self.assertNotIn("## Quality Indicators", report)
        self.assertNotIn("Headings from LLM", report)


if __name__ == "__main__":
    unittest.main()
