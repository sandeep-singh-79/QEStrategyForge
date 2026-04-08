from __future__ import annotations

import unittest
from unittest.mock import patch

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


if __name__ == "__main__":
    unittest.main()
