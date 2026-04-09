from __future__ import annotations

from ai_test_strategy_generator.models import ClassificationResult, InputPackage
from ai_test_strategy_generator.output_validator import REQUIRED_HEADINGS, REQUIRED_LABELS

_NO_INVENTION_INSTRUCTION = (
    "Do not invent facts, systems, constraints, or requirements that are not present "
    "in the engagement context above. If information is missing, state it explicitly "
    "in the Assumptions, Gaps, And Open Questions section."
)

_ASSUMPTION_INSTRUCTION = (
    "Surface all assumptions clearly. Do not present inferred or default values as "
    "confirmed facts. Use conditional language where certainty is not supported by "
    "the provided context."
)


def build_prompt(
    input_package: InputPackage,
    classifications: ClassificationResult,
    decisions: dict[str, str],
) -> str:
    """Build a bounded prompt from normalized input, classification, and rule outputs."""
    blocks = [
        _engagement_context_block(input_package.normalized),
        _classification_block(classifications),
        _decision_block(decisions),
        _output_contract_block(),
        _instruction_block(),
    ]
    return "\n\n".join(blocks)


def _engagement_context_block(data: dict[str, object]) -> str:
    lines = [
        "## Engagement Context",
        f"Project Posture: {data.get('project_posture', 'unknown')}",
        f"Delivery Model: {data.get('delivery_model', 'unknown')}",
        f"System Type: {data.get('system_type', 'unknown')}",
        f"Domain: {data.get('domain', 'unknown')}",
        f"Quality Goal: {data.get('quality_goal', 'not provided')}",
        f"Business Goal: {data.get('business_goal', 'not provided')}",
        f"Existing Automation State: {data.get('existing_automation_state', 'unknown')}",
        f"Target Automation State: {data.get('target_automation_state', 'unknown')}",
        f"Current Automation State: {data.get('existing_automation_state', 'unknown')}",
        f"Current CI/CD Maturity: {data.get('ci_cd_maturity', 'unknown')}",
        f"AI Adoption Posture: {data.get('ai_adoption_posture', 'unknown')}",
        f"Regulatory Needs: {_join(data.get('regulatory_or_compliance_needs', []))}",
        f"Critical Business Flows: {_join(data.get('critical_business_flows', []))}",
        f"Key Constraints: {_join(data.get('known_constraints', []))}",
        f"Delivery Risks: {_join(data.get('delivery_risks', []))}",
        f"Key Integrations: {_join(data.get('key_integrations', []))}",
        f"Missing Information: {_join(data.get('missing_information', []))}",
        f"Human Review Boundaries: {_join(data.get('human_review_expectations', []))}",
    ]
    return "\n".join(lines)


def _classification_block(classifications: ClassificationResult) -> str:
    lines = ["## Context Classification (Deterministic)"]
    for key, value in sorted(classifications.items()):
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _decision_block(decisions: dict[str, str]) -> str:
    lines = ["## Deterministic Rule Decisions"]
    for key, value in sorted(decisions.items()):
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _output_contract_block() -> str:
    lines = [
        "## Required Output Contract",
        "Your response must be a complete markdown test strategy document.",
        "It must include ALL of the following required section headings:",
    ]
    for heading in REQUIRED_HEADINGS:
        lines.append(f"  {heading}")
    lines.append("")
    lines.append("Each section must include the following required labeled lines:")
    for label in REQUIRED_LABELS:
        lines.append(f"  {label} <value>")
    return "\n".join(lines)


def _instruction_block() -> str:
    return "\n".join([
        "## Instructions",
        _NO_INVENTION_INSTRUCTION,
        _ASSUMPTION_INSTRUCTION,
        "Do not modify or contradict the deterministic rule decisions listed above.",
        "Do not mix greenfield guidance into brownfield posture or vice versa.",
        "Ensure AI adoption guidance is consistent with the stated AI Adoption Posture.",
        "Write coherent strategy narrative connecting lifecycle, automation, governance, and AI posture.",
    ])


def _join(items: object) -> str:
    if isinstance(items, list):
        return ", ".join(str(i) for i in items) if items else "none"
    return str(items) if items else "none"
