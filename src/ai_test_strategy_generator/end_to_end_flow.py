from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_test_strategy_generator.benchmark_runner import run_assertions
from ai_test_strategy_generator.context_classifier import classify_context
from ai_test_strategy_generator.input_loader import InputLoadError, load_input
from ai_test_strategy_generator.models import (
    EXIT_ASSERTIONS_FAILED,
    EXIT_INPUT_INVALID,
    EXIT_LOAD_ERROR,
    EXIT_OUTPUT_INVALID,
    EXIT_SUCCESS,
    FlowResult,
    InputPackage,
    make_flow_result,
)
from ai_test_strategy_generator.output_validator import validate_output
from ai_test_strategy_generator.renderer import render_strategy
from ai_test_strategy_generator.rule_engine import apply_rules
from ai_test_strategy_generator.validators.input_validator import validate_input


def run_benchmark_flow(
    input_path: str | Path,
    assertions_path: str | Path,
    output_path: str | Path,
) -> FlowResult:
    try:
        input_package = load_input(input_path)
    except InputLoadError as exc:
        return make_flow_result(False, EXIT_LOAD_ERROR, [str(exc)], [], output_path)

    return run_input_package_flow(input_package, assertions_path, output_path)


def run_input_package_flow(
    input_package: InputPackage,
    assertions_path: str | Path,
    output_path: str | Path,
) -> FlowResult:
    input_validation = validate_input(input_package)
    if not input_validation.is_valid:
        return make_flow_result(False, EXIT_INPUT_INVALID, input_validation.errors, [], output_path)

    classifications = classify_context(input_package)
    decisions = apply_rules(classifications)
    markdown = render_strategy(input_package, classifications, decisions)

    output_validation = validate_output(markdown)
    if not output_validation.is_valid:
        return make_flow_result(False, EXIT_OUTPUT_INVALID, output_validation.errors, [], output_path)

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(markdown, encoding="utf-8")

    assertion_result = run_assertions(markdown, assertions_path)
    if not assertion_result.is_valid:
        return make_flow_result(False, EXIT_ASSERTIONS_FAILED, [], assertion_result.errors, output_file)

    return make_flow_result(True, EXIT_SUCCESS, [], [], output_file)
