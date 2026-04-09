from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder
from ai_test_strategy_generator.artifact_mapping import ArtifactMappingError, map_artifact_bundle
from ai_test_strategy_generator.end_to_end_flow import run_input_package_flow


def run_artifact_benchmark_flow(
    artifact_folder_path: str | Path,
    assertions_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    try:
        artifact_bundle = load_artifact_folder(artifact_folder_path)
    except ArtifactLoadError as exc:
        return _result(False, 1, [str(exc)], [], output_path)

    try:
        input_package = map_artifact_bundle(artifact_bundle)
    except ArtifactMappingError as exc:
        return _result(False, 2, [str(exc)], [], output_path)

    return run_input_package_flow(input_package, assertions_path, output_path)


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
