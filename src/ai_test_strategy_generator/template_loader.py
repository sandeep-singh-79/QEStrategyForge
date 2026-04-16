from __future__ import annotations

from pathlib import Path

from ai_test_strategy_generator.models import PromptTemplate

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_template(name: str, version: str = "v1", prompt_dir: Path | None = None) -> PromptTemplate:
    """Load a prompt template by name.

    If *prompt_dir* is given, load directly from that flat directory
    (``prompt_dir / name.txt``).  This is used by the optimizer to load
    mutated templates from a temporary directory.  Otherwise load from
    the installed prompts directory (``_PROMPTS_DIR / version / name.txt``).
    """
    if prompt_dir is not None:
        path = prompt_dir / f"{name}.txt"
    else:
        path = _PROMPTS_DIR / version / f"{name}.txt"
    if not path.is_file():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    text = path.read_text(encoding="utf-8")
    return PromptTemplate(name=name, version=version, template_text=text)
