"""Tests for prompt_optimizer.py — optimization loop runner.

Uses mocked scoring so tests run without Ollama/OpenAI.
"""
from __future__ import annotations

import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

from ai_test_strategy_generator.llm_client import FakeLLMClient
from ai_test_strategy_generator.models import LLMConfig
from ai_test_strategy_generator.prompt_optimizer import (
    BenchmarkSpec,
    IterationRecord,
    OptimizationConfig,
    OptimizationResult,
    _score_iteration,
    run_optimization_loop,
)

_BENCHMARKS_DIR = Path("benchmarks")
_FAKE_CONFIG = LLMConfig(model="fake")
_TESTS_TMP = Path(__file__).parent / ".tmp"

# ---------------------------------------------------------------------------
# BenchmarkSpec
# ---------------------------------------------------------------------------

class BenchmarkSpecTests(unittest.TestCase):

    def test_paths_coerced_to_path(self) -> None:
        spec = BenchmarkSpec("benchmarks/a.yaml", "benchmarks/b.yaml")
        self.assertIsInstance(spec.input_path, Path)
        self.assertIsInstance(spec.assertions_path, Path)


# ---------------------------------------------------------------------------
# OptimizationConfig
# ---------------------------------------------------------------------------

class OptimizationConfigTests(unittest.TestCase):

    def test_unknown_mutation_raises(self) -> None:
        with self.assertRaises(ValueError):
            OptimizationConfig(
                prompt_dir=Path("."),
                mutations=["nonexistent_strategy"],
            )

    def test_valid_mutations_accepted(self) -> None:
        cfg = OptimizationConfig(
            prompt_dir=Path("."),
            mutations=["emphasis_strengthening", "instruction_reordering"],
        )
        self.assertEqual(len(cfg.mutations), 2)

    def test_prompt_dir_coerced_to_path(self) -> None:
        cfg = OptimizationConfig(prompt_dir="some/dir")
        self.assertIsInstance(cfg.prompt_dir, Path)

    def test_default_n_iterations(self) -> None:
        cfg = OptimizationConfig(prompt_dir=Path("."))
        self.assertEqual(cfg.n_iterations, 5)


# ---------------------------------------------------------------------------
# OptimizationResult
# ---------------------------------------------------------------------------

class OptimizationResultTests(unittest.TestCase):

    def _make_result(self, baseline: int, best: int, best_iter: int) -> OptimizationResult:
        records = [
            IterationRecord(0, None, None, [baseline], baseline, is_best=(best_iter == 0)),
        ]
        if best_iter > 0:
            records.append(
                IterationRecord(1, "emphasis_strengthening", "adds CRITICAL", [best], best, is_best=True)
            )
        return OptimizationResult(
            baseline_aggregate=baseline,
            best_aggregate=best,
            best_iteration=best_iter,
            improvement_delta=best - baseline,
            records=records,
            best_prompt_dir=Path("optimization_runs/best") if best > baseline else None,
        )

    def test_improved_true_when_delta_positive(self) -> None:
        result = self._make_result(10, 15, 1)
        self.assertTrue(result.improved())

    def test_improved_false_when_no_delta(self) -> None:
        result = self._make_result(10, 10, 0)
        self.assertFalse(result.improved())

    def test_summary_contains_baseline(self) -> None:
        result = self._make_result(20, 25, 1)
        summary = result.summary()
        self.assertIn("20", summary)
        self.assertIn("25", summary)

    def test_summary_contains_winner_line_when_improved(self) -> None:
        result = self._make_result(10, 15, 1)
        summary = result.summary()
        # Path may use OS separator; check the folder name exists
        self.assertIn("best", summary)

    def test_summary_contains_no_improvement_msg_when_flat(self) -> None:
        result = self._make_result(10, 10, 0)
        summary = result.summary()
        self.assertIn("No improvement", summary)


# ---------------------------------------------------------------------------
# run_optimization_loop — functional tests with mocked LLM flow
# ---------------------------------------------------------------------------


class RunOptimizationLoopTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmpdir = _TESTS_TMP / f"opt_{id(self)}"
        self._tmpdir.mkdir(parents=True, exist_ok=True)
        self._prompt_dir = self._tmpdir / "prompts"
        self._prompt_dir.mkdir()
        (self._prompt_dir / "base.txt").write_text(
            "You MUST include a risk section.\nGenerate the test strategy.\n",
            encoding="utf-8",
        )
        self._output_dir = Path(self._tmpdir) / "opt_runs"
        self._llm_client = FakeLLMClient()
        self._specs = [
            BenchmarkSpec(
                _BENCHMARKS_DIR / "brownfield-partial-automation.input.yaml",
                _BENCHMARKS_DIR / "brownfield-partial-automation.assertions.yaml",
            )
        ]
        self._config = OptimizationConfig(
            prompt_dir=self._prompt_dir,
            mutations=["emphasis_strengthening"],
            n_iterations=2,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def _patch_score_iteration(self, scores: list[int]):
        """Return a context manager that patches _score_iteration to return successive scores.
        Each element in `scores` is a single-benchmark score; wrapped in a list to match signature.
        """
        call_count = {"n": 0}
        def fake_score_iteration(templates, specs, llm_config, llm_client, timeout, work_dir):
            idx = min(call_count["n"], len(scores) - 1)
            call_count["n"] += 1
            return [scores[idx]], False  # _score_iteration returns (list[int], bool)
        return patch(
            "ai_test_strategy_generator.prompt_optimizer._score_iteration",
            side_effect=fake_score_iteration,
        )

    def test_raises_on_empty_specs(self) -> None:
        with self.assertRaises(ValueError):
            run_optimization_loop([], _FAKE_CONFIG, FakeLLMClient(), self._config)

    def test_returns_optimization_result(self) -> None:
        with self._patch_score_iteration([20, 22]):
            result = run_optimization_loop(
                self._specs, _FAKE_CONFIG, self._llm_client, self._config
            )
        self.assertIsInstance(result, OptimizationResult)

    def test_improvement_detected(self) -> None:
        with self._patch_score_iteration([20, 22]):
            result = run_optimization_loop(
                self._specs, _FAKE_CONFIG, self._llm_client, self._config
            )
        self.assertTrue(result.improved())
        self.assertEqual(result.improvement_delta, 2)
        self.assertEqual(result.best_iteration, 1)

    def test_no_improvement_detected(self) -> None:
        with self._patch_score_iteration([20, 18]):
            result = run_optimization_loop(
                self._specs, _FAKE_CONFIG, self._llm_client, self._config
            )
        self.assertFalse(result.improved())
        self.assertEqual(result.improvement_delta, 0)
        self.assertEqual(result.best_iteration, 0)

    def test_records_length_equals_n_iterations(self) -> None:
        with self._patch_score_iteration([10, 12]):
            result = run_optimization_loop(
                self._specs, _FAKE_CONFIG, self._llm_client, self._config
            )
        # n_iterations=2 means iter 0 (baseline) + iter 1 = 2 records
        self.assertEqual(len(result.records), 2)

    def test_baseline_record_has_no_mutation(self) -> None:
        with self._patch_score_iteration([10, 12]):
            result = run_optimization_loop(
                self._specs, _FAKE_CONFIG, self._llm_client, self._config
            )
        self.assertIsNone(result.records[0].mutation_strategy)

    def test_iteration_1_has_mutation_strategy(self) -> None:
        with self._patch_score_iteration([10, 12]):
            result = run_optimization_loop(
                self._specs, _FAKE_CONFIG, self._llm_client, self._config
            )
        self.assertEqual(result.records[1].mutation_strategy, "emphasis_strengthening")

    def test_output_dir_iter_0_created(self) -> None:
        with self._patch_score_iteration([10, 12]):
            result = run_optimization_loop(
                self._specs, _FAKE_CONFIG, self._llm_client, self._config,
                output_dir=self._output_dir,
            )
        self.assertTrue((self._output_dir / "iter_0").exists())

    def test_winner_saved_to_best_dir(self) -> None:
        with self._patch_score_iteration([10, 15]):
            result = run_optimization_loop(
                self._specs, _FAKE_CONFIG, self._llm_client, self._config,
                output_dir=self._output_dir,
            )
        self.assertIsNotNone(result.best_prompt_dir)
        self.assertTrue((self._output_dir / "best" / "base.txt").exists())

    def test_no_winner_dir_when_no_improvement(self) -> None:
        with self._patch_score_iteration([10, 10]):
            result = run_optimization_loop(
                self._specs, _FAKE_CONFIG, self._llm_client, self._config,
                output_dir=self._output_dir,
            )
        self.assertIsNone(result.best_prompt_dir)
        self.assertFalse((self._output_dir / "best").exists())

    def test_timed_out_iteration_scores_zero(self) -> None:
        call_count = {"n": 0}
        def fake_score_iteration(templates, specs, llm_config, llm_client, timeout, work_dir):
            idx = min(call_count["n"], 1)
            call_count["n"] += 1
            return ([10], False) if idx == 0 else ([], True)

        with patch(
            "ai_test_strategy_generator.prompt_optimizer._score_iteration",
            side_effect=fake_score_iteration,
        ):
            result = run_optimization_loop(
                self._specs, _FAKE_CONFIG, self._llm_client, self._config
            )

        self.assertTrue(result.records[1].timed_out)
        self.assertFalse(result.improved())

    def test_n_iterations_1_runs_baseline_only(self) -> None:
        """n_iterations=1 means range(1,1) is empty — only baseline record exists."""
        config = OptimizationConfig(
            prompt_dir=self._prompt_dir,
            mutations=["emphasis_strengthening"],
            n_iterations=1,
        )
        with self._patch_score_iteration([15]):
            result = run_optimization_loop(
                self._specs, _FAKE_CONFIG, self._llm_client, config
            )

        self.assertEqual(len(result.records), 1)
        self.assertIsNone(result.records[0].mutation_strategy)
        self.assertTrue(result.records[0].is_best)
        self.assertEqual(result.best_iteration, 0)
        self.assertFalse(result.improved())

    def test_mutations_cycle_when_iterations_exceed_mutation_count(self) -> None:
        """With 4 iterations and 2 mutations, mutations cycle:
        iter1→mut[0], iter2→mut[1], iter3→mut[0].
        """
        config = OptimizationConfig(
            prompt_dir=self._prompt_dir,
            mutations=["emphasis_strengthening", "instruction_reordering"],
            n_iterations=4,
        )
        with self._patch_score_iteration([10, 10, 10, 10]):
            result = run_optimization_loop(
                self._specs, _FAKE_CONFIG, self._llm_client, config
            )

        strategies = [r.mutation_strategy for r in result.records if r.mutation_strategy]
        self.assertEqual(strategies, [
            "emphasis_strengthening",
            "instruction_reordering",
            "emphasis_strengthening",
        ])


# ---------------------------------------------------------------------------
# _score_iteration — pipeline integration (RED test exposes core bug)
# ---------------------------------------------------------------------------

_REAL_PROMPTS_V1 = (
    Path(__file__).parent.parent
    / "src" / "ai_test_strategy_generator" / "prompts" / "v1"
)
_UNIQUE_MARKER = "UNIQUE_TEST_MARKER_XYZ_42"


class _CapturingClient:
    """LLMClient that records the prompt text it receives."""

    def __init__(self) -> None:
        self.last_prompt: str = ""

    def generate(
        self, request: object
    ) -> object:
        from ai_test_strategy_generator.llm_client import GenerationRequest
        assert isinstance(request, GenerationRequest)
        self.last_prompt = request.prompt
        return FakeLLMClient().generate(request)


class ScoreIterationPipelineTests(unittest.TestCase):
    """Verify that _score_iteration uses the templates dict it receives.

    This is the core behavioural contract of the optimizer: if mutations
    written to a temp dir are not fed into the LLM prompt, then scoring
    different prompt variants is meaningless.
    """

    def setUp(self) -> None:
        self._tmpdir = _TESTS_TMP / f"score_iter_{id(self)}"
        self._tmpdir.mkdir(parents=True, exist_ok=True)
        self._prompt_dir = self._tmpdir / "prompts"
        # Copy installed v1 templates so the flow can find scenario files.
        shutil.copytree(str(_REAL_PROMPTS_V1), str(self._prompt_dir))
        # Inject a unique marker into base.txt so we can detect which file was loaded.
        base_path = self._prompt_dir / "base.txt"
        base_path.write_text(
            f"# {_UNIQUE_MARKER}\n" + base_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_score_iteration_uses_provided_base_template(self) -> None:
        """The templates dict passed to _score_iteration must be used to build
        the LLM prompt.  If the installed base.txt is loaded instead, mutations
        never affect scoring and the whole optimization loop is a no-op.
        """
        templates = {
            f.name: f.read_text(encoding="utf-8")
            for f in self._prompt_dir.glob("*.txt")
        }
        client = _CapturingClient()
        specs = [BenchmarkSpec(
            _BENCHMARKS_DIR / "brownfield-partial-automation.input.yaml",
            _BENCHMARKS_DIR / "brownfield-partial-automation.assertions.yaml",
        )]

        _score_iteration(templates, specs, LLMConfig(model="fake"), client, timeout_per_iter=60,
                         work_dir=self._tmpdir / "score_work")

        self.assertIn(
            _UNIQUE_MARKER,
            client.last_prompt,
            "Templates provided to _score_iteration must be used to build the LLM prompt. "
            "If this fails, mutations have zero effect on scoring.",
        )


if __name__ == "__main__":
    unittest.main()
