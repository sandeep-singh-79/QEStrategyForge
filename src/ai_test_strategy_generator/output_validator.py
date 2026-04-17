from __future__ import annotations

from ai_test_strategy_generator.models import ValidationResult


REQUIRED_HEADINGS = [
    "## Executive Summary",
    "## Engagement Context",
    "## Quality Objectives And Risk Priorities",
    "## Lifecycle Posture",
    "## Layered Test Strategy",
    "## Test Types And Coverage Focus",
    "## Automation Strategy",
    "## CI/CD And Quality Gates",
    "## Test Data Strategy",
    "## Environment Strategy",
    "## Defect, Triage, And Reporting Model",
    "## AI Usage Model",
    "## Assumptions, Gaps, And Open Questions",
    "## Recommended Next Steps",
]

REQUIRED_LABELS = [
    "Project Posture:",
    "Delivery Model:",
    "System Type:",
    "Current Automation State:",
    "Target Automation State:",
    "Current CI/CD Maturity:",
    "Target CI/CD Posture:",
    "AI Adoption Posture:",
    "Human Review Boundaries:",
    "Missing Information:",
    "Shift-Left Stance:",
    "Layering Priority:",
    "Automation Adoption Path:",
    "Governance Depth:",
    "Reporting Emphasis:",
    "Reporting Audience:",
    "Assumption Mode:",
    "Strategy Confidence:",
    "Recommended Immediate Actions:",
    "Non-Functional Priorities:",
]

# Each entry maps a label to the section heading it must appear in.
LABEL_SECTION_MAP: dict[str, str] = {
    "Strategy Confidence:": "## Executive Summary",
    "Project Posture:": "## Engagement Context",
    "Delivery Model:": "## Engagement Context",
    "System Type:": "## Engagement Context",
    "Shift-Left Stance:": "## Lifecycle Posture",
    "Layering Priority:": "## Layered Test Strategy",
    "Non-Functional Priorities:": "## Test Types And Coverage Focus",
    "Current Automation State:": "## Automation Strategy",
    "Target Automation State:": "## Automation Strategy",
    "Automation Adoption Path:": "## Automation Strategy",
    "Current CI/CD Maturity:": "## CI/CD And Quality Gates",
    "Target CI/CD Posture:": "## CI/CD And Quality Gates",
    "Reporting Emphasis:": "## Defect, Triage, And Reporting Model",
    "Reporting Audience:": "## Defect, Triage, And Reporting Model",
    "Governance Depth:": "## Defect, Triage, And Reporting Model",
    "AI Adoption Posture:": "## AI Usage Model",
    "Human Review Boundaries:": "## AI Usage Model",
    "Missing Information:": "## Assumptions, Gaps, And Open Questions",
    "Assumption Mode:": "## Assumptions, Gaps, And Open Questions",
    "Recommended Immediate Actions:": "## Recommended Next Steps",
}


def _parse_sections(markdown: str) -> dict[str, str]:
    """Return a mapping of heading → section body text."""
    sections: dict[str, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines)
            current_heading = line.strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines)
    return sections


def validate_output(markdown: str) -> ValidationResult:
    errors: list[str] = []

    markdown_lines = markdown.splitlines()
    for heading in REQUIRED_HEADINGS:
        if not any(line.rstrip() == heading for line in markdown_lines):
            errors.append(f"Missing required heading: {heading}")

    for label in REQUIRED_LABELS:
        count = markdown.count(label)
        if count == 0:
            errors.append(f"Missing required label: {label}")
        elif count > 1:
            errors.append(f"Duplicate label found: {label} (appears {count} times)")

    sections = _parse_sections(markdown)
    for label, expected_heading in LABEL_SECTION_MAP.items():
        if label not in markdown:
            continue  # already reported as missing above
        section_body = sections.get(expected_heading, "")
        if label not in section_body:
            errors.append(f"Label '{label}' must appear in section '{expected_heading}'")

    return ValidationResult(is_valid=not errors, errors=errors)
