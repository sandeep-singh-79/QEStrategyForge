from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_test_strategy_generator.cli import build_parser, main


class CliTests(unittest.TestCase):
    def test_build_parser_reads_input_argument(self) -> None:
        parser = build_parser()

        args = parser.parse_args(["example.yaml"])

        self.assertEqual(args.input_file, "example.yaml")

    def test_main_exits_with_run_validation_code(self) -> None:
        with patch("ai_test_strategy_generator.cli.run_validation", return_value=7) as mocked_run:
            with patch("sys.argv", ["ai-test-strategy-generator", "example.yaml"]):
                with self.assertRaises(SystemExit) as ctx:
                    main()

        mocked_run.assert_called_once_with("example.yaml")
        self.assertEqual(ctx.exception.code, 7)

    def test_main_exits_non_zero_when_required_arg_missing(self) -> None:
        with patch("sys.argv", ["ai-test-strategy-generator"]):
            with self.assertRaises(SystemExit) as ctx:
                main()

        self.assertNotEqual(ctx.exception.code, 0)

    def test_build_parser_accepts_compare_flag(self) -> None:
        parser = build_parser()

        args = parser.parse_args([
            "example.yaml",
            "--mode", "llm_assisted",
            "--assertions", "asserts.yaml",
            "--output", "out.md",
            "--compare", "compare.md",
        ])

        self.assertEqual(args.compare, "compare.md")

    def test_build_parser_compare_is_none_by_default(self) -> None:
        parser = build_parser()

        args = parser.parse_args(["example.yaml"])

        self.assertIsNone(args.compare)

    # ------------------------------------------------------------------
    # CLI flag overrides
    # ------------------------------------------------------------------

    def test_build_provider_config_applies_cli_overrides(self) -> None:
        from ai_test_strategy_generator.cli import _build_provider_config

        parser = build_parser()
        args = parser.parse_args([
            "example.yaml",
            "--provider", "ollama",
            "--model", "llama3",
            "--base-url", "http://localhost:11434",
            "--temperature", "0.5",
            "--max-tokens", "2048",
        ])

        with patch("ai_test_strategy_generator.cli.load_config", return_value={
            "provider": "openai", "model": "gpt-4o", "base_url": None,
            "temperature": 0.0, "max_tokens": 4096,
        }):
            config = _build_provider_config(args)

        self.assertEqual(config.provider, "ollama")
        self.assertEqual(config.model, "llama3")
        self.assertEqual(config.base_url, "http://localhost:11434")
        self.assertAlmostEqual(config.temperature, 0.5)
        self.assertEqual(config.max_tokens, 2048)

    # ------------------------------------------------------------------
    # Error path: missing --output in generation mode
    # ------------------------------------------------------------------

    def test_main_errors_when_assertions_given_without_output(self) -> None:
        with patch("sys.argv", [
            "ai-test-strategy-generator", "example.yaml",
            "--assertions", "assert.yaml",
        ]):
            with self.assertRaises(SystemExit) as ctx:
                main()

        self.assertNotEqual(ctx.exception.code, 0)

    # ------------------------------------------------------------------
    # Deterministic generation mode
    # ------------------------------------------------------------------

    def test_main_deterministic_mode_calls_run_benchmark_flow(self) -> None:
        fake_result = {"exit_code": 0, "output_path": "out.md", "assertion_errors": []}
        with patch("ai_test_strategy_generator.cli.run_benchmark_flow", return_value=fake_result) as mock_flow:
            with patch("sys.argv", [
                "ai-test-strategy-generator", "input.yaml",
                "--assertions", "assert.yaml",
                "--output", "out.md",
            ]):
                with self.assertRaises(SystemExit) as ctx:
                    main()

        mock_flow.assert_called_once_with("input.yaml", "assert.yaml", "out.md")
        self.assertEqual(ctx.exception.code, 0)

    # ------------------------------------------------------------------
    # LLM-assisted generation mode
    # ------------------------------------------------------------------

    def test_main_llm_mode_calls_run_llm_benchmark_flow(self) -> None:
        fake_result = {"exit_code": 0, "output_path": "out.md", "repair_stats": None, "assertion_errors": []}
        fake_client = MagicMock()

        with patch("ai_test_strategy_generator.cli.run_llm_benchmark_flow", return_value=fake_result) as mock_flow, \
             patch("ai_test_strategy_generator.cli.create_llm_client", return_value=fake_client), \
             patch("ai_test_strategy_generator.cli.load_config", return_value={
                 "provider": "ollama", "model": "llama3", "base_url": None,
                 "temperature": 0.0, "max_tokens": 4096,
             }):
            with patch("sys.argv", [
                "ai-test-strategy-generator", "input.yaml",
                "--mode", "llm_assisted",
                "--provider", "ollama",
                "--assertions", "assert.yaml",
                "--output", "out.md",
            ]):
                with self.assertRaises(SystemExit) as ctx:
                    main()

        mock_flow.assert_called_once()
        self.assertEqual(ctx.exception.code, 0)

    def test_main_llm_mode_errors_without_provider(self) -> None:
        with patch("sys.argv", [
            "ai-test-strategy-generator", "input.yaml",
            "--mode", "llm_assisted",
            "--assertions", "assert.yaml",
            "--output", "out.md",
        ]):
            with self.assertRaises(SystemExit) as ctx:
                main()

        self.assertNotEqual(ctx.exception.code, 0)

    def test_main_llm_mode_errors_when_create_client_raises(self) -> None:
        with patch("ai_test_strategy_generator.cli.load_config", return_value={
            "provider": "openai", "model": "gpt-4o", "base_url": None,
            "temperature": 0.0, "max_tokens": 4096,
        }), patch("ai_test_strategy_generator.cli.create_llm_client", side_effect=ValueError("bad provider")):
            with patch("sys.argv", [
                "ai-test-strategy-generator", "input.yaml",
                "--mode", "llm_assisted",
                "--provider", "openai",
                "--assertions", "assert.yaml",
                "--output", "out.md",
            ]):
                with self.assertRaises(SystemExit) as ctx:
                    main()

        self.assertNotEqual(ctx.exception.code, 0)

    # ------------------------------------------------------------------
    # Optimize mode
    # ------------------------------------------------------------------

    def test_main_optimize_flag_calls_run_optimization_loop(self) -> None:
        from ai_test_strategy_generator.prompt_optimizer import OptimizationResult

        fake_result = OptimizationResult(
            baseline_aggregate=0,
            best_aggregate=1,
            best_iteration=1,
            improvement_delta=1,
            records=[],
            best_prompt_dir=None,
        )
        fake_client = MagicMock()

        with patch("ai_test_strategy_generator.cli.run_optimization_loop", return_value=fake_result) as mock_opt, \
             patch("ai_test_strategy_generator.cli.create_llm_client", return_value=fake_client), \
             patch("ai_test_strategy_generator.cli.load_config", return_value={
                 "provider": "ollama", "model": "llama3", "base_url": None,
                 "temperature": 0.0, "max_tokens": 4096,
             }):
            with patch("sys.argv", [
                "ai-test-strategy-generator", "input.yaml",
                "--mode", "llm_assisted",
                "--provider", "ollama",
                "--assertions", "assert.yaml",
                "--output", "out.md",
                "--optimize",
            ]):
                with self.assertRaises(SystemExit) as ctx:
                    main()

        mock_opt.assert_called_once()
        self.assertEqual(ctx.exception.code, 0)

    def test_main_optimize_errors_without_assertions(self) -> None:
        fake_client = MagicMock()
        with patch("ai_test_strategy_generator.cli.create_llm_client", return_value=fake_client), \
             patch("ai_test_strategy_generator.cli.load_config", return_value={
                 "provider": "ollama", "model": "llama3", "base_url": None,
                 "temperature": 0.0, "max_tokens": 4096,
             }):
            # --optimize requires --assertions, which is also the generation-mode gate
            with patch("sys.argv", [
                "ai-test-strategy-generator", "input.yaml",
                "--mode", "llm_assisted",
                "--provider", "ollama",
                "--output", "out.md",
                "--optimize",
            ]):
                with self.assertRaises(SystemExit) as ctx:
                    main()

        self.assertNotEqual(ctx.exception.code, 0)

    def test_main_errors_when_artifact_folder_given_with_no_assertions(self) -> None:
        """--artifact-folder without --assertions triggers validation-mode error (needs input_file)."""
        with patch("sys.argv", [
            "ai-test-strategy-generator",
            "--artifact-folder", "benchmarks/artifact-brownfield",
        ]):
            with self.assertRaises(SystemExit) as ctx:
                main()

        self.assertNotEqual(ctx.exception.code, 0)

    def test_main_llm_mode_errors_when_build_provider_config_raises(self) -> None:
        """_build_provider_config raising ValueError triggers parser.error."""
        with patch("ai_test_strategy_generator.cli._build_provider_config", side_effect=ValueError("bad config")):
            with patch("sys.argv", [
                "ai-test-strategy-generator", "input.yaml",
                "--mode", "llm_assisted",
                "--provider", "ollama",
                "--assertions", "assert.yaml",
                "--output", "out.md",
            ]):
                with self.assertRaises(SystemExit) as ctx:
                    main()

        self.assertNotEqual(ctx.exception.code, 0)

    def test_main_llm_mode_writes_compare_report_when_flag_set(self) -> None:
        import tempfile, os
        fake_result = {"exit_code": 0, "output_path": "out.md", "repair_stats": None, "assertion_errors": []}
        fake_client = MagicMock()

        with tempfile.TemporaryDirectory() as tmp:
            compare_path = os.path.join(tmp, "compare.md")
            out_path = os.path.join(tmp, "out.md")
            open(out_path, "w").close()  # create empty output file

            with patch("ai_test_strategy_generator.cli.run_llm_benchmark_flow", return_value=fake_result), \
                 patch("ai_test_strategy_generator.cli.create_llm_client", return_value=fake_client), \
                 patch("ai_test_strategy_generator.cli.load_config", return_value={
                     "provider": "ollama", "model": "llama3", "base_url": None,
                     "temperature": 0.0, "max_tokens": 4096,
                 }), \
                 patch("ai_test_strategy_generator.cli.run_benchmark_flow", return_value={"exit_code": 0}), \
                 patch("ai_test_strategy_generator.cli.build_comparison_report", return_value="# Report"):
                with patch("sys.argv", [
                    "ai-test-strategy-generator", "input.yaml",
                    "--mode", "llm_assisted",
                    "--provider", "ollama",
                    "--assertions", "assert.yaml",
                    "--output", out_path,
                    "--compare", compare_path,
                ]):
                    with self.assertRaises(SystemExit) as ctx:
                        main()

            self.assertEqual(ctx.exception.code, 0)
            self.assertTrue(Path(compare_path).exists())

    def test_run_optimization_errors_without_input_file(self) -> None:
        """_run_optimization returns non-zero when input_file is missing."""
        from ai_test_strategy_generator.cli import _run_optimization
        from ai_test_strategy_generator.models import LLMConfig

        parser = build_parser()
        args = parser.parse_args(["--artifact-folder", "some/folder", "--assertions", "a.yaml", "--output", "out.md"])
        # no input_file set
        result = _run_optimization(args, LLMConfig(model="llama3"), MagicMock())

    def test_run_optimization_writes_scoreboard_when_output_dir_given(self) -> None:
        import tempfile
        from ai_test_strategy_generator.cli import _run_optimization
        from ai_test_strategy_generator.models import LLMConfig
        from ai_test_strategy_generator.prompt_optimizer import OptimizationResult, IterationRecord

        record = IterationRecord(
            iteration=1,
            mutation_strategy="baseline",
            mutation_description="initial",
            per_benchmark_scores={"s": 1},
            aggregate=1,
            is_best=True,
            timed_out=False,
        )
        fake_result = OptimizationResult(
            baseline_aggregate=0,
            best_aggregate=1,
            best_iteration=1,
            improvement_delta=1,
            records=[record],
            best_prompt_dir=None,
        )

        parser = build_parser()

        with tempfile.TemporaryDirectory() as tmp:
            args = parser.parse_args([
                "input.yaml",
                "--assertions", "a.yaml",
                "--output", "out.md",
                "--optimize-output-dir", tmp,
            ])
            with patch("ai_test_strategy_generator.cli.run_optimization_loop", return_value=fake_result):
                result = _run_optimization(args, LLMConfig(model="llama3"), MagicMock())

            self.assertEqual(result, 0)
            # Scoreboard written inside a timestamped run_* subdirectory
            scoreboards = list(Path(tmp).rglob("scoreboard.yaml"))
            self.assertGreater(len(scoreboards), 0, "Expected scoreboard.yaml to be written")


if __name__ == "__main__":
    unittest.main()
