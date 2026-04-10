"""Comparison report generator for deterministic vs LLM-assisted strategy outputs."""
from __future__ import annotations

import datetime


def build_comparison_report(
    input_description: str,
    deterministic_markdown: str,
    llm_markdown: str,
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
