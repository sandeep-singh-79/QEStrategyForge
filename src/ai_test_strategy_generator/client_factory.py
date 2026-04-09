"""Factory function for creating LLMClient instances by provider name."""
from __future__ import annotations

from ai_test_strategy_generator.gemini_client import GeminiClient
from ai_test_strategy_generator.llm_client import LLMClient
from ai_test_strategy_generator.models import ProviderConfig
from ai_test_strategy_generator.ollama_client import OllamaClient
from ai_test_strategy_generator.openai_client import OpenAIClient

_SUPPORTED_PROVIDERS: frozenset[str] = frozenset({"ollama", "openai", "gemini"})


def create_llm_client(config: ProviderConfig) -> LLMClient:
    """Return the correct LLMClient implementation for the given provider.

    Parameters
    ----------
    config:
        A fully resolved ProviderConfig.  The factory validates that API keys
        are present for providers that require them (openai, gemini).

    Raises
    ------
    ValueError
        If the provider is unknown or required credentials are missing.
    """
    provider = config.provider.lower()

    if provider == "ollama":
        return OllamaClient(config)
    if provider == "openai":
        return OpenAIClient(config)  # raises ValueError internally if api_key missing
    if provider == "gemini":
        return GeminiClient(config)  # raises ValueError internally if api_key missing

    raise ValueError(
        f"Unsupported LLM provider: {provider!r}. "
        f"Supported providers: {sorted(_SUPPORTED_PROVIDERS)}"
    )
