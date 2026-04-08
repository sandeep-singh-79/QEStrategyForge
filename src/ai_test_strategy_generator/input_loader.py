from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ai_test_strategy_generator.models import InputPackage


LIST_FIELDS = {
    "critical_business_flows",
    "applications_in_scope",
    "key_integrations",
    "known_constraints",
    "regulatory_or_compliance_needs",
    "delivery_risks",
    "missing_information",
    "ai_governance_constraints",
    "human_review_expectations",
}


class InputLoadError(Exception):
    """Raised when an input file cannot be loaded."""


def load_input(input_path: str | Path) -> InputPackage:
    path = Path(input_path)
    if not path.exists():
        raise InputLoadError(f"Input file not found: {path}")
    if path.suffix.lower() not in {".yaml", ".yml"}:
        raise InputLoadError(f"Unsupported input file type: {path.suffix}")

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise InputLoadError(f"YAML parsing failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise InputLoadError("Top-level YAML content must be a mapping/object.")

    normalized = _normalize(data)
    return InputPackage(source_path=path, raw=data, normalized=normalized)


def _normalize(data: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(data)
    for field_name in LIST_FIELDS:
        value = normalized.get(field_name)
        if value is None:
            normalized[field_name] = []
        elif isinstance(value, list):
            normalized[field_name] = value
        else:
            normalized[field_name] = [value]
    return normalized
