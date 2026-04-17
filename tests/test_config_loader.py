from __future__ import annotations

import os
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from ai_test_strategy_generator.config_loader import load_config
from ai_test_strategy_generator.models import ProviderConfig


class TestProviderConfig(unittest.TestCase):
    """ProviderConfig dataclass validation."""

    def test_defaults_applied(self) -> None:
        cfg = ProviderConfig()
        self.assertEqual(cfg.provider, "ollama")
        self.assertEqual(cfg.model, "glm4:latest")
        self.assertEqual(cfg.base_url, "http://localhost:11434")
        self.assertIsNone(cfg.api_key)
        self.assertEqual(cfg.temperature, 0.0)
        self.assertEqual(cfg.max_tokens, 4096)

    def test_custom_values(self) -> None:
        cfg = ProviderConfig(
            provider="openai",
            model="gpt-4o",
            base_url="https://api.openai.com",
            api_key="sk-test",
            temperature=0.7,
            max_tokens=2048,
        )
        self.assertEqual(cfg.provider, "openai")
        self.assertEqual(cfg.api_key, "sk-test")

    def test_invalid_temperature_low(self) -> None:
        with self.assertRaises(ValueError):
            ProviderConfig(temperature=-0.1)

    def test_invalid_temperature_high(self) -> None:
        with self.assertRaises(ValueError):
            ProviderConfig(temperature=2.1)

    def test_invalid_max_tokens(self) -> None:
        with self.assertRaises(ValueError):
            ProviderConfig(max_tokens=0)

    def test_empty_provider_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ProviderConfig(provider="")

    def test_empty_model_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ProviderConfig(model="")


class TestLoadConfig(unittest.TestCase):
    """load_config returns correct dict from YAML + env vars."""

    def test_returns_defaults_when_no_file(self, tmp_path: Path | None = None) -> None:
        result = load_config(None)
        self.assertIn("provider", result)
        self.assertEqual(result["provider"], "ollama")

    def test_valid_yaml_loaded(self) -> None:
        import tempfile

        yaml_content = textwrap.dedent("""\
            provider: openai
            model: gpt-4o
            temperature: 0.3
            max_tokens: 2048
        """)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(yaml_content)
            tmp_path = Path(f.name)
        try:
            result = load_config(tmp_path)
            self.assertEqual(result["provider"], "openai")
            self.assertEqual(result["model"], "gpt-4o")
            self.assertAlmostEqual(result["temperature"], 0.3)
            self.assertEqual(result["max_tokens"], 2048)
        finally:
            tmp_path.unlink()

    def test_missing_file_uses_defaults(self) -> None:
        result = load_config(Path("/nonexistent/strategy.config.yaml"))
        self.assertEqual(result["provider"], "ollama")

    def test_env_var_overrides_yaml(self) -> None:
        import tempfile

        yaml_content = "provider: ollama\nmodel: glm4:latest\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(yaml_content)
            tmp_path = Path(f.name)
        try:
            with patch.dict(
                os.environ,
                {"STRATEGY_LLM_PROVIDER": "openai", "STRATEGY_LLM_MODEL": "gpt-4o"},
            ):
                result = load_config(tmp_path)
            self.assertEqual(result["provider"], "openai")
            self.assertEqual(result["model"], "gpt-4o")
        finally:
            tmp_path.unlink()

    def test_api_key_in_file_is_ignored_with_warning(self) -> None:
        import tempfile

        yaml_content = textwrap.dedent("""\
            provider: openai
            model: gpt-4o
            api_key: sk-secret
        """)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(yaml_content)
            tmp_path = Path(f.name)
        try:
            import warnings

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                result = load_config(tmp_path)
            self.assertNotIn("api_key", result)
            self.assertTrue(
                any("api_key" in str(w.message).lower() for w in caught),
                "Expected a warning about api_key in config file",
            )
        finally:
            tmp_path.unlink()

    def test_env_api_key_not_in_result_dict(self) -> None:
        """API key from env var ends up in ProviderConfig, not in the raw config dict."""
        with patch.dict(os.environ, {"STRATEGY_LLM_API_KEY": "sk-from-env"}):
            result = load_config(None)
        # api_key is surfaced only through ProviderConfig construction, not raw dict
        self.assertNotIn("api_key", result)

    def test_base_url_env_var_applied(self) -> None:
        with patch.dict(
            os.environ,
            {"STRATEGY_LLM_BASE_URL": "http://custom-host:8080"},
        ):
            result = load_config(None)
        self.assertEqual(result["base_url"], "http://custom-host:8080")

    def test_temperature_env_var_is_float(self) -> None:
        with patch.dict(os.environ, {"STRATEGY_LLM_TEMPERATURE": "0.7"}):
            result = load_config(None)
        self.assertAlmostEqual(result["temperature"], 0.7)

    def test_max_tokens_env_var_is_int(self) -> None:
        with patch.dict(os.environ, {"STRATEGY_LLM_MAX_TOKENS": "1024"}):
            result = load_config(None)
        self.assertEqual(result["max_tokens"], 1024)

    def test_invalid_yaml_warns_and_uses_defaults(self) -> None:
        import tempfile
        import warnings

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(": invalid: yaml: {")
            tmp_path = Path(f.name)
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                result = load_config(tmp_path)
            self.assertEqual(result["provider"], "ollama")  # fell back to defaults
            self.assertTrue(
                any("Could not parse" in str(w.message) for w in caught),
                "Expected a warning about unparseable config",
            )
        finally:
            tmp_path.unlink()

    def test_bad_env_var_cast_warns_and_keeps_previous_value(self) -> None:
        import warnings

        with patch.dict(os.environ, {"STRATEGY_LLM_TEMPERATURE": "not-a-float"}):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                result = load_config(None)
        self.assertAlmostEqual(result["temperature"], 0.0)  # default retained
        self.assertTrue(
            any("STRATEGY_LLM_TEMPERATURE" in str(w.message) for w in caught),
            "Expected a warning about bad env var cast",
        )


class TestBuildProviderConfig(unittest.TestCase):
    """Integration between load_config and ProviderConfig construction."""

    def test_build_from_defaults(self) -> None:
        raw = load_config(None)
        cfg = ProviderConfig(**raw)
        self.assertEqual(cfg.provider, "ollama")

    def test_build_with_all_env_vars(self) -> None:
        with patch.dict(
            os.environ,
            {
                "STRATEGY_LLM_PROVIDER": "gemini",
                "STRATEGY_LLM_MODEL": "gemini-2.0-flash",
                "STRATEGY_LLM_BASE_URL": "https://generativelanguage.googleapis.com",
                "STRATEGY_LLM_TEMPERATURE": "0.5",
                "STRATEGY_LLM_MAX_TOKENS": "1024",
            },
        ):
            raw = load_config(None)
        cfg = ProviderConfig(**raw)
        self.assertEqual(cfg.provider, "gemini")
        self.assertEqual(cfg.model, "gemini-2.0-flash")
        self.assertAlmostEqual(cfg.temperature, 0.5)


if __name__ == "__main__":
    unittest.main()
