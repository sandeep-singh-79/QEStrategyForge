from __future__ import annotations

from ai_test_strategy_generator.models import ClassificationResult


def apply_rules(classifications: ClassificationResult) -> dict[str, str]:
    project_posture = classifications.get("project_posture", "")
    automation_maturity = classifications.get("automation_maturity", "")
    ci_cd_maturity = classifications.get("ci_cd_maturity", "")
    system_profile = classifications.get("system_profile", "")
    regulatory_sensitivity = classifications.get("regulatory_sensitivity", "")
    information_completeness = classifications.get("information_completeness", "")
    release_frequency = classifications.get("release_frequency", "unknown")

    result = {
        "shift_left_stance": "moderate",
        "layering_priority": "balanced",
        "brownfield_transition_strategy": "not_applicable",
        "automation_adoption_path": "phased_expansion",
        "ci_cd_posture": "staged_enablement",
        "governance_depth": "medium",
        "reporting_emphasis": "medium",
        "assumption_mode": "normal",
        "strategy_confidence": "standard",
        "nfr_depth": "standard",
    }

    if project_posture == "greenfield":
        result["shift_left_stance"] = "strong"
        result["layering_priority"] = "lower_layers_first"
        result["brownfield_transition_strategy"] = "not_applicable"

    if project_posture == "brownfield":
        result["brownfield_transition_strategy"] = "assess_reuse_stabilize_retire_replace"

    if automation_maturity == "none":
        result["automation_adoption_path"] = "foundation_first"
    elif automation_maturity in {"limited", "partial"}:
        result["automation_adoption_path"] = "phased_expansion"
    elif automation_maturity == "strong":
        result["automation_adoption_path"] = "optimize_and_govern"
        result["reporting_emphasis"] = "high"
        if project_posture != "greenfield":
            result["layering_priority"] = "optimize_and_govern"

    if ci_cd_maturity in {"none", "manual", "unknown"}:
        result["ci_cd_posture"] = "staged_enablement"
    elif ci_cd_maturity == "partial":
        result["ci_cd_posture"] = "progressive_gates"
    elif ci_cd_maturity == "mature":
        result["ci_cd_posture"] = "pipeline_native"

    if system_profile == "legacy":
        result["layering_priority"] = "stabilize_lower_layers_then_ui"
    elif system_profile == "api_first" and project_posture == "greenfield":
        result["layering_priority"] = "lower_layers_first"

    if regulatory_sensitivity == "high":
        result["governance_depth"] = "high"
    elif regulatory_sensitivity == "low":
        result["governance_depth"] = "light"

    if information_completeness == "incomplete":
        result["assumption_mode"] = "explicit"
        result["strategy_confidence"] = "conditional"
    elif information_completeness == "partial":
        result["assumption_mode"] = "explicit"

    if classifications.get("nfr_priority") == "high":
        result["nfr_depth"] = "deep"

    if release_frequency == "high":
        result["ci_cd_posture"] = "pipeline_native"
        result["reporting_emphasis"] = "high"
    elif release_frequency == "low":
        if result["ci_cd_posture"] == "staged_enablement":
            result["ci_cd_posture"] = "staged_enablement"  # keep, but note low cadence

    return result
