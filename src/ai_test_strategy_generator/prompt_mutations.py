"""Prompt mutation strategies for the Karpathy-style optimization loop.

Each strategy is a callable:  mutate(template_text: str) -> (mutated_text: str, description: str)

All mutations are pure text transformations applied to a single template file.
They are intentionally simple — reordering, emphasis, and example injection.
Genetic algorithms and neural mutation are explicitly out of scope.

Usage
-----
    from ai_test_strategy_generator.prompt_mutations import ALL_MUTATIONS, apply_mutation

    mutated, description = apply_mutation(template_text, strategy_name)
"""
from __future__ import annotations

import random
import re
from collections.abc import Callable


# ---------------------------------------------------------------------------
# Strategy: emphasis_strengthening
# ---------------------------------------------------------------------------
# Add "CRITICAL: " prefix to instruction lines that start with "You MUST" or
# "It must include" or "Each section must".  Only runs if none are already
# prefixed (idempotent).
# ---------------------------------------------------------------------------

_EMPHASIS_TARGETS = re.compile(
    r"^(You MUST|It must include|Each section must)",
    re.MULTILINE,
)


def emphasis_strengthening(template: str) -> tuple[str, str]:
    """Prefix key instruction lines with 'CRITICAL: '."""
    if "CRITICAL:" in template:
        return template, "emphasis_strengthening: already applied, no change"
    mutated = _EMPHASIS_TARGETS.sub(r"CRITICAL: \1", template)
    count = len(_EMPHASIS_TARGETS.findall(template))
    return mutated, f"emphasis_strengthening: added CRITICAL prefix to {count} instruction line(s)"


# ---------------------------------------------------------------------------
# Strategy: emphasis_removal
# ---------------------------------------------------------------------------
# Remove "CRITICAL: " prefixes added by emphasis_strengthening (revert).
# ---------------------------------------------------------------------------

def emphasis_removal(template: str) -> tuple[str, str]:
    """Remove any 'CRITICAL: ' prefixes previously added."""
    if "CRITICAL:" not in template:
        return template, "emphasis_removal: no CRITICAL prefixes found, no change"
    mutated = re.sub(r"CRITICAL: ", "", template)
    return mutated, "emphasis_removal: removed all CRITICAL prefixes"


# ---------------------------------------------------------------------------
# Strategy: instruction_reordering
# ---------------------------------------------------------------------------
# Shuffle the order of "Place each decision in its natural section:" bullet
# lines.  These are the per-decision placement instructions in base.txt.
# Affects only the base template.
# ---------------------------------------------------------------------------

_PLACEMENT_BLOCK_RE = re.compile(
    r"(Place each decision in its natural section:\n)((?:  .+\n?)+)",
    re.MULTILINE,
)


def instruction_reordering(template: str) -> tuple[str, str]:
    """Shuffle the order of decision-placement bullet lines."""
    match = _PLACEMENT_BLOCK_RE.search(template)
    if not match:
        return template, "instruction_reordering: no placement block found, no change"

    header = match.group(1)
    block = match.group(2)
    lines = block.splitlines(keepends=True)
    shuffled = lines[:]
    random.shuffle(shuffled)
    if shuffled == lines:
        # Guarantee a change if order is identical
        shuffled = list(reversed(lines))
    mutated = template[: match.start()] + header + "".join(shuffled) + template[match.end() :]
    return mutated, f"instruction_reordering: shuffled {len(lines)} placement lines"


# ---------------------------------------------------------------------------
# Strategy: example_injection
# ---------------------------------------------------------------------------
# Append a short exemplar fragment after the Required Output Contract section
# in base.txt to show the LLM what a well-formed labeled line looks like.
# Only injected once (idempotent).
# ---------------------------------------------------------------------------

_EXAMPLE_MARKER = "## EXAMPLE (do not reproduce verbatim)"

_EXAMPLE_FRAGMENT = """
## EXAMPLE (do not reproduce verbatim)
The following shows the expected format for labeled lines in the output.
Do NOT copy this example — produce equivalent lines with values from the engagement context above.

  Strategy Confidence: standard
  Shift-Left Stance: strong_shift_left
  Layering Priority: lower_layers_first
  Automation Adoption Path: phased_expansion
  Governance Depth: standard
  Reporting Emphasis: pipeline_native
  Recommended Immediate Actions: establish_baseline_metrics

"""


def example_injection(template: str) -> tuple[str, str]:
    """Append a labeled-line example fragment to the template."""
    if _EXAMPLE_MARKER in template:
        return template, "example_injection: example already present, no change"
    return template + _EXAMPLE_FRAGMENT, "example_injection: appended labeled-line example fragment"


def example_removal(template: str) -> tuple[str, str]:
    """Remove example fragment added by example_injection (revert)."""
    if _EXAMPLE_MARKER not in template:
        return template, "example_removal: no example fragment found, no change"
    idx = template.index(_EXAMPLE_MARKER)
    # Walk back to the preceding newline so we clean up the blank line
    start = template.rfind("\n", 0, idx)
    mutated = template[:start].rstrip() + "\n"
    return mutated, "example_removal: removed labeled-line example fragment"


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

MutationFn = Callable[[str], tuple[str, str]]

ALL_MUTATIONS: dict[str, MutationFn] = {
    "emphasis_strengthening": emphasis_strengthening,
    "emphasis_removal": emphasis_removal,
    "instruction_reordering": instruction_reordering,
    "example_injection": example_injection,
    "example_removal": example_removal,
}


def apply_mutation(template: str, strategy_name: str) -> tuple[str, str]:
    """Apply a named mutation strategy to a template string.

    Returns
    -------
    tuple[str, str]
        (mutated_template, human-readable description of what changed)

    Raises
    ------
    KeyError
        If ``strategy_name`` is not in ALL_MUTATIONS.
    """
    fn = ALL_MUTATIONS[strategy_name]
    return fn(template)
