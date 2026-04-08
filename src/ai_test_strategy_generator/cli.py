from __future__ import annotations

import argparse
import sys

from ai_test_strategy_generator.main import run_validation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-test-strategy-generator",
        description="Deterministic v1 input validation for the AI Test Strategy Generator.",
    )
    parser.add_argument("input_file", help="Path to the v1 YAML input file.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(run_validation(args.input_file))
