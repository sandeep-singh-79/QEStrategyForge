from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypedDict

GENERATION_MODES: frozenset[str] = frozenset({"deterministic", "llm_assisted"})

# Exit codes used by all benchmark flow functions.
EXIT_SUCCESS = 0       # All assertions passed.
EXIT_LOAD_ERROR = 1    # Input file / artifact folder could not be loaded.
EXIT_INPUT_INVALID = 2 # Input failed schema validation.
EXIT_OUTPUT_INVALID = 3 # Generated output is structurally invalid after all fallbacks.
EXIT_ASSERTIONS_FAILED = 4 # Output is valid but one or more benchmark assertions failed.


class FlowResult(TypedDict):
    """Structured return type for all benchmark flow functions."""
    success: bool
    exit_code: int          # One of the EXIT_* constants above.
    validation_errors: list[str]
    assertion_errors: list[str]
    output_path: str
    repair_stats: dict[str, object]  # Populated by LLM flow; empty dict for deterministic flow.


def make_flow_result(
    success: bool,
    exit_code: int,
    validation_errors: list[str],
    assertion_errors: list[str],
    output_path: str | Path,
    repair_stats: dict[str, object] | None = None,
) -> FlowResult:
    """Construct a FlowResult dict from the given parameters."""
    return FlowResult(
        success=success,
        exit_code=exit_code,
        validation_errors=validation_errors,
        assertion_errors=assertion_errors,
        output_path=str(output_path),
        repair_stats=repair_stats if repair_stats is not None else {},
    )


def validate_mode(mode: str) -> None:
    """Raise ValueError for unsupported generation mode values."""
    if mode not in GENERATION_MODES:
        raise ValueError(
            f"Unsupported generation mode: {mode!r}. "
            f"Valid modes: {sorted(GENERATION_MODES)}"
        )


@dataclass(slots=True)
class InputPackage:
    source_path: Path
    raw: dict[str, Any]
    normalized: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ArtifactReference:
    artifact_type: str
    path: Path


@dataclass(slots=True)
class ArtifactManifest:
    source_path: Path
    engagement_name: str
    domain: str
    project_posture: str
    artifacts: list[ArtifactReference] = field(default_factory=list)
    overrides: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ArtifactDocument:
    artifact_type: str
    path: Path
    format: str
    content: Any


@dataclass(slots=True)
class ArtifactBundle:
    root_path: Path
    manifest: ArtifactManifest
    documents: list[ArtifactDocument] = field(default_factory=list)


@dataclass(slots=True)
class StrategySection:
    heading: str
    lines: list[str] = field(default_factory=list)


@dataclass(slots=True)
class StrategyDocument:
    sections: list[StrategySection] = field(default_factory=list)

    def to_markdown(self) -> str:
        markdown_lines: list[str] = []
        for section in self.sections:
            markdown_lines.append(section.heading)
            markdown_lines.extend(section.lines)
            markdown_lines.append("")

        return "\n".join(_drop_trailing_blank_lines(markdown_lines)) + "\n"


@dataclass(slots=True)
class PromptTemplate:
    name: str
    version: str
    template_text: str


@dataclass(slots=True)
class LLMConfig:
    model: str
    max_tokens: int = 4096
    temperature: float = 0.0

    def __post_init__(self) -> None:
        if not self.model or not self.model.strip():
            raise ValueError("LLMConfig.model must be a non-empty string")
        if self.max_tokens <= 0:
            raise ValueError(
                f"LLMConfig.max_tokens must be a positive integer, got {self.max_tokens}"
            )
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError(
                f"LLMConfig.temperature must be between 0.0 and 2.0, got {self.temperature}"
            )


@dataclass(slots=True)
class ProviderConfig:
    provider: str = "ollama"
    model: str = "glm4:latest"
    base_url: str = "http://localhost:11434"
    api_key: str | None = None
    temperature: float = 0.0
    max_tokens: int = 4096

    def __post_init__(self) -> None:
        if not self.provider or not self.provider.strip():
            raise ValueError("ProviderConfig.provider must be a non-empty string")
        if not self.model or not self.model.strip():
            raise ValueError("ProviderConfig.model must be a non-empty string")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError(
                f"ProviderConfig.temperature must be between 0.0 and 2.0, got {self.temperature}"
            )
        if self.max_tokens <= 0:
            raise ValueError(
                f"ProviderConfig.max_tokens must be a positive integer, got {self.max_tokens}"
            )


ClassificationResult = dict[str, str]


def _drop_trailing_blank_lines(lines: list[str]) -> list[str]:
    result = list(lines)
    while result and result[-1] == "":
        result.pop()
    return result
