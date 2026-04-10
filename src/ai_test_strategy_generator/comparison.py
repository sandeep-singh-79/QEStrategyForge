"""Comparison report generator for deterministic vs LLM-assisted strategy outputs."""
from __future__ import annotations

import datetime


def build_comparison_report(
    input_description: str,
    deterministic_markdown: str,
    llm_markdown: str,
    repair_stats: dict[str, object] | None = None,
) -> str:
    """Generate a markdown side-by-side comparison of deterministic vs LLM output."""
    det_lines = deterministic_markdown.splitlines()
    llm_lines = llm_markdown.splitlines()
    det_sections = _count_sections(deterministic_markdown)
    llm_sections = _count_sections(llm_markdown)
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")

    report_lines = [
        "# Strategy Comparison: Deterministic vs LLM-Assisted",
        "",
        f"**Input:** {input_description}",
        f"**Generated:** {timestamp}",
        "",
        "## Summary",
        "",
        "| Attribute | Deterministic | LLM-Assisted |",
        "|---|---|---|",
        f"| Output Lines | {len(det_lines)} | {len(llm_lines)} |",
        f"| Word Count | {_word_count(deterministic_markdown)} | {_word_count(llm_markdown)} |",
        f"| Sections | {det_sections} | {llm_sections} |",
        "",
    ]

    if repair_stats is not None:
        total_headings = int(repair_stats.get("total_headings", 0))
        headings_injected = int(repair_stats.get("headings_injected", 0))
        total_labels = int(repair_stats.get("total_labels", 0))
        labels_injected = int(repair_stats.get("labels_injected", 0))
        headings_from_llm = total_headings - headings_injected
        labels_from_llm = total_labels - labels_injected
        report_lines += [
            "## Quality Indicators",
            "",
            "| Metric | Value |",
            "|---|---|",
            f"| Headings from LLM | {headings_from_llm} / {total_headings} |",
            f"| Headings injected by repair | {headings_injected} |",
            f"| Labels from LLM | {labels_from_llm} / {total_labels} |",
            f"| Labels injected by repair | {labels_injected} |",
            "",
        ]

    report_lines += [
        "---",
        "",
        "## Deterministic Strategy",
        "",
        deterministic_markdown.rstrip(),
        "",
        "---",
        "",
        "## LLM-Assisted Strategy",
        "",
        llm_markdown.rstrip(),
    ]
    return "\n".join(report_lines) + "\n"


def _count_sections(markdown: str) -> int:
    return sum(1 for line in markdown.splitlines() if line.startswith("## "))


def _word_count(text: str) -> int:
    return len(text.split())
