from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder
from ai_test_strategy_generator.artifact_mapping import ArtifactMappingError, map_artifact_bundle
from ai_test_strategy_generator.benchmark_runner import run_assertions
from ai_test_strategy_generator.context_classifier import classify_context
from ai_test_strategy_generator.input_loader import InputLoadError, load_input
from ai_test_strategy_generator.llm_client import GenerationRequest, LLMClient
from ai_test_strategy_generator.models import (
    EXIT_ASSERTIONS_FAILED,
    EXIT_INPUT_INVALID,
    EXIT_LOAD_ERROR,
    EXIT_OUTPUT_INVALID,
    EXIT_SUCCESS,
    FlowResult,
    InputPackage,
    LLMConfig,
    make_flow_result,
)
from ai_test_strategy_generator.output_validator import (
    REQUIRED_HEADINGS,
    REQUIRED_LABELS,
    validate_output,
)
from ai_test_strategy_generator.prompt_builder import build_prompt
from ai_test_strategy_generator.renderer import render_strategy
from ai_test_strategy_generator.rule_engine import apply_rules
from ai_test_strategy_generator.validators.input_validator import validate_input

_log = logging.getLogger(__name__)


def run_llm_artifact_benchmark_flow(
    artifact_folder_path: str | Path,
    assertions_path: str | Path,
    output_path: str | Path,
    llm_config: LLMConfig,
    llm_client: LLMClient,
) -> FlowResult:
    """Load artifact folder and run the LLM-assisted strategy generation flow."""
    try:
        artifact_bundle = load_artifact_folder(artifact_folder_path)
    except ArtifactLoadError as exc:
        return make_flow_result(False, EXIT_LOAD_ERROR, [str(exc)], [], output_path)

    try:
        input_package = map_artifact_bundle(artifact_bundle)
    except ArtifactMappingError as exc:
        return make_flow_result(False, EXIT_INPUT_INVALID, [str(exc)], [], output_path)

    return run_llm_input_package_flow(
        input_package, assertions_path, output_path, llm_config, llm_client
    )


def run_llm_benchmark_flow(
    input_path: str | Path,
    assertions_path: str | Path,
    output_path: str | Path,
    llm_config: LLMConfig,
    llm_client: LLMClient,
) -> FlowResult:
    """Load input from file and run the LLM-assisted strategy generation flow."""
    try:
        input_package = load_input(input_path)
    except InputLoadError as exc:
        return make_flow_result(False, EXIT_LOAD_ERROR, [str(exc)], [], output_path)

    return run_llm_input_package_flow(
        input_package, assertions_path, output_path, llm_config, llm_client
    )


def run_llm_input_package_flow(
    input_package: InputPackage,
    assertions_path: str | Path,
    output_path: str | Path,
    llm_config: LLMConfig,
    llm_client: LLMClient,
) -> FlowResult:
    """Run the LLM-assisted strategy generation flow from a pre-loaded InputPackage."""
    input_validation = validate_input(input_package)
    if not input_validation.is_valid:
        return make_flow_result(False, EXIT_INPUT_INVALID, input_validation.errors, [], output_path)

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
    _log.debug("LLM call starting: model=%s max_tokens=%d", llm_config.model, llm_config.max_tokens)
    try:
        response = llm_client.generate(request)
        markdown = response.text
        _log.debug("LLM call succeeded: response_length=%d chars", len(markdown))
    except RuntimeError as exc:
        _log.warning("LLM call failed (%s); triggering repair chain", exc)
        markdown = ""  # empty string will fail validate_output → triggers repair chain

    repair_stats: dict[str, object] = {
        "source": "llm",
        "headings_injected": 0,
        "labels_injected": 0,
        "total_headings": len(REQUIRED_HEADINGS),
        "total_labels": len(REQUIRED_LABELS),
    }

    # Validate; attempt constrained repair if structurally invalid
    output_validation = validate_output(markdown)
    if not output_validation.is_valid:
        _log.info(
            "LLM output failed structural validation (%d errors); attempting repair",
            len(output_validation.errors),
        )
        markdown, repair_counts = _repair_output(markdown, input_package.normalized, decisions)
        repair_stats.update(repair_counts)
        repair_stats["source"] = "repair"
        output_validation = validate_output(markdown)
        if output_validation.is_valid:
            _log.info(
                "Repair succeeded; injected %d headings, %d labels",
                repair_counts["headings_injected"], repair_counts["labels_injected"],
            )
        else:
            _log.warning(
                "Repair did not resolve all issues (%d errors remain); falling back to deterministic renderer",
                len(output_validation.errors),
            )

    # If still invalid after repair, fall back to deterministic renderer
    if not output_validation.is_valid:
        markdown = render_strategy(input_package, classifications, decisions)
        output_validation = validate_output(markdown)
        repair_stats["source"] = "deterministic"
        _log.info("Deterministic fallback used")

    if not output_validation.is_valid:
        _log.error("All fallbacks exhausted; output structurally invalid (exit %d)", EXIT_OUTPUT_INVALID)
        return make_flow_result(False, EXIT_OUTPUT_INVALID, output_validation.errors, [], output_path, repair_stats)

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(markdown, encoding="utf-8")

    assertion_result = run_assertions(markdown, assertions_path)
    if not assertion_result.is_valid:
        _log.warning(
            "Benchmark assertions failed (%d); output written to %s",
            len(assertion_result.errors), output_file,
        )
        return make_flow_result(False, EXIT_ASSERTIONS_FAILED, [], assertion_result.errors, output_file, repair_stats)

    _log.info("LLM flow completed successfully; output written to %s", output_file)
    return make_flow_result(True, EXIT_SUCCESS, [], [], output_file, repair_stats)


def _repair_output(
    markdown: str,
    input_data: dict[str, Any] | None = None,
    decisions: dict[str, str] | None = None,
) -> tuple[str, dict[str, int]]:
    """One constrained repair pass: append any missing required headings and labels.

    Returns a tuple of (repaired_markdown, repair_counts) where repair_counts has
    keys 'headings_injected' and 'labels_injected'.
    """
    existing_lines = markdown.splitlines()
    lines = list(existing_lines)
    headings_injected = 0
    labels_injected = 0

    # Use line-anchored checks so that "### Foo" does not satisfy "## Foo".
    present_headings = {line.strip() for line in existing_lines}
    for heading in REQUIRED_HEADINGS:
        if heading not in present_headings:
            lines.append("")
            lines.append(heading)
            lines.append("Not specified in engagement context.")
            headings_injected += 1

    label_values = _build_label_values(input_data, decisions)
    for label in REQUIRED_LABELS:
        if not any(line.strip().startswith(label) for line in existing_lines):
            value = label_values.get(label, "not specified")
            lines.append(f"{label} {value}")
            labels_injected += 1

    # Conditional: add brownfield transition line only when applicable
    if decisions:
        transition = decisions.get("brownfield_transition_strategy", "not_applicable")
        bt_label = "Brownfield Transition Strategy:"
        if transition != "not_applicable" and not any(
            line.strip().startswith(bt_label) for line in existing_lines
        ):
            lines.append(f"{bt_label} {transition}")

    return "\n".join(lines), {"headings_injected": headings_injected, "labels_injected": labels_injected}


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
