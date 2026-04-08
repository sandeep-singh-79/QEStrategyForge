from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_test_strategy_generator.benchmark_runner import run_assertions
from ai_test_strategy_generator.context_classifier import classify_context
from ai_test_strategy_generator.input_loader import InputLoadError, load_input
from ai_test_strategy_generator.output_validator import validate_output
from ai_test_strategy_generator.renderer import render_strategy
from ai_test_strategy_generator.rule_engine import apply_rules
from ai_test_strategy_generator.validators.input_validator import validate_input


def run_benchmark_flow(
    input_path: str | Path,
    assertions_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    try:
        input_package = load_input(input_path)
    except InputLoadError as exc:
        return _result(False, 1, [str(exc)], [], output_path)

    input_validation = validate_input(input_package)
    if not input_validation.is_valid:
        return _result(False, 2, input_validation.errors, [], output_path)

    classifications = classify_context(input_package)
    decisions = apply_rules(classifications)
    markdown = render_strategy(input_package, classifications, decisions)

    output_validation = validate_output(markdown)
    if not output_validation.is_valid:
        return _result(False, 3, output_validation.errors, [], output_path)

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(markdown, encoding="utf-8")

    assertion_result = run_assertions(markdown, assertions_path)
    if not assertion_result.is_valid:
        return _result(False, 4, [], assertion_result.errors, output_file)

    return _result(True, 0, [], [], output_file)


def _result(
    success: bool,
    exit_code: int,
    validation_errors: list[str],
    assertion_errors: list[str],
    output_path: str | Path,
) -> dict[str, Any]:
    return {
        "success": success,
        "exit_code": exit_code,
        "validation_errors": validation_errors,
        "assertion_errors": assertion_errors,
        "output_path": str(output_path),
    }
