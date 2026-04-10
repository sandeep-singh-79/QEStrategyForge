from __future__ import annotations

from pathlib import Path

from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder
from ai_test_strategy_generator.artifact_mapping import ArtifactMappingError, map_artifact_bundle
from ai_test_strategy_generator.end_to_end_flow import run_input_package_flow
from ai_test_strategy_generator.models import (
    EXIT_INPUT_INVALID,
    EXIT_LOAD_ERROR,
    FlowResult,
    make_flow_result,
)


def run_artifact_benchmark_flow(
    artifact_folder_path: str | Path,
    assertions_path: str | Path,
    output_path: str | Path,
) -> FlowResult:
    try:
        artifact_bundle = load_artifact_folder(artifact_folder_path)
    except ArtifactLoadError as exc:
        return make_flow_result(False, EXIT_LOAD_ERROR, [str(exc)], [], output_path)

    try:
        input_package = map_artifact_bundle(artifact_bundle)
    except ArtifactMappingError as exc:
        return make_flow_result(False, EXIT_INPUT_INVALID, [str(exc)], [], output_path)

    return run_input_package_flow(input_package, assertions_path, output_path)
