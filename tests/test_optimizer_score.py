"""Tests for optimizer_score.py — binary scoring model."""
from __future__ import annotations

import unittest

from ai_test_strategy_generator.models import EXIT_ASSERTIONS_FAILED, EXIT_SUCCESS, ValidationResult
from ai_test_strategy_generator.optimizer_score import (
    aggregate_scores,
    max_checks_for_run,
    score_benchmark_run,
)

_FULL_REPAIR_STATS: dict = {
    "source": "llm",
    "headings_injected": 0,
    "labels_injected": 0,
    "total_headings": 14,
    "total_labels": 18,
}


def _make_result(exit_code: int, repair_stats: dict | None = None) -> dict:
    return {
        "success": exit_code == EXIT_SUCCESS,
        "exit_code": exit_code,
        "validation_errors": [],
        "assertion_errors": [],
        "output_path": "",
        "repair_stats": repair_stats if repair_stats is not None else {},
    }


class ScoreBenchmarkRunTests(unittest.TestCase):

    def test_perfect_run_scores_maximum(self) -> None:
        result = _make_result(EXIT_SUCCESS, _FULL_REPAIR_STATS)
        assertion_result = ValidationResult(is_valid=True, errors=[], total_checks=10)

        score = score_benchmark_run(result, assertion_result)

        # 1 (exit_code) + 1 (source==llm) + 10 (assertions) + 14 (headings) + 18 (labels) = 44
        self.assertEqual(score, 44)
        self.assertEqual(score, max_checks_for_run(10, 14, 18))

    def test_failed_exit_code_loses_one_point(self) -> None:
        result = _make_result(EXIT_ASSERTIONS_FAILED, _FULL_REPAIR_STATS)
        assertion_result = ValidationResult(is_valid=False, errors=["miss1"], total_checks=10)

        score = score_benchmark_run(result, assertion_result)

        # exit_code fails (-1), source still llm (+1), 9/10 assertions pass (+9), all native (+32)
        self.assertEqual(score, 1 + 9 + 14 + 18)

    def test_repair_source_loses_source_check(self) -> None:
        stats = {**_FULL_REPAIR_STATS, "source": "repair", "headings_injected": 2}
        result = _make_result(EXIT_SUCCESS, stats)
        assertion_result = ValidationResult(is_valid=True, errors=[], total_checks=5)

        score = score_benchmark_run(result, assertion_result)

        # exit_code (+1), source NOT llm (+0), 5 assertions (+5), 12 native headings (+12), 18 labels (+18)
        self.assertEqual(score, 1 + 0 + 5 + 12 + 18)

    def test_injected_labels_reduce_score(self) -> None:
        stats = {**_FULL_REPAIR_STATS, "labels_injected": 5}
        result = _make_result(EXIT_SUCCESS, stats)
        assertion_result = ValidationResult(is_valid=True, errors=[], total_checks=0)

        score = score_benchmark_run(result, assertion_result)

        self.assertEqual(score, 1 + 1 + 0 + 14 + 13)

    def test_empty_repair_stats_still_scores_exit_and_assertions(self) -> None:
        result = _make_result(EXIT_SUCCESS, {})
        assertion_result = ValidationResult(is_valid=True, errors=[], total_checks=3)

        score = score_benchmark_run(result, assertion_result)

        # exit_code (+1), source not "llm" (+0), 3 assertions (+3), 0 headings/labels (+0)
        self.assertEqual(score, 4)

    def test_all_failed_returns_zero(self) -> None:
        stats = {
            "source": "deterministic",
            "headings_injected": 14,
            "labels_injected": 18,
            "total_headings": 14,
            "total_labels": 18,
        }
        result = _make_result(EXIT_ASSERTIONS_FAILED, stats)
        assertion_result = ValidationResult(
            is_valid=False,
            errors=[f"err{i}" for i in range(5)],
            total_checks=5,
        )

        score = score_benchmark_run(result, assertion_result)
        self.assertEqual(score, 0)


class AggregateScoresTests(unittest.TestCase):

    def test_sum_of_per_benchmark_scores(self) -> None:
        self.assertEqual(aggregate_scores([10, 20, 30]), 60)

    def test_empty_list_returns_zero(self) -> None:
        self.assertEqual(aggregate_scores([]), 0)

    def test_single_benchmark(self) -> None:
        self.assertEqual(aggregate_scores([44]), 44)


class MaxChecksTests(unittest.TestCase):

    def test_max_checks_formula(self) -> None:
        # 2 fixed + N assertions + H headings + L labels
        self.assertEqual(max_checks_for_run(10, 14, 18), 44)
        self.assertEqual(max_checks_for_run(0, 0, 0), 2)


if __name__ == "__main__":
    unittest.main()
