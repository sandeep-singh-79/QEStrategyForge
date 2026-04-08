from __future__ import annotations

from pathlib import Path

from ai_test_strategy_generator.input_loader import InputLoadError, load_input
from ai_test_strategy_generator.validators.input_validator import validate_input


def run_validation(input_path: str | Path) -> int:
    try:
        input_package = load_input(input_path)
    except InputLoadError as exc:
        print(f"LOAD FAIL: {exc}")
        return 1

    result = validate_input(input_package)
    if not result.is_valid:
        print("VALIDATION FAIL")
        for error in result.errors:
            print(f"- {error}")
        return 2

    print("VALIDATION PASS")
    print(f"Input: {input_package.source_path}")
    print(f"Project Posture: {input_package.normalized['project_posture']}")
    print(f"Current Automation State: {input_package.normalized['existing_automation_state']}")
    print(f"Current CI/CD Maturity: {input_package.normalized['ci_cd_maturity']}")
    return 0
