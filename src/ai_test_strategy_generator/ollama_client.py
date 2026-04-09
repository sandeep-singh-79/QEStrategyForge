"""Ollama LLM client — implements LLMClient Protocol using stdlib urllib."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from ai_test_strategy_generator.llm_client import GenerationRequest, GenerationResponse
from ai_test_strategy_generator.models import ProviderConfig


class OllamaClient:
    """LLMClient implementation for a local Ollama instance.

    API: POST {base_url}/api/generate
    Docs: https://github.com/ollama/ollama/blob/main/docs/api.md
    """

    def __init__(self, config: ProviderConfig) -> None:
        self._config = config
        self._url = f"{config.base_url.rstrip('/')}/api/generate"

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        body: dict[str, Any] = {
            "model": request.model,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "num_predict": request.max_tokens,
                "temperature": self._config.temperature,
            },
        }
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            self._url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                raw = resp.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(
                f"Ollama request to {self._url} failed: {exc}"
            ) from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Ollama returned non-JSON response: {raw[:200]!r}"
            ) from exc

        text: str = payload.get("response", "")
        if not text:
            raise RuntimeError(
                f"Ollama returned an empty or missing 'response' field: {payload}"
            )

        return GenerationResponse(text=text, model=request.model)
