from __future__ import annotations

from pathlib import Path

from ai_test_strategy_generator.models import PromptTemplate

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_template(name: str, version: str = "v1") -> PromptTemplate:
    """Load a prompt template by name and version from the prompts directory."""
    path = _PROMPTS_DIR / version / f"{name}.txt"
    if not path.is_file():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    text = path.read_text(encoding="utf-8")
    return PromptTemplate(name=name, version=version, template_text=text)
