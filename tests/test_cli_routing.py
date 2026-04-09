"""Tests for CLI routing + DI wiring (Slice 7.2)."""
from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_test_strategy_generator.cli import build_parser, main
from ai_test_strategy_generator.llm_client import FakeLLMClient


# ---------------------------------------------------------------------------
# Parser unit tests
# ---------------------------------------------------------------------------

class TestBuildParserNewFlags(unittest.TestCase):
    """New flags are properly declared and default correctly."""

    def _parse(self, argv: list[str]) -> object:
        return build_parser().parse_args(argv)

    def test_assertions_flag_accepted(self) -> None:
        args = self._parse(["input.yaml", "--assertions", "a.yaml"])
        self.assertEqual(args.assertions, "a.yaml")

    def test_output_flag_accepted(self) -> None:
        args = self._parse(["input.yaml", "--output", "out.md"])
        self.assertEqual(args.output, "out.md")

    def test_artifact_folder_flag_accepted(self) -> None:
        args = self._parse(["--artifact-folder", "/some/folder"])
        self.assertIsNone(args.input_file)
        self.assertEqual(args.artifact_folder, "/some/folder")

    def test_provider_flag_accepted(self) -> None:
        args = self._parse(["input.yaml", "--provider", "openai"])
        self.assertEqual(args.provider, "openai")

    def test_model_flag_accepted(self) -> None:
        args = self._parse(["input.yaml", "--model", "gpt-4o"])
        self.assertEqual(args.model, "gpt-4o")

    def test_config_flag_accepted(self) -> None:
        args = self._parse(["input.yaml", "--config", "strategy.config.yaml"])
        self.assertEqual(args.config, "strategy.config.yaml")

    def test_base_url_flag_accepted(self) -> None:
        args = self._parse(["input.yaml", "--base-url", "http://localhost:11434"])
        self.assertEqual(args.base_url, "http://localhost:11434")

    def test_temperature_flag_accepted(self) -> None:
        args = self._parse(["input.yaml", "--temperature", "0.7"])
        self.assertAlmostEqual(args.temperature, 0.7)

    def test_max_tokens_flag_accepted(self) -> None:
        args = self._parse(["input.yaml", "--max-tokens", "1024"])
        self.assertEqual(args.max_tokens, 1024)

    def test_input_file_is_optional(self) -> None:
        args = self._parse(["--artifact-folder", "/folder"])
        self.assertIsNone(args.input_file)

    def test_defaults_are_none_for_optional_flags(self) -> None:
        args = self._parse(["input.yaml"])
        self.assertIsNone(args.assertions)
        self.assertIsNone(args.output)
        self.assertIsNone(args.artifact_folder)
        self.assertIsNone(args.provider)
        self.assertIsNone(args.model)
        self.assertIsNone(args.config)
        self.assertIsNone(args.base_url)
        self.assertIsNone(args.temperature)
        self.assertIsNone(args.max_tokens)


# ---------------------------------------------------------------------------
# Backward-compatibility: no assertions → run_validation
# ---------------------------------------------------------------------------

class TestMainBackwardCompatibility(unittest.TestCase):
    def test_validation_mode_called_when_no_assertions(self) -> None:
        with patch("ai_test_strategy_generator.cli.run_validation", return_value=0) as mock_val:
            with patch("sys.argv", ["ai-test-strategy-generator", "input.yaml"]):
                with self.assertRaises(SystemExit) as ctx:
                    main()
        mock_val.assert_called_once_with("input.yaml")
        self.assertEqual(ctx.exception.code, 0)

    def test_no_input_and_no_artifact_folder_exits_nonzero(self) -> None:
        with patch("sys.argv", ["ai-test-strategy-generator"]):
            with self.assertRaises(SystemExit) as ctx:
                main()
        self.assertNotEqual(ctx.exception.code, 0)


# ---------------------------------------------------------------------------
# Routing to deterministic flow
# ---------------------------------------------------------------------------

class TestMainDeterministicRouting(unittest.TestCase):
    _COMMON_ARGV = [
        "ai-test-strategy-generator",
        "benchmarks/input.yaml",
        "--mode", "deterministic",
        "--assertions", "benchmarks/a.yaml",
        "--output", "out.md",
    ]

    def test_deterministic_input_routes_to_benchmark_flow(self) -> None:
        mock_result = {"success": True, "exit_code": 0, "validation_errors": [], "assertion_errors": [], "output_path": "out.md"}
        with patch("ai_test_strategy_generator.cli.run_benchmark_flow", return_value=mock_result) as mock_flow:
            with patch("sys.argv", self._COMMON_ARGV):
                with self.assertRaises(SystemExit) as ctx:
                    main()
        mock_flow.assert_called_once()
        call_kwargs = mock_flow.call_args
        self.assertEqual(ctx.exception.code, 0)

    def test_deterministic_artifact_routes_to_artifact_benchmark_flow(self) -> None:
        mock_result = {"success": True, "exit_code": 0, "validation_errors": [], "assertion_errors": [], "output_path": "out.md"}
        with patch("ai_test_strategy_generator.cli.run_artifact_benchmark_flow", return_value=mock_result) as mock_flow:
            with patch("sys.argv", [
                "ai-test-strategy-generator",
                "--artifact-folder", "benchmarks/artifact-brownfield",
                "--mode", "deterministic",
                "--assertions", "benchmarks/a.yaml",
                "--output", "out.md",
            ]):
                with self.assertRaises(SystemExit) as ctx:
                    main()
        mock_flow.assert_called_once()
        self.assertEqual(ctx.exception.code, 0)

    def test_exit_code_reflects_flow_result(self) -> None:
        mock_result = {"success": False, "exit_code": 4, "validation_errors": [], "assertion_errors": ["x"], "output_path": "out.md"}
        with patch("ai_test_strategy_generator.cli.run_benchmark_flow", return_value=mock_result):
            with patch("sys.argv", self._COMMON_ARGV):
                with self.assertRaises(SystemExit) as ctx:
                    main()
        self.assertEqual(ctx.exception.code, 4)


# ---------------------------------------------------------------------------
# Routing to LLM-assisted flow
# ---------------------------------------------------------------------------

class TestMainLLMRoutingUnit(unittest.TestCase):
    """Use FakeLLMClient injected directly — no HTTP calls, no mocking urllib."""

    _BASE_ARGV = [
        "ai-test-strategy-generator",
        "input.yaml",
        "--mode", "llm_assisted",
        "--provider", "ollama",
        "--assertions", "a.yaml",
        "--output", "out.md",
    ]

    def test_llm_assisted_routes_to_llm_benchmark_flow(self) -> None:
        mock_result = {"success": True, "exit_code": 0, "validation_errors": [], "assertion_errors": [], "output_path": "out.md"}
        with patch("ai_test_strategy_generator.cli.run_llm_benchmark_flow", return_value=mock_result) as mock_flow:
            with patch("ai_test_strategy_generator.cli.create_llm_client", return_value=FakeLLMClient()):
                with patch("sys.argv", self._BASE_ARGV):
                    with self.assertRaises(SystemExit) as ctx:
                        main()
        mock_flow.assert_called_once()
        self.assertEqual(ctx.exception.code, 0)

    def test_llm_assisted_without_provider_exits_nonzero(self) -> None:
        with patch("sys.argv", [
            "ai-test-strategy-generator",
            "input.yaml",
            "--mode", "llm_assisted",
            "--assertions", "a.yaml",
            "--output", "out.md",
        ]):
            with self.assertRaises(SystemExit) as ctx:
                main()
        self.assertNotEqual(ctx.exception.code, 0)

    def test_llm_assisted_artifact_routes_to_llm_artifact_path(self) -> None:
        mock_result = {"success": True, "exit_code": 0, "validation_errors": [], "assertion_errors": [], "output_path": "out.md"}
        with patch("ai_test_strategy_generator.cli.run_llm_artifact_benchmark_flow", return_value=mock_result) as mock_flow:
            with patch("ai_test_strategy_generator.cli.create_llm_client", return_value=FakeLLMClient()):
                with patch("sys.argv", [
                    "ai-test-strategy-generator",
                    "--artifact-folder", "benchmarks/artifact-brownfield",
                    "--mode", "llm_assisted",
                    "--provider", "ollama",
                    "--assertions", "a.yaml",
                    "--output", "out.md",
                ]):
                    with self.assertRaises(SystemExit) as ctx:
                        main()
        mock_flow.assert_called_once()
        self.assertEqual(ctx.exception.code, 0)


# ---------------------------------------------------------------------------
# Integration: deterministic benchmark end-to-end (real files)
# ---------------------------------------------------------------------------

class TestMainDeterministicIntegration(unittest.TestCase):
    """Full CLI invocation against committed benchmark files (no mocking)."""

    _INPUT = str(
        Path(__file__).parent.parent
        / "benchmarks"
        / "brownfield-partial-automation.input.yaml"
    )
    _ASSERTIONS = str(
        Path(__file__).parent.parent
        / "benchmarks"
        / "brownfield-partial-automation.assertions.yaml"
    )

    def test_deterministic_benchmark_exits_zero(self) -> None:
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            output_path = f.name
        try:
            with patch("sys.argv", [
                "ai-test-strategy-generator",
                self._INPUT,
                "--mode", "deterministic",
                "--assertions", self._ASSERTIONS,
                "--output", output_path,
            ]):
                with self.assertRaises(SystemExit) as ctx:
                    main()
            self.assertEqual(ctx.exception.code, 0)
            self.assertTrue(Path(output_path).stat().st_size > 0)
        finally:
            Path(output_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
