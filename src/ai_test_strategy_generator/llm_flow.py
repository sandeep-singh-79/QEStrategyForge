from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder
from ai_test_strategy_generator.artifact_mapping import ArtifactMappingError, map_artifact_bundle
from ai_test_strategy_generator.benchmark_runner import run_assertions
from ai_test_strategy_generator.context_classifier import classify_context
from ai_test_strategy_generator.input_loader import InputLoadError, load_input
from ai_test_strategy_generator.llm_client import GenerationRequest, LLMClient
from ai_test_strategy_generator.models import InputPackage, LLMConfig
from ai_test_strategy_generator.output_validator import (
    REQUIRED_HEADINGS,
    REQUIRED_LABELS,
    validate_output,
)
from ai_test_strategy_generator.prompt_builder import build_prompt
from ai_test_strategy_generator.renderer import render_strategy
from ai_test_strategy_generator.rule_engine import apply_rules
from ai_test_strategy_generator.validators.input_validator import validate_input


def run_llm_artifact_benchmark_flow(
    artifact_folder_path: str | Path,
    assertions_path: str | Path,
    output_path: str | Path,
    llm_config: LLMConfig,
    llm_client: LLMClient,
) -> dict[str, Any]:
    """Load artifact folder and run the LLM-assisted strategy generation flow."""
    try:
        artifact_bundle = load_artifact_folder(artifact_folder_path)
    except ArtifactLoadError as exc:
        return _result(False, 1, [str(exc)], [], output_path)

    try:
        input_package = map_artifact_bundle(artifact_bundle)
    except ArtifactMappingError as exc:
        return _result(False, 2, [str(exc)], [], output_path)

    return run_llm_input_package_flow(
        input_package, assertions_path, output_path, llm_config, llm_client
    )


def run_llm_benchmark_flow(
    input_path: str | Path,
    assertions_path: str | Path,
    output_path: str | Path,
    llm_config: LLMConfig,
    llm_client: LLMClient,
) -> dict[str, Any]:
    """Load input from file and run the LLM-assisted strategy generation flow."""
    try:
        input_package = load_input(input_path)
    except InputLoadError as exc:
        return _result(False, 1, [str(exc)], [], output_path)

    return run_llm_input_package_flow(
        input_package, assertions_path, output_path, llm_config, llm_client
    )


def run_llm_input_package_flow(
    input_package: InputPackage,
    assertions_path: str | Path,
    output_path: str | Path,
    llm_config: LLMConfig,
    llm_client: LLMClient,
) -> dict[str, Any]:
    """Run the LLM-assisted strategy generation flow from a pre-loaded InputPackage."""
    input_validation = validate_input(input_package)
    if not input_validation.is_valid:
        return _result(False, 2, input_validation.errors, [], output_path)

    classifications = classify_context(input_package)
    decisions = apply_rules(classifications)

    # Build prompt and call LLM; RuntimeError (timeout, network, bad response)
    # triggers the same repair → deterministic fallback chain.
    prompt = build_prompt(input_package, classifications, decisions)
    request = GenerationRequest(
        prompt=prompt,
        model=llm_config.model,
        max_tokens=llm_config.max_tokens,
    )
    try:
        response = llm_client.generate(request)
        markdown = response.text
    except RuntimeError:
        markdown = ""  # empty string will fail validate_output → triggers repair chain

    # Validate; attempt constrained repair if structurally invalid
    output_validation = validate_output(markdown)
    if not output_validation.is_valid:
        markdown = _repair_output(markdown, input_package.normalized, decisions)
        output_validation = validate_output(markdown)

    # If still invalid after repair, fall back to deterministic renderer
    if not output_validation.is_valid:
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


def _repair_output(
    markdown: str,
    input_data: dict[str, Any] | None = None,
    decisions: dict[str, str] | None = None,
) -> str:
    """One constrained repair pass: append any missing required headings and labels."""
    lines = list(markdown.splitlines())

    for heading in REQUIRED_HEADINGS:
        if heading not in markdown:
            lines.append("")
            lines.append(heading)
            lines.append("Not specified in engagement context.")

    label_values = _build_label_values(input_data, decisions)
    for label in REQUIRED_LABELS:
        if label not in markdown:
            value = label_values.get(label, "not specified")
            lines.append(f"{label} {value}")

    # Conditional: add brownfield transition line only when applicable
    if decisions:
        transition = decisions.get("brownfield_transition_strategy", "not_applicable")
        if transition != "not_applicable" and "Brownfield Transition Strategy:" not in markdown:
            lines.append(f"Brownfield Transition Strategy: {transition}")

    return "\n".join(lines)


def _build_label_values(
    input_data: dict[str, Any] | None,
    decisions: dict[str, str] | None,
) -> dict[str, str]:
    """Build a mapping from required label prefix to its actual value."""
    if not input_data:
        return {}

    def _join_list(items: Any) -> str:
        if isinstance(items, list) and items:
            return ", ".join(str(i) for i in items)
        return str(items) if items else "none"

    d = decisions or {}
    return {
        "Project Posture:": str(input_data.get("project_posture", "not specified")),
        "Delivery Model:": str(input_data.get("delivery_model", "not specified")),
        "System Type:": str(input_data.get("system_type", "not specified")),
        "Current Automation State:": str(input_data.get("existing_automation_state", "not specified")),
        "Target Automation State:": str(input_data.get("target_automation_state", "not specified")),
        "Current CI/CD Maturity:": str(input_data.get("ci_cd_maturity", "not specified")),
        "Target CI/CD Posture:": d.get("ci_cd_posture", "not specified"),
        "AI Adoption Posture:": str(input_data.get("ai_adoption_posture", "not specified")),
        "Human Review Boundaries:": _join_list(input_data.get("human_review_expectations", [])),
        "Missing Information:": _join_list(input_data.get("missing_information", [])),
        "Shift-Left Stance:": d.get("shift_left_stance", "not specified"),
        "Layering Priority:": d.get("layering_priority", "not specified"),
        "Automation Adoption Path:": d.get("automation_adoption_path", "not specified"),
        "Governance Depth:": d.get("governance_depth", "not specified"),
        "Reporting Emphasis:": d.get("reporting_emphasis", "not specified"),
        "Assumption Mode:": d.get("assumption_mode", "not specified"),
        "Strategy Confidence:": d.get("strategy_confidence", "not specified"),
        "Recommended Immediate Actions:": "validate current-state evidence and confirm scope",
    }


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
