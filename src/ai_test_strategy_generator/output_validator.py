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
    "Assumption Mode:",
    "Strategy Confidence:",
    "Recommended Immediate Actions:",
    "Non-Functional Priorities:",
]


def validate_output(markdown: str) -> ValidationResult:
    errors: list[str] = []

    for heading in REQUIRED_HEADINGS:
        if heading not in markdown:
            errors.append(f"Missing required heading: {heading}")

    for label in REQUIRED_LABELS:
        if label not in markdown:
            errors.append(f"Missing required label: {label}")

    return ValidationResult(is_valid=not errors, errors=errors)
