from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_test_strategy_generator.input_loader import LIST_FIELDS, _normalize
from ai_test_strategy_generator.models import ArtifactBundle, ArtifactDocument, InputPackage


MARKDOWN_SCALAR_FIELD_MAP = {
    "Delivery Model": "delivery_model",
    "Timeline Pressure": "timeline_pressure",
    "Business Goal": "business_goal",
    "Quality Goal": "quality_goal",
    "Release Expectation": "release_expectation",
    "Primary Audience": "primary_audience",
    "System Type": "system_type",
    "Platform Notes": "platform_notes",
    "Existing Test Process": "existing_test_process",
    "Existing Automation State": "existing_automation_state",
    "CI/CD Maturity": "ci_cd_maturity",
    "Environment Maturity": "environment_maturity",
    "Test Data Maturity": "test_data_maturity",
    "Requirements Available": "requirements_available",
    "API Docs Available": "api_docs_available",
    "Existing Test Cases Available": "existing_test_cases_available",
    "Automation Assets Available": "automation_assets_available",
    "Production Or Operational Feedback Available": "production_or_operational_feedback_available",
    "AI Adoption Posture": "ai_adoption_posture",
    "Strategy Depth": "strategy_depth",
}

MARKDOWN_LIST_FIELD_MAP = {
    "Critical Business Flows": "critical_business_flows",
    "Applications In Scope": "applications_in_scope",
    "Key Integrations": "key_integrations",
    "Known Constraints": "known_constraints",
    "Regulatory Or Compliance Needs": "regulatory_or_compliance_needs",
    "Delivery Risks": "delivery_risks",
    "Missing Information": "missing_information",
    "AI Governance Constraints": "ai_governance_constraints",
    "Human Review Expectations": "human_review_expectations",
}


class ArtifactMappingError(Exception):
    """Raised when artifact content cannot be mapped deterministically."""


def map_artifact_bundle(bundle: ArtifactBundle) -> InputPackage:
    merged: dict[str, Any] = {
        "engagement_name": bundle.manifest.engagement_name,
        "domain": bundle.manifest.domain,
        "project_posture": bundle.manifest.project_posture,
    }

    for document in bundle.documents:
        partial = _map_document(document)
        _merge_partial(merged, partial)

    _merge_partial(merged, bundle.manifest.overrides, allow_override=True)
    normalized = _normalize(merged)
    return InputPackage(source_path=bundle.manifest.source_path, raw={"artifacts": []}, normalized=normalized)


def _map_document(document: ArtifactDocument) -> dict[str, Any]:
    if document.format == "md":
        if not isinstance(document.content, str):
            raise ArtifactMappingError(f"Markdown artifact must contain text content: {document.path}")
        return _map_markdown_document(document.content)
    if document.format in {"yaml", "json"}:
        if not isinstance(document.content, dict):
            raise ArtifactMappingError(f"Structured artifact must contain mapping content: {document.path}")
        return dict(document.content)

    raise ArtifactMappingError(f"Unsupported artifact document format: {document.format}")


def _map_markdown_document(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    lines = [line.rstrip() for line in text.splitlines()]
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue

        if ":" in line:
            label, value = line.split(":", 1)
            label = label.strip()
            value = value.strip()
            if label in MARKDOWN_SCALAR_FIELD_MAP and value:
                result[MARKDOWN_SCALAR_FIELD_MAP[label]] = value
                index += 1
                continue
            if label in MARKDOWN_LIST_FIELD_MAP:
                values: list[str] = []
                if value:
                    values.append(value)
                index += 1
                while index < len(lines) and lines[index].strip().startswith("- "):
                    values.append(lines[index].strip()[2:].strip())
                    index += 1
                result[MARKDOWN_LIST_FIELD_MAP[label]] = values
                continue

        index += 1

    return result


def _merge_partial(target: dict[str, Any], partial: dict[str, Any], allow_override: bool = False) -> None:
    for key, value in partial.items():
        if key not in target or _is_empty(target[key]):
            target[key] = value
            continue

        existing = target[key]
        if key in LIST_FIELDS:
            target[key] = _merge_lists(existing, value)
            continue

        if allow_override:
            target[key] = value
            continue

        if existing != value:
            raise ArtifactMappingError(f"Conflicting values detected for field '{key}'.")


def _merge_lists(existing: Any, incoming: Any) -> list[Any]:
    existing_list = existing if isinstance(existing, list) else [existing]
    incoming_list = incoming if isinstance(incoming, list) else [incoming]
    merged: list[Any] = []
    for value in existing_list + incoming_list:
        if value not in merged:
            merged.append(value)
    return merged


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return len(value) == 0
    return False
