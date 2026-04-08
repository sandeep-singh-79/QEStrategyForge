from __future__ import annotations

from ai_test_strategy_generator.models import ClassificationResult, InputPackage


REGULATED_DOMAINS = {"insurance", "banking", "healthcare", "fintech"}
MEDIUM_REGULATORY_TERMS = {"privacy", "audit", "compliance", "security"}


def classify_context(input_package: InputPackage) -> ClassificationResult:
    data = input_package.normalized
    return {
        "project_posture": _as_text(data.get("project_posture")),
        "automation_maturity": _as_text(data.get("existing_automation_state")),
        "ci_cd_maturity": _as_text(data.get("ci_cd_maturity")),
        "system_profile": _classify_system_profile(_as_text(data.get("system_type"))),
        "regulatory_sensitivity": _classify_regulatory_sensitivity(
            _as_text(data.get("domain")),
            data.get("regulatory_or_compliance_needs", []),
        ),
        "information_completeness": _classify_information_completeness(data),
    }


def _classify_system_profile(system_type: str) -> str:
    lowered = system_type.lower()
    if "api" in lowered or "microservices" in lowered or "service" in lowered:
        return "api_first"
    if "legacy" in lowered:
        return "legacy"
    if "ui" in lowered:
        return "ui_heavy"
    if "data" in lowered:
        return "data_heavy"
    return "general"


def _classify_regulatory_sensitivity(domain: str, controls: list[str]) -> str:
    lowered_domain = domain.lower()
    if lowered_domain in REGULATED_DOMAINS:
        return "high"

    joined_controls = " ".join(controls).lower()
    if any(term in joined_controls for term in MEDIUM_REGULATORY_TERMS):
        return "medium"

    return "low"


def _classify_information_completeness(data: dict[str, object]) -> str:
    unknown_count = sum(
        1
        for field_name in (
            "existing_automation_state",
            "ci_cd_maturity",
            "environment_maturity",
            "test_data_maturity",
        )
        if _as_text(data.get(field_name)) == "unknown"
    )
    missing_info = data.get("missing_information", [])
    missing_count = len(missing_info) if isinstance(missing_info, list) else 0

    if unknown_count >= 3 or missing_count >= 3:
        return "incomplete"
    if unknown_count >= 1 or missing_count >= 1:
        return "partial"
    return "sufficient"


def _as_text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""
