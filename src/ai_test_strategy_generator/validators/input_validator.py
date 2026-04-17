from __future__ import annotations

from typing import Any

from ai_test_strategy_generator.models import InputPackage, ValidationResult


REQUIRED_FIELDS = {
    "engagement_name",
    "project_posture",
    "system_type",
    "existing_automation_state",
    "ci_cd_maturity",
    "ai_adoption_posture",
    "strategy_depth",
}

AT_LEAST_ONE_OF = [
    ("business_goal", "quality_goal"),
    ("known_constraints", "delivery_risks"),
]

ENUM_FIELDS = {
    "project_posture": {"greenfield", "brownfield"},
    "existing_automation_state": {"none", "limited", "partial", "strong", "unknown"},
    "ci_cd_maturity": {"none", "manual", "partial", "mature", "unknown"},
    "environment_maturity": {"weak", "moderate", "strong", "unknown"},
    "test_data_maturity": {"weak", "moderate", "strong", "unknown"},
    "ai_adoption_posture": {"supportive", "cautious", "restricted", "unknown"},
    "strategy_depth": {"light", "standard", "detailed"},
}

# Optional fields that are validated when present but not required.
OPTIONAL_ENUM_FIELDS = {
    "release_cadence": {"continuous", "weekly", "fortnightly", "monthly", "quarterly", "unknown"},
    "qe_capacity": {"small", "medium", "large", "unknown"},
    "reporting_audience": {"engineering", "management", "executive", "mixed", "unknown"},
}


def validate_input(input_package: InputPackage) -> ValidationResult:
    data = input_package.normalized
    errors: list[str] = []

    for field_name in sorted(REQUIRED_FIELDS):
        if _is_missing(data.get(field_name)):
            errors.append(f"Missing required field: {field_name}")

    for left, right in AT_LEAST_ONE_OF:
        if _is_missing(data.get(left)) and _is_missing(data.get(right)):
            errors.append(f"At least one of '{left}' or '{right}' must be provided.")

    for field_name, allowed_values in ENUM_FIELDS.items():
        value = data.get(field_name)
        if _is_missing(value):
            continue
        if not isinstance(value, str):
            errors.append(f"Field '{field_name}' must be a string.")
            continue
        if value not in allowed_values:
            allowed = ", ".join(sorted(allowed_values))
            errors.append(f"Field '{field_name}' must be one of: {allowed}")

    for field_name, allowed_values in OPTIONAL_ENUM_FIELDS.items():
        value = data.get(field_name)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            continue  # absent optional fields are fine
        if not isinstance(value, str):
            errors.append(f"Field '{field_name}' must be a string.")
            continue
        if value not in allowed_values:
            allowed = ", ".join(sorted(allowed_values))
            errors.append(f"Field '{field_name}' must be one of: {allowed}")

    return ValidationResult(is_valid=not errors, errors=errors)


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return len(value) == 0
    return False
