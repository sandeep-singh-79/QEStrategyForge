from __future__ import annotations

from ai_test_strategy_generator.models import (
    ClassificationResult,
    InputPackage,
    StrategyDocument,
    StrategySection,
)


def render_strategy(
    input_package: InputPackage,
    classifications: ClassificationResult,
    decisions: dict[str, str],
) -> str:
    return build_strategy_document(input_package, classifications, decisions).to_markdown()


def build_strategy_document(
    input_package: InputPackage,
    classifications: ClassificationResult,
    decisions: dict[str, str],
) -> StrategyDocument:
    data = input_package.normalized
    missing_information = _join_list(data.get("missing_information", []))
    critical_flows = _join_list(data.get("critical_business_flows", []))
    constraints = _join_list(data.get("known_constraints", []))
    risks = _join_list(data.get("delivery_risks", []))
    integrations = _join_list(data.get("key_integrations", []))
    compliance = _join_list(data.get("regulatory_or_compliance_needs", []))
    human_review = _join_list(data.get("human_review_expectations", []))
    return StrategyDocument(
        sections=[
            StrategySection(
                heading="## Executive Summary",
                lines=[
                    f"Strategy Confidence: {decisions['strategy_confidence']}",
                    f"This strategy is tailored for a {data.get('project_posture', 'unknown')} engagement with a focus on {data.get('quality_goal', 'quality improvement')}.",
                ],
            ),
            StrategySection(
                heading="## Engagement Context",
                lines=[
                    f"Project Posture: {data.get('project_posture', 'unknown')}",
                    f"Delivery Model: {data.get('delivery_model', 'unknown')}",
                    f"System Type: {data.get('system_type', 'unknown')}",
                    f"Critical Business Flows: {critical_flows}",
                    f"Key Constraints: {constraints}",
                ],
            ),
            StrategySection(
                heading="## Quality Objectives And Risk Priorities",
                lines=[
                    f"Primary Quality Goal: {data.get('quality_goal', 'Not provided')}",
                    f"Business Goal: {data.get('business_goal', 'Not provided')}",
                    f"Risk Priorities: {risks}",
                    f"Compliance Focus: {compliance}",
                ],
            ),
            StrategySection(
                heading="## Lifecycle Posture",
                lines=[
                    f"Shift-Left Stance: {decisions['shift_left_stance']}",
                    "Shift-Right Stance: selective where production signals are available",
                    "Prevention vs Detection Balance: prevention first where feasible, detection where legacy or integration risk remains",
                    "Lifecycle Checkpoints: requirements -> design -> build -> integration -> release readiness",
                ],
            ),
            StrategySection(
                heading="## Layered Test Strategy",
                lines=[
                    f"Layering Priority: {decisions['layering_priority']}",
                    f"System Profile: {classifications['system_profile']}",
                    "Recommended Coverage Layers: unit / component / integration / API / UI / regression with emphasis adjusted by context",
                ],
            ),
            StrategySection(
                heading="## Test Types And Coverage Focus",
                lines=[
                    "Functional Coverage: critical business flows and high-risk integrations",
                    "Regression Coverage: risk-based and posture-aware",
                    "Exploratory Coverage: targeted around uncertainty and legacy behavior",
                    "Non-Functional Priorities: performance, security, accessibility, and resilience where context requires them",
                ],
            ),
            StrategySection(
                heading="## Automation Strategy",
                lines=_automation_strategy_lines(data, decisions),
            ),
            StrategySection(
                heading="## CI/CD And Quality Gates",
                lines=[
                    f"Current CI/CD Maturity: {data.get('ci_cd_maturity', 'unknown')}",
                    f"Target CI/CD Posture: {decisions['ci_cd_posture']}",
                    "Pipeline Quality Gates: smoke, critical-path, and risk-based checks scaled to current maturity",
                    "Release Decision Guidance: use explicit quality signals rather than subjective judgment alone",
                    "quality gate progression should support clearer release decisions as delivery maturity improves",
                ],
            ),
            StrategySection(
                heading="## Test Data Strategy",
                lines=[
                    f"Current Test Data Maturity: {data.get('test_data_maturity', 'unknown')}",
                    "Data Handling Guidance: protect privacy-sensitive data and use synthetic or masked data where needed",
                    f"Data Risk Notes: {compliance}",
                ],
            ),
            StrategySection(
                heading="## Environment Strategy",
                lines=[
                    f"Current Environment Maturity: {data.get('environment_maturity', 'unknown')}",
                    f"Key Integrations: {integrations}",
                    "Environment Guidance: align environments to integration risk and use virtualization where dependencies are unstable",
                ],
            ),
            StrategySection(
                heading="## Defect, Triage, And Reporting Model",
                lines=[
                    "Defect Triage: establish regular triage with shared ownership",
                    f"Reporting Emphasis: {decisions['reporting_emphasis']}",
                    f"Governance Depth: {decisions['governance_depth']}",
                    "Recommended KPIs: defect leakage, release confidence, automation coverage, cycle time",
                    "reporting should make release risk visible enough for quality gate decisions",
                ],
            ),
            StrategySection(
                heading="## AI Usage Model",
                lines=[
                    f"AI Adoption Posture: {data.get('ai_adoption_posture', 'unknown')}",
                    "Allowed AI Uses: drafting, gap detection, reporting summarization, strategy acceleration",
                    "Constrained AI Uses: compliance interpretation, release approval, unsupported completeness claims",
                    f"Human Review Boundaries: {human_review}",
                ],
            ),
            StrategySection(
                heading="## Assumptions, Gaps, And Open Questions",
                lines=[
                    f"Missing Information: {missing_information}",
                    f"Assumption Mode: {decisions['assumption_mode']}",
                    "Open Questions: confirm missing architecture, automation baseline, CI/CD posture, and operational feedback before finalizing target-state commitments",
                ],
            ),
            StrategySection(
                heading="## Recommended Next Steps",
                lines=[
                    "Recommended Immediate Actions: validate current-state evidence, confirm release model, and baseline automation and CI/CD maturity",
                    "Medium-Term Actions: refine layer strategy, target-state automation, and governance model once discovery improves",
                    "Validation Guidance: run deterministic checks before using the strategy as a committed delivery position",
                ],
            ),
        ]
    )


def _join_list(values: object) -> str:
    if isinstance(values, list) and values:
        return "; ".join(str(value) for value in values)
    return "None declared"


def _brownfield_transition_line(decisions: dict[str, str]) -> str:
    strategy = decisions.get("brownfield_transition_strategy", "not_applicable")
    if strategy == "not_applicable":
        return ""
    return f"Brownfield Transition Strategy: {strategy}"

def _automation_strategy_lines(data: dict[str, object], decisions: dict[str, str]) -> list[str]:
    lines = [
        f"Current Automation State: {data.get('existing_automation_state', 'unknown')}",
        f"Target Automation State: guided by {decisions['automation_adoption_path']}",
        f"Automation Adoption Path: {decisions['automation_adoption_path']}",
    ]
    brownfield_transition_line = _brownfield_transition_line(decisions)
    if brownfield_transition_line:
        lines.append(brownfield_transition_line)
    lines.append("Manual Retention Guidance: keep exploratory and unstable-path validation manual until confidence improves")
    return lines
