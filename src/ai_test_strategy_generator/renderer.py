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
    env_constraints = _join_list(data.get("environment_constraints", []))
    privacy_constraints = _join_list(data.get("data_privacy_constraints", []))
    target_gates = _join_list(data.get("target_quality_gates", []))
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
                    f"Release Cadence: {data.get('release_cadence', 'unknown')}",
                    f"QE Capacity: {data.get('qe_capacity', 'unknown')}",
                    f"Team Topology: {data.get('team_topology', 'unknown')}",
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
                lines=_lifecycle_posture_lines(decisions, classifications),
            ),
            StrategySection(
                heading="## Layered Test Strategy",
                lines=_layered_strategy_lines(decisions, classifications),
            ),
            StrategySection(
                heading="## Test Types And Coverage Focus",
                lines=[
                    "Functional Coverage: critical business flows and high-risk integrations",
                    "Regression Coverage: risk-based and posture-aware",
                    "Exploratory Coverage: targeted around uncertainty and legacy behavior",
                    *_nfr_section_lines(data, decisions),
                ],
            ),
            StrategySection(
                heading="## Automation Strategy",
                lines=_automation_strategy_lines(data, decisions),
            ),
            StrategySection(
                heading="## CI/CD And Quality Gates",
                lines=_cicd_lines(data, decisions, classifications),
            ),
            StrategySection(
                heading="## Test Data Strategy",
                lines=[
                    f"Current Test Data Maturity: {data.get('test_data_maturity', 'unknown')}",
                    "Data Handling Guidance: protect privacy-sensitive data and use synthetic or masked data where needed",
                    f"Data Privacy Constraints: {privacy_constraints}",
                    f"Data Risk Notes: {compliance}",
                ],
            ),
            StrategySection(
                heading="## Environment Strategy",
                lines=[
                    f"Current Environment Maturity: {data.get('environment_maturity', 'unknown')}",
                    f"Key Integrations: {integrations}",
                    f"Environment Constraints: {env_constraints}",
                    "Environment Guidance: align environments to integration risk and use virtualization where dependencies are unstable",
                ],
            ),
            StrategySection(
                heading="## Defect, Triage, And Reporting Model",
                lines=[
                    "Defect Triage: establish regular triage with shared ownership",
                    f"Reporting Emphasis: {decisions['reporting_emphasis']}",
                    f"Reporting Audience: {data.get('reporting_audience', 'unknown')}",
                    f"Governance Depth: {decisions['governance_depth']}",
                    "Recommended KPIs: defect leakage, release confidence, automation coverage, cycle time",
                    "reporting should make release risk visible enough for quality gate decisions",
                ],
            ),
            StrategySection(
                heading="## AI Usage Model",
                lines=_ai_usage_lines(data, decisions),
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
                lines=_next_steps_lines(decisions, classifications, data),
            ),
        ]
    )


def _lifecycle_posture_lines(decisions: dict[str, str], classifications: ClassificationResult) -> list[str]:
    shift_left = decisions["shift_left_stance"]
    posture = classifications.get("project_posture", "")
    completeness = classifications.get("information_completeness", "")

    lines = [f"Shift-Left Stance: {shift_left}"]

    if shift_left == "strong":
        lines.append("Shift-Right Stance: monitoring and observability gates after each release from the start")
    else:
        lines.append("Shift-Right Stance: selective where production signals are available")

    if posture == "brownfield":
        lines.append("Prevention vs Detection Balance: detection first to stabilise existing behaviour, then shift prevention forward as coverage matures")
    elif posture == "greenfield":
        lines.append("Prevention vs Detection Balance: prevention-first from day one; embed quality gates before defects can accumulate")
    else:
        lines.append("Prevention vs Detection Balance: prevention first where feasible, detection where legacy or integration risk remains")

    if completeness == "incomplete":
        lines.append("Lifecycle Checkpoints: discovery -> scope confirmation -> design review -> build -> integration -> release readiness")
    else:
        lines.append("Lifecycle Checkpoints: requirements -> design -> build -> integration -> release readiness")

    return lines


def _layered_strategy_lines(decisions: dict[str, str], classifications: ClassificationResult) -> list[str]:
    layering = decisions["layering_priority"]
    system_profile = classifications.get("system_profile", "")
    reg = classifications.get("regulatory_sensitivity", "")

    lines = [
        f"Layering Priority: {layering}",
        f"System Profile: {system_profile}",
    ]

    if layering == "lower_layers_first":
        lines.append("Recommended Coverage Layers: unit and component tests first; integration and API tests before any UI layer; UI automation only after lower layers are stable")
    elif layering == "stabilize_lower_layers_then_ui":
        lines.append("Recommended Coverage Layers: prioritise unit and integration stability; add UI regression only after lower-layer coverage is anchored")
    elif layering == "optimize_and_govern":
        lines.append("Recommended Coverage Layers: maintain existing pyramid; review coverage gaps; retire stale tests; strengthen contract and performance layers")
    else:
        layers = "unit / component / integration / API / UI / regression"
        if system_profile == "api_first":
            layers = "unit / contract / integration / API / end-to-end (minimal UI)"
        elif system_profile == "legacy":
            layers = "characterisation tests / integration / regression / selective UI"
        elif system_profile == "data_heavy":
            layers = "unit / data-pipeline / integration / output-assertion / regression"
        lines.append(f"Recommended Coverage Layers: {layers}")

    if reg == "high":
        lines.append("Compliance Layer: traceability and audit-ready test evidence required at every lifecycle gate")

    return lines


def _cicd_lines(data: dict[str, object], decisions: dict[str, str], classifications: ClassificationResult) -> list[str]:
    ci_cd_maturity = str(data.get("ci_cd_maturity", "unknown"))
    ci_cd_posture = decisions["ci_cd_posture"]
    target_gates = _join_list(data.get("target_quality_gates", []))
    release_freq = classifications.get("release_frequency", "unknown")

    lines = [
        f"Current CI/CD Maturity: {ci_cd_maturity}",
        f"Target CI/CD Posture: {ci_cd_posture}",
        f"Target Quality Gates: {target_gates}",
    ]

    if ci_cd_posture == "pipeline_native":
        lines.append("Pipeline Quality Gates: fast-feedback unit gate -> integration gate -> security scan -> performance baseline -> release approval")
        if release_freq == "high" and ci_cd_maturity not in {"none", "manual"}:
            lines.append("Release Decision Guidance: automated gate results are the primary release signal; manual override requires documented justification")
        elif release_freq == "high":
            lines.append("Release Decision Guidance: build automated gates as immediately as capacity allows; manual sign-off required until pipeline is in place")
        else:
            lines.append("Release Decision Guidance: automated gates combined with QE lead sign-off for each release")
    elif ci_cd_posture == "progressive_gates":
        lines.append("Pipeline Quality Gates: smoke gate on every commit; critical-path regression on merge; full suite before release")
        lines.append("Release Decision Guidance: gate results plus QE lead review before promoting to production")
    else:  # staged_enablement
        if ci_cd_maturity in {"none", "manual"}:
            lines.append("Pipeline Quality Gates: start with smoke gate only; expand as pipeline matures")
            lines.append("Release Decision Guidance: manual QE sign-off supported by test reports until automated gates are in place")
        else:
            lines.append("Pipeline Quality Gates: smoke and critical-path checks currently; scale to risk-based full suite as maturity improves")
            lines.append("Release Decision Guidance: use explicit quality signals rather than subjective judgment alone")

    lines.append("Gate Progression Principle: quality gate scope should expand as delivery maturity improves, not remain static")
    return lines


def _ai_usage_lines(data: dict[str, object], decisions: dict[str, str]) -> list[str]:
    posture = str(data.get("ai_adoption_posture", "unknown"))
    human_review = _join_list(data.get("human_review_expectations", []))
    governance = decisions.get("governance_depth", "medium")

    lines = [f"AI Adoption Posture: {posture}"]

    if posture == "supportive":
        lines.append("Allowed AI Uses: test generation, risk analysis, gap detection, reporting summarization, strategy drafting, exploratory test design")
    elif posture == "restricted":
        lines.append("Allowed AI Uses: internal drafting and summarization only; no AI-generated artefacts in regulated deliverables")
    else:  # cautious or unknown
        lines.append("Allowed AI Uses: drafting, gap detection, reporting summarization, strategy acceleration")

    if governance == "high" or posture == "restricted":
        lines.append("Constrained AI Uses: compliance interpretation, release approval, completeness claims, any artefact requiring regulatory traceability")
    else:
        lines.append("Constrained AI Uses: compliance interpretation, release approval, unsupported completeness claims")

    lines.append(f"Human Review Boundaries: {human_review}")
    return lines


def _next_steps_lines(decisions: dict[str, str], classifications: ClassificationResult, data: dict[str, object]) -> list[str]:
    completeness = classifications.get("information_completeness", "")
    posture = classifications.get("project_posture", "")
    automation = classifications.get("automation_maturity", "")
    ci_cd = classifications.get("ci_cd_maturity", "")

    immediate: list[str] = []
    medium: list[str] = []

    # Immediate actions driven by gaps and maturity
    if completeness == "incomplete":
        immediate.append("run discovery workshops to resolve missing architecture, scope, and requirements before committing to a target state")
    if automation in {"none", "limited"}:
        immediate.append("baseline existing test coverage and identify the highest-value automation candidates")
    if ci_cd in {"none", "manual"}:
        immediate.append("establish a minimal CI pipeline with a smoke gate as the first quality enforcement point")
    if posture == "brownfield":
        immediate.append("audit existing test assets for coverage gaps and retirement candidates before extending automation")
    if not immediate:
        immediate.append("validate current-state evidence and confirm release model and automation baseline")

    # Medium-term
    if posture == "greenfield":
        medium.append("build the test pyramid bottom-up as features stabilise; enforce layer gates in CI/CD from the first sprint")
    elif posture == "brownfield":
        medium.append("stabilise lower-layer coverage, then retire redundant UI tests and introduce contract and performance layers")
    else:
        medium.append("refine layer strategy and target-state automation once discovery evidence improves")

    if decisions.get("governance_depth") == "high":
        medium.append("establish traceability from requirements through to test evidence for all regulated flows")

    medium.append("revisit and update this strategy as delivery context, team maturity, or scope changes")

    immediate_text = "; ".join(immediate)
    medium_text = "; ".join(medium)

    return [
        f"Recommended Immediate Actions: {immediate_text}",
        f"Medium-Term Actions: {medium_text}",
        "Validation Guidance: re-run deterministic checks after each major context change before treating this strategy as a committed delivery position",
    ]


_NFR_APPROACH: dict[str, str] = {
    "performance": "NFR Detail: performance — define SLAs/SLOs, run load and latency tests in CI, establish baselines before release",
    "security": "NFR Detail: security — integrate SAST and SCA in pipeline, DAST on staging, validate auth and data-protection flows",
    "resilience": "NFR Detail: resilience — chaos and fault-injection tests, retry and circuit-breaker validation, degraded-mode coverage",
    "accessibility": "NFR Detail: accessibility — automated WCAG scanning, keyboard and screen-reader coverage, pipeline gate on accessibility failures",
    "compliance": "NFR Detail: compliance — traceability from requirement to test, audit-ready evidence, governance checkpoint at each lifecycle gate",
    "privacy": "NFR Detail: privacy — data masking and anonymisation in test data, PII handling validation, consent-flow coverage",
}
_NFR_FALLBACK = "Non-Functional Priorities: performance, security, accessibility, and resilience where context requires them"


def _nfr_section_lines(data: dict[str, object], decisions: dict[str, str]) -> list[str]:
    """Return NFR output lines for the Test Types section.

    When nfr_depth is 'deep' and named priorities are present, returns one
    concrete approach line per named priority.  Known priorities are expanded
    into specific guidance; unknown ones get a generic line.  When depth is
    'standard' or no priorities are named, returns the single fallback line.
    """
    nfr = data.get("nfr_priorities", [])
    named: list[str] = [str(v).lower() for v in nfr] if isinstance(nfr, list) else []

    if decisions.get("nfr_depth") == "deep" and named:
        # One summary label, then per-priority detail lines with a separate prefix
        summary = f"Non-Functional Priorities: {', '.join(named)}"
        detail_lines: list[str] = []
        for priority in named:
            if priority in _NFR_APPROACH:
                detail_lines.append(_NFR_APPROACH[priority])
            else:
                detail_lines.append(f"NFR Detail: {priority} — define explicit tests and pipeline gates for this concern")
        return [summary, *detail_lines]

    # Standard depth or no named priorities
    if named:
        return [f"Non-Functional Priorities: {', '.join(named)}"]
    return [_NFR_FALLBACK]


def _nfr_priorities_line(data: dict[str, object]) -> str:
    """Single-line NFR summary (kept for backward compatibility; prefer _nfr_section_lines)."""
    nfr = data.get("nfr_priorities", [])
    if isinstance(nfr, list) and nfr:
        return f"Non-Functional Priorities: {', '.join(str(v) for v in nfr)}"
    return _NFR_FALLBACK


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
