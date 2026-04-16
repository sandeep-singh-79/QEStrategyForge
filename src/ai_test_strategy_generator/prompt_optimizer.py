"""Karpathy-style prompt optimization loop for QEStrategyForge.

Design principles
-----------------
- Binary scoring: every check is yes/no.  Score = count of passes.  Higher is better.
- Hybrid mutation: cumulative within a run (mutate best-so-far); fresh baseline across runs.
- Per-iteration wall-clock timeout: configurable, default 300 s.
- Experiment tracking: caller is responsible for persisting outputs to optimization_runs/.
- Winning prompts saved separately (e.g. prompts/v2/) — never overwrites prompts/v1/.

Typical usage
-------------
    from pathlib import Path
    from ai_test_strategy_generator.prompt_optimizer import (
        BenchmarkSpec, OptimizationConfig, run_optimization_loop
    )

    specs = [
        BenchmarkSpec("benchmarks/brownfield-partial-automation.input.yaml",
                      "benchmarks/brownfield-partial-automation.assertions.yaml"),
        BenchmarkSpec("benchmarks/greenfield-low-automation.input.yaml",
                      "benchmarks/greenfield-low-automation.assertions.yaml"),
    ]
    config = OptimizationConfig(
        prompt_dir=Path("src/ai_test_strategy_generator/prompts/v1"),
        mutations=["emphasis_strengthening", "instruction_reordering", "example_injection"],
        n_iterations=5,
        timeout_per_iter=300,
    )
    result = run_optimization_loop(specs, llm_config, llm_client, config)
    print(result.summary())
"""
from __future__ import annotations

import logging
import shutil
import signal
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from ai_test_strategy_generator.benchmark_runner import run_assertions
from ai_test_strategy_generator.llm_flow import run_llm_benchmark_flow
from ai_test_strategy_generator.models import LLMConfig
from ai_test_strategy_generator.optimizer_score import aggregate_scores, score_benchmark_run
from ai_test_strategy_generator.prompt_mutations import ALL_MUTATIONS, apply_mutation

if TYPE_CHECKING:
    from ai_test_strategy_generator.llm_client import LLMClient

_log = logging.getLogger(__name__)

# Template file names that can be mutated (only base.txt by default in v1)
_MUTABLE_TEMPLATES = ("base.txt",)


@dataclass
class BenchmarkSpec:
    """A single benchmark scenario: input YAML + assertions YAML."""
    input_path: str | Path
    assertions_path: str | Path

    def __post_init__(self) -> None:
        self.input_path = Path(self.input_path)
        self.assertions_path = Path(self.assertions_path)


@dataclass
class IterationRecord:
    """Score record for one optimization iteration."""
    iteration: int
    mutation_strategy: str | None
    mutation_description: str | None
    per_benchmark_scores: list[int]
    aggregate: int
    is_best: bool = False
    timed_out: bool = False


@dataclass
class OptimizationConfig:
    """Configuration for a single optimization run."""
    prompt_dir: Path
    mutations: list[str] = field(default_factory=lambda: [
        "emphasis_strengthening",
        "instruction_reordering",
        "example_injection",
    ])
    n_iterations: int = 5
    timeout_per_iter: int = 300  # seconds

    def __post_init__(self) -> None:
        self.prompt_dir = Path(self.prompt_dir)
        unknown = [m for m in self.mutations if m not in ALL_MUTATIONS]
        if unknown:
            raise ValueError(f"Unknown mutation strategies: {unknown}")


@dataclass
class OptimizationResult:
    """Full result of an optimization run."""
    baseline_aggregate: int
    best_aggregate: int
    best_iteration: int
    improvement_delta: int
    records: list[IterationRecord]
    best_prompt_dir: Path | None  # Dir containing the winning templates (None if no improvement)

    def improved(self) -> bool:
        return self.improvement_delta > 0

    def summary(self) -> str:
        lines = [
            "Optimization Run Summary",
            "=" * 40,
            f"  Baseline aggregate:  {self.baseline_aggregate}",
            f"  Best aggregate:      {self.best_aggregate}",
            f"  Improvement delta:   +{self.improvement_delta}",
            f"  Best iteration:      {self.best_iteration}",
            "",
            f"  {'Iter':<6} {'Mutation':<35} {'Aggregate':<12} {'Best?'}",
            f"  {'-'*6} {'-'*35} {'-'*12} {'-'*5}",
        ]
        for rec in self.records:
            mutation_label = rec.mutation_strategy or "baseline"
            if rec.timed_out:
                mutation_label += " [TIMEOUT]"
            best_marker = "★" if rec.is_best else ""
            lines.append(
                f"  {rec.iteration:<6} {mutation_label:<35} {rec.aggregate:<12} {best_marker}"
            )
        if self.improved():
            lines.append(f"\nWinner saved to: {self.best_prompt_dir}")
        else:
            lines.append("\nNo improvement found — prompts/v1/ unchanged.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _copy_prompt_dir(src: Path, dst: Path) -> None:
    """Copy all .txt files from src to dst (creates dst if needed)."""
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.glob("*.txt"):
        shutil.copy2(f, dst / f.name)


def _load_templates(prompt_dir: Path) -> dict[str, str]:
    """Return {filename: content} for all .txt files in prompt_dir."""
    return {f.name: f.read_text(encoding="utf-8") for f in prompt_dir.glob("*.txt")}


def _write_templates(templates: dict[str, str], target_dir: Path) -> None:
    """Write templates to target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)
    for name, text in templates.items():
        (target_dir / name).write_text(text, encoding="utf-8")


def _score_iteration(
    templates: dict[str, str],
    specs: list[BenchmarkSpec],
    llm_config: LLMConfig,
    llm_client: LLMClient,
    timeout_per_iter: int,
) -> tuple[list[int], bool]:
    """Run all benchmarks against the given templates and return (scores, timed_out).

    Templates are written to a temporary directory so llm_flow can load them
    via the standard template_loader path.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_prompt_dir = Path(tmpdir) / "prompts" / "active"
        _write_templates(templates, tmp_prompt_dir)

        per_benchmark_scores: list[int] = []
        deadline = time.monotonic() + timeout_per_iter

        for spec in specs:
            if time.monotonic() > deadline:
                _log.warning("Iteration timed out after %d s", timeout_per_iter)
                return per_benchmark_scores, True

            with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as out_f:
                out_path = Path(out_f.name)

            try:
                result = run_llm_benchmark_flow(
                    spec.input_path,
                    spec.assertions_path,
                    out_path,
                    llm_config,
                    llm_client,
                    prompt_dir=tmp_prompt_dir,
                )
                assertion_result = run_assertions(
                    out_path.read_text(encoding="utf-8") if out_path.exists() else "",
                    spec.assertions_path,
                )
                score = score_benchmark_run(result, assertion_result)
            finally:
                out_path.unlink(missing_ok=True)

            per_benchmark_scores.append(score)
            _log.debug(
                "Benchmark %s: score=%d exit_code=%d",
                spec.input_path.name,
                score,
                result["exit_code"],
            )

    return per_benchmark_scores, False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_optimization_loop(
    specs: list[BenchmarkSpec],
    llm_config: LLMConfig,
    llm_client: LLMClient,
    config: OptimizationConfig,
    output_dir: Path | None = None,
) -> OptimizationResult:
    """Run the Karpathy-style optimization loop.

    Parameters
    ----------
    specs:
        List of benchmark scenarios to evaluate on each iteration.
    llm_config:
        LLM model/token/temperature config.
    llm_client:
        Instantiated LLM client (Ollama, OpenAI, Gemini, or Fake).
    config:
        Optimization run configuration.
    output_dir:
        If given, baseline and winning templates are saved here for audit.
        The directory is NOT created inside the committed repo — callers
        are responsible for pointing to an .gitignored location.

    Returns
    -------
    OptimizationResult
        Full record of every iteration, the winner, and the improvement delta.
    """
    if not specs:
        raise ValueError("No benchmark specs provided.")

    mutations_cycle = list(config.mutations)

    # ------------------------------------------------------------------
    # Iteration 0: baseline (no mutation)
    # ------------------------------------------------------------------
    _log.info("Optimization loop starting: %d benchmarks, %d iterations",
              len(specs), config.n_iterations)

    baseline_templates = _load_templates(config.prompt_dir)
    if output_dir:
        _copy_prompt_dir(config.prompt_dir, output_dir / "iter_0")

    baseline_scores, timed_out = _score_iteration(
        baseline_templates, specs, llm_config, llm_client, config.timeout_per_iter
    )
    baseline_agg = aggregate_scores(baseline_scores)

    baseline_record = IterationRecord(
        iteration=0,
        mutation_strategy=None,
        mutation_description=None,
        per_benchmark_scores=baseline_scores,
        aggregate=baseline_agg,
        timed_out=timed_out,
    )
    records: list[IterationRecord] = [baseline_record]

    best_aggregate = baseline_agg
    best_iteration = 0
    best_templates = dict(baseline_templates)

    _log.info("Baseline aggregate score: %d", baseline_agg)

    # ------------------------------------------------------------------
    # Iterations 1..N: mutate best-so-far, score, keep-or-reject
    # ------------------------------------------------------------------
    current_templates = dict(baseline_templates)

    for i in range(1, config.n_iterations):
        mutation_name = mutations_cycle[(i - 1) % len(mutations_cycle)]
        _log.info("Iteration %d: applying mutation '%s'", i, mutation_name)

        # Apply mutation to base.txt only (other files unchanged)
        mutated_templates = dict(current_templates)
        description = f"{mutation_name}: no mutable template found"
        for tmpl_name in _MUTABLE_TEMPLATES:
            if tmpl_name in mutated_templates:
                mutated_templates[tmpl_name], description = apply_mutation(
                    mutated_templates[tmpl_name], mutation_name
                )
                break

        scores, timed_out = _score_iteration(
            mutated_templates, specs, llm_config, llm_client, config.timeout_per_iter
        )
        agg = aggregate_scores(scores) if not timed_out else 0

        is_best = agg > best_aggregate
        if is_best:
            best_aggregate = agg
            best_iteration = i
            best_templates = dict(mutated_templates)
            current_templates = dict(mutated_templates)  # compound next mutation on this winner
            _log.info("Iteration %d: new best score %d (+%d)", i, agg, agg - baseline_agg)
        else:
            _log.info("Iteration %d: score %d (no improvement; best remains %d)", i, agg, best_aggregate)

        records.append(IterationRecord(
            iteration=i,
            mutation_strategy=mutation_name,
            mutation_description=description,
            per_benchmark_scores=scores,
            aggregate=agg,
            is_best=is_best,
            timed_out=timed_out,
        ))

        if output_dir:
            iter_dir = output_dir / f"iter_{i}"
            _write_templates(mutated_templates, iter_dir)
            (iter_dir / "mutation.yaml").write_text(
                f"strategy: {mutation_name}\ndescription: {description}\n",
                encoding="utf-8",
            )

    # Mark baseline as best if nothing improved
    if best_iteration == 0:
        records[0].is_best = True

    # ------------------------------------------------------------------
    # Formalization: save winner to output_dir/best/
    # ------------------------------------------------------------------
    best_prompt_dir: Path | None = None
    improvement_delta = best_aggregate - baseline_agg
    if improvement_delta > 0 and output_dir:
        best_prompt_dir = output_dir / "best"
        _write_templates(best_templates, best_prompt_dir)
        _log.info(
            "Improvement found (+%d checks). Winner saved to %s",
            improvement_delta,
            best_prompt_dir,
        )
    elif improvement_delta == 0:
        _log.info("No improvement found after %d iterations.", config.n_iterations)

    return OptimizationResult(
        baseline_aggregate=baseline_agg,
        best_aggregate=best_aggregate,
        best_iteration=best_iteration,
        improvement_delta=improvement_delta,
        records=records,
        best_prompt_dir=best_prompt_dir,
    )
