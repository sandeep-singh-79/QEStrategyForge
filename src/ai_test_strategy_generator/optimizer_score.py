"""Binary scoring model for the Karpathy-style prompt optimization loop.

Every measurement is a yes/no check.  Score = number of checks that passed.
No weights, no thresholds, no subjective quality layers.

Per-benchmark binary checks
----------------------------
1. exit_code == EXIT_SUCCESS (0)              — 1 check
2. repair_stats["source"] == "llm"            — 1 check (LLM produced without repair)
3. Each individual assertion from YAML        — N checks (total_checks from run_assertions)
4. Each required heading natively present     — total_headings checks
5. Each required label natively present       — total_labels checks

Score aggregation
-----------------
Aggregate across benchmarks = sum of per-benchmark scores (integer).
Higher is better.  Improvement criterion: aggregate > best_so_far.
"""
from __future__ import annotations

from ai_test_strategy_generator.models import EXIT_SUCCESS, FlowResult, ValidationResult


def score_benchmark_run(result: FlowResult, assertion_result: ValidationResult) -> int:
    """Compute the binary check score for a single benchmark run.

    Parameters
    ----------
    result:
        The FlowResult returned by the LLM flow.
    assertion_result:
        The ValidationResult returned by benchmark_runner.run_assertions().
        Must have ``total_checks`` populated (requires the updated benchmark_runner).

    Returns
    -------
    int
        Count of binary checks that passed.  Range: 0 .. max_checks_for_run().
    """
    passed = 0

    # Check 1: successful exit code
    if result["exit_code"] == EXIT_SUCCESS:
        passed += 1

    # Check 2: LLM produced output without needing the repair pass
    repair_stats = result.get("repair_stats") or {}
    if repair_stats.get("source") == "llm":
        passed += 1

    # Checks 3..N: individual assertion outcomes
    total_assertions = assertion_result.total_checks
    failed_assertions = len(assertion_result.errors)
    passed += max(0, total_assertions - failed_assertions)

    # Checks for headings natively present (not injected)
    total_headings = int(repair_stats.get("total_headings", 0))
    headings_injected = int(repair_stats.get("headings_injected", 0))
    passed += max(0, total_headings - headings_injected)

    # Checks for labels natively present (not injected)
    total_labels = int(repair_stats.get("total_labels", 0))
    labels_injected = int(repair_stats.get("labels_injected", 0))
    passed += max(0, total_labels - labels_injected)

    return passed


def max_checks_for_run(assertion_total_checks: int, total_headings: int, total_labels: int) -> int:
    """Return the theoretical maximum score for one benchmark run.

    Parameters
    ----------
    assertion_total_checks:
        Total number of assertions in the benchmark YAML (from ValidationResult.total_checks).
    total_headings:
        Number of required headings (from repair_stats["total_headings"]).
    total_labels:
        Number of required labels (from repair_stats["total_labels"]).
    """
    return 2 + assertion_total_checks + total_headings + total_labels


def aggregate_scores(per_benchmark: list[int]) -> int:
    """Return the aggregate score across all benchmark runs (simple sum)."""
    return sum(per_benchmark)
