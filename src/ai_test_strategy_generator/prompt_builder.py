from __future__ import annotations

from ai_test_strategy_generator.models import ClassificationResult, InputPackage
from ai_test_strategy_generator.output_validator import REQUIRED_HEADINGS, REQUIRED_LABELS
from ai_test_strategy_generator.template_loader import load_template


def build_prompt(
    input_package: InputPackage,
    classifications: ClassificationResult,
    decisions: dict[str, str],
) -> str:
    """Build a bounded prompt from normalized input, classification, and rule outputs."""
    base = load_template("base")
    scenario_name = _select_scenario(classifications)
    scenario = load_template(scenario_name)
    return base.template_text.format(
        engagement_context=_format_engagement_context(input_package.normalized),
        classifications=_format_classifications(classifications),
        decisions=_format_decisions(decisions),
        required_headings=_format_required_headings(),
        required_labels=_format_required_labels(),
        scenario_instructions=scenario.template_text.rstrip("\n"),
    ).rstrip("\n")


def _select_scenario(classifications: ClassificationResult) -> str:
    """Select the best scenario template based on classification priority."""
    if classifications.get("information_completeness") == "incomplete":
        return "incomplete_context"
    if classifications.get("regulatory_sensitivity") == "high":
        return "compliance_heavy"
    if classifications.get("project_posture") == "greenfield":
        return "greenfield"
    return "brownfield"


def _format_engagement_context(data: dict[str, object]) -> str:
    lines = [
        f"Project Posture: {data.get('project_posture', 'unknown')}",
        f"Delivery Model: {data.get('delivery_model', 'unknown')}",
        f"System Type: {data.get('system_type', 'unknown')}",
        f"Domain: {data.get('domain', 'unknown')}",
        f"Quality Goal: {data.get('quality_goal', 'not provided')}",
        f"Business Goal: {data.get('business_goal', 'not provided')}",
        f"Current Automation State: {data.get('existing_automation_state', 'unknown')}",
        f"Target Automation State: {data.get('target_automation_state', 'unknown')}",
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


def _format_classifications(classifications: ClassificationResult) -> str:
    return "\n".join(f"{key}: {value}" for key, value in sorted(classifications.items()))


def _format_decisions(decisions: dict[str, str]) -> str:
    return "\n".join(
        f"{key}: {value}"
        for key, value in sorted(decisions.items())
        if value != "not_applicable"
    )


def _format_required_headings() -> str:
    return "\n".join(f"  {heading}" for heading in REQUIRED_HEADINGS)


def _format_required_labels() -> str:
    return "\n".join(f"  {label} <value>" for label in REQUIRED_LABELS)


def _join(items: object) -> str:
    if isinstance(items, list):
        return ", ".join(str(i) for i in items) if items else "none"
    return str(items) if items else "none"
