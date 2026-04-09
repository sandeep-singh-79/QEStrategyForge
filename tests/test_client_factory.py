from __future__ import annotations

import unittest

from ai_test_strategy_generator.client_factory import create_llm_client
from ai_test_strategy_generator.gemini_client import GeminiClient
from ai_test_strategy_generator.models import ProviderConfig
from ai_test_strategy_generator.ollama_client import OllamaClient
from ai_test_strategy_generator.openai_client import OpenAIClient


class TestCreateLLMClient(unittest.TestCase):
    def test_ollama_returns_ollama_client(self) -> None:
        config = ProviderConfig(provider="ollama", model="glm4:latest")
        client = create_llm_client(config)
        self.assertIsInstance(client, OllamaClient)

    def test_openai_returns_openai_client(self) -> None:
        config = ProviderConfig(
            provider="openai", model="gpt-4o", api_key="sk-test"
        )
        client = create_llm_client(config)
        self.assertIsInstance(client, OpenAIClient)

    def test_gemini_returns_gemini_client(self) -> None:
        config = ProviderConfig(
            provider="gemini", model="gemini-2.0-flash", api_key="AIza-test"
        )
        client = create_llm_client(config)
        self.assertIsInstance(client, GeminiClient)

    def test_unknown_provider_raises_value_error(self) -> None:
        config = ProviderConfig(provider="anthropic", model="claude-4")
        with self.assertRaises(ValueError) as ctx:
            create_llm_client(config)
        self.assertIn("anthropic", str(ctx.exception).lower())

    def test_openai_without_api_key_raises_value_error(self) -> None:
        config = ProviderConfig(provider="openai", model="gpt-4o", api_key=None)
        with self.assertRaises(ValueError):
            create_llm_client(config)

    def test_gemini_without_api_key_raises_value_error(self) -> None:
        config = ProviderConfig(
            provider="gemini", model="gemini-2.0-flash", api_key=None
        )
        with self.assertRaises(ValueError):
            create_llm_client(config)

    def test_ollama_does_not_require_api_key(self) -> None:
        """Ollama is local — no API key required."""
        config = ProviderConfig(provider="ollama", model="glm4:latest", api_key=None)
        client = create_llm_client(config)  # must not raise
        self.assertIsInstance(client, OllamaClient)

    def test_returned_clients_satisfy_llm_client_protocol(self) -> None:
        from ai_test_strategy_generator.llm_client import LLMClient

        for config in [
            ProviderConfig(provider="ollama", model="glm4:latest"),
            ProviderConfig(provider="openai", model="gpt-4o", api_key="sk-x"),
            ProviderConfig(provider="gemini", model="gemini-2.0-flash", api_key="k"),
        ]:
            client = create_llm_client(config)
            self.assertIsInstance(client, LLMClient)


if __name__ == "__main__":
    unittest.main()
