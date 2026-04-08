from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ai_test_strategy_generator.models import ValidationResult


class AssertionLoadError(Exception):
    """Raised when benchmark assertion files cannot be loaded."""


def run_assertions(markdown: str, assertions_path: str | Path) -> ValidationResult:
    assertions = _load_assertions(assertions_path)
    errors: list[str] = []

    for heading in assertions.get("must_include_headings", []):
        if heading not in markdown:
            errors.append(f"Missing required heading: {heading}")

    for label in assertions.get("must_include_labels", []):
        if label not in markdown:
            errors.append(f"Missing required label: {label}")

    for substring in assertions.get("must_include_substrings", []):
        if substring not in markdown:
            errors.append(f"Missing required substring: {substring}")

    for substring in assertions.get("must_not_include_substrings", []):
        if substring in markdown:
            errors.append(f"Forbidden substring present: {substring}")

    return ValidationResult(is_valid=not errors, errors=errors)


def _load_assertions(assertions_path: str | Path) -> dict[str, list[str]]:
    path = Path(assertions_path)
    if not path.exists():
        raise AssertionLoadError(f"Assertions file not found: {path}")

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise AssertionLoadError(f"Assertions YAML parsing failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise AssertionLoadError("Assertions file must contain a mapping/object.")

    return {
        "must_include_headings": _normalize_str_list(data.get("must_include_headings")),
        "must_include_labels": _normalize_str_list(data.get("must_include_labels")),
        "must_include_substrings": _normalize_str_list(data.get("must_include_substrings")),
        "must_not_include_substrings": _normalize_str_list(data.get("must_not_include_substrings")),
    }


def _normalize_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]
