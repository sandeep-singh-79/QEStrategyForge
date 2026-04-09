from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from ai_test_strategy_generator.models import (
    ArtifactBundle,
    ArtifactDocument,
    ArtifactManifest,
    ArtifactReference,
)


SUPPORTED_FILE_TYPES = {".md", ".yaml", ".yml", ".json"}
SUPPORTED_ARTIFACT_TYPES = {
    "project_summary",
    "requirements_summary",
    "system_landscape",
    "api_summary",
    "current_test_state",
}
SUPPORTED_PROJECT_POSTURES = {"greenfield", "brownfield"}
REQUIRED_MANIFEST_FIELDS = {"engagement_name", "domain", "project_posture", "artifacts"}


class ArtifactLoadError(Exception):
    """Raised when an artifact folder cannot be loaded deterministically."""


def load_artifact_folder(folder_path: str | Path) -> ArtifactBundle:
    root_path = Path(folder_path)
    if not root_path.exists() or not root_path.is_dir():
        raise ArtifactLoadError(f"Artifact folder not found: {root_path}")
    root_path = root_path.resolve()

    manifest_path = _resolve_manifest_path(root_path)
    manifest_data = _load_yaml_mapping(manifest_path, "manifest")
    manifest = _build_manifest(manifest_path, manifest_data)
    documents = [_load_artifact_document(root_path, reference) for reference in manifest.artifacts]
    return ArtifactBundle(root_path=root_path, manifest=manifest, documents=documents)


def _resolve_manifest_path(root_path: Path) -> Path:
    for candidate_name in ("manifest.yaml", "manifest.yml"):
        candidate_path = root_path / candidate_name
        if candidate_path.exists():
            return candidate_path
    raise ArtifactLoadError(f"Artifact manifest not found in folder: {root_path}")


def _build_manifest(manifest_path: Path, manifest_data: dict[str, Any]) -> ArtifactManifest:
    missing_fields = sorted(field for field in REQUIRED_MANIFEST_FIELDS if field not in manifest_data)
    if missing_fields:
        raise ArtifactLoadError(f"Manifest is missing required fields: {', '.join(missing_fields)}")

    artifacts_data = manifest_data.get("artifacts")
    if not isinstance(artifacts_data, list):
        raise ArtifactLoadError("Manifest artifacts field must be a list.")
    if not artifacts_data:
        raise ArtifactLoadError("Manifest must declare at least one artifact.")

    overrides = manifest_data.get("overrides", {})
    if overrides is None:
        overrides = {}
    if not isinstance(overrides, dict):
        raise ArtifactLoadError("Manifest overrides field must be a mapping/object when present.")

    artifact_references: list[ArtifactReference] = []
    seen_types: set[str] = set()
    for item in artifacts_data:
        artifact_reference = _build_artifact_reference(item)
        if artifact_reference.artifact_type in seen_types:
            raise ArtifactLoadError(f"Duplicate artifact type declared in manifest: {artifact_reference.artifact_type}")
        seen_types.add(artifact_reference.artifact_type)
        artifact_references.append(artifact_reference)

    project_posture = _require_non_blank_string(manifest_data, "project_posture", "manifest")
    if project_posture not in SUPPORTED_PROJECT_POSTURES:
        raise ArtifactLoadError(
            "Invalid project_posture in manifest. Supported values are: brownfield, greenfield."
        )

    return ArtifactManifest(
        source_path=manifest_path,
        engagement_name=_require_non_blank_string(manifest_data, "engagement_name", "manifest"),
        domain=_require_non_blank_string(manifest_data, "domain", "manifest"),
        project_posture=project_posture,
        artifacts=artifact_references,
        overrides=overrides,
    )


def _build_artifact_reference(item: object) -> ArtifactReference:
    if not isinstance(item, dict):
        raise ArtifactLoadError("Each manifest artifact entry must be a mapping/object.")

    artifact_type = _require_non_blank_string(item, "type", "artifact entry")
    relative_path = _require_non_blank_string(item, "path", "artifact entry")
    if artifact_type not in SUPPORTED_ARTIFACT_TYPES:
        raise ArtifactLoadError(f"Unsupported artifact type declared in manifest: {artifact_type}")

    path = Path(relative_path)
    if path.suffix.lower() not in SUPPORTED_FILE_TYPES:
        raise ArtifactLoadError(f"Unsupported artifact file type: {path.suffix}")

    return ArtifactReference(artifact_type=artifact_type, path=path)


def _load_artifact_document(root_path: Path, reference: ArtifactReference) -> ArtifactDocument:
    artifact_path = (root_path / reference.path).resolve()
    if not artifact_path.is_relative_to(root_path):
        raise ArtifactLoadError(f"Referenced artifact path points outside the artifact folder: {reference.path}")
    if not artifact_path.exists():
        raise ArtifactLoadError(f"Referenced artifact file not found: {artifact_path}")
    if not artifact_path.is_file():
        raise ArtifactLoadError(f"Referenced artifact path must be a file: {artifact_path}")

    suffix = artifact_path.suffix.lower()
    if suffix == ".md":
        content = artifact_path.read_text(encoding="utf-8")
        return ArtifactDocument(reference.artifact_type, artifact_path, "md", content)
    if suffix in {".yaml", ".yml"}:
        content = _load_yaml_mapping(artifact_path, "artifact file")
        return ArtifactDocument(reference.artifact_type, artifact_path, "yaml", content)
    if suffix == ".json":
        content = _load_json_mapping(artifact_path)
        return ArtifactDocument(reference.artifact_type, artifact_path, "json", content)

    raise ArtifactLoadError(f"Unsupported artifact file type: {artifact_path.suffix}")


def _load_yaml_mapping(path: Path, label: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ArtifactLoadError(f"YAML parsing failed for {label} {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ArtifactLoadError(f"Top-level YAML content for {label} must be a mapping/object.")
    return data


def _load_json_mapping(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ArtifactLoadError(f"JSON parsing failed for artifact file {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ArtifactLoadError(f"Top-level JSON content for artifact file must be a mapping/object: {path}")
    return data


def _require_non_blank_string(container: dict[str, Any], key: str, label: str) -> str:
    value = container.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ArtifactLoadError(f"Missing or invalid {key} in {label}.")
    return value.strip()
