from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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


ClassificationResult = dict[str, str]


def _drop_trailing_blank_lines(lines: list[str]) -> list[str]:
    result = list(lines)
    while result and result[-1] == "":
        result.pop()
    return result
