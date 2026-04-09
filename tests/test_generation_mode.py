from __future__ import annotations

import unittest


class GenerationModeTests(unittest.TestCase):
    def test_deterministic_is_valid_mode(self) -> None:
        from ai_test_strategy_generator.models import validate_mode

        validate_mode("deterministic")  # must not raise

    def test_llm_assisted_is_valid_mode(self) -> None:
        from ai_test_strategy_generator.models import validate_mode

        validate_mode("llm_assisted")  # must not raise

    def test_invalid_mode_raises_value_error(self) -> None:
        from ai_test_strategy_generator.models import validate_mode

        with self.assertRaises(ValueError):
            validate_mode("auto")

    def test_empty_mode_raises_value_error(self) -> None:
        from ai_test_strategy_generator.models import validate_mode

        with self.assertRaises(ValueError):
            validate_mode("")

    def test_unknown_mode_error_message_names_valid_modes(self) -> None:
        from ai_test_strategy_generator.models import validate_mode

        with self.assertRaises(ValueError) as ctx:
            validate_mode("magic")

        self.assertIn("deterministic", str(ctx.exception))
        self.assertIn("llm_assisted", str(ctx.exception))


class LLMConfigTests(unittest.TestCase):
    def test_llm_config_created_with_valid_model(self) -> None:
        from ai_test_strategy_generator.models import LLMConfig

        config = LLMConfig(model="gpt-5.4")

        self.assertEqual(config.model, "gpt-5.4")
        self.assertEqual(config.max_tokens, 4096)
        self.assertAlmostEqual(config.temperature, 0.0)

    def test_llm_config_accepts_custom_tokens_and_temperature(self) -> None:
        from ai_test_strategy_generator.models import LLMConfig

        config = LLMConfig(model="gemini-pro", max_tokens=2048, temperature=0.3)

        self.assertEqual(config.max_tokens, 2048)
        self.assertAlmostEqual(config.temperature, 0.3)

    def test_llm_config_raises_for_empty_model(self) -> None:
        from ai_test_strategy_generator.models import LLMConfig

        with self.assertRaises(ValueError):
            LLMConfig(model="")

    def test_llm_config_raises_for_whitespace_only_model(self) -> None:
        from ai_test_strategy_generator.models import LLMConfig

        with self.assertRaises(ValueError):
            LLMConfig(model="   ")

    def test_llm_config_raises_for_non_positive_max_tokens(self) -> None:
        from ai_test_strategy_generator.models import LLMConfig

        with self.assertRaises(ValueError):
            LLMConfig(model="gpt-5.4", max_tokens=0)

    def test_llm_config_raises_for_negative_max_tokens(self) -> None:
        from ai_test_strategy_generator.models import LLMConfig

        with self.assertRaises(ValueError):
            LLMConfig(model="gpt-5.4", max_tokens=-1)

    def test_llm_config_raises_for_temperature_above_range(self) -> None:
        from ai_test_strategy_generator.models import LLMConfig

        with self.assertRaises(ValueError):
            LLMConfig(model="gpt-5.4", temperature=2.1)

    def test_llm_config_raises_for_negative_temperature(self) -> None:
        from ai_test_strategy_generator.models import LLMConfig

        with self.assertRaises(ValueError):
            LLMConfig(model="gpt-5.4", temperature=-0.1)

    def test_llm_config_accepts_boundary_temperature_zero(self) -> None:
        from ai_test_strategy_generator.models import LLMConfig

        config = LLMConfig(model="gpt-5.4", temperature=0.0)

        self.assertAlmostEqual(config.temperature, 0.0)

    def test_llm_config_accepts_boundary_temperature_two(self) -> None:
        from ai_test_strategy_generator.models import LLMConfig

        config = LLMConfig(model="gpt-5.4", temperature=2.0)

        self.assertAlmostEqual(config.temperature, 2.0)


class CliModeTests(unittest.TestCase):
    def test_cli_defaults_to_deterministic_mode(self) -> None:
        from ai_test_strategy_generator.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["input.yaml"])

        self.assertEqual(args.mode, "deterministic")

    def test_cli_accepts_deterministic_flag(self) -> None:
        from ai_test_strategy_generator.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["--mode", "deterministic", "input.yaml"])

        self.assertEqual(args.mode, "deterministic")

    def test_cli_accepts_llm_assisted_flag(self) -> None:
        from ai_test_strategy_generator.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["--mode", "llm_assisted", "input.yaml"])

        self.assertEqual(args.mode, "llm_assisted")

    def test_cli_rejects_invalid_mode_value(self) -> None:
        from ai_test_strategy_generator.cli import build_parser

        parser = build_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args(["--mode", "auto", "input.yaml"])


if __name__ == "__main__":
    unittest.main()
