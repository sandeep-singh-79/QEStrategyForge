"""OpenAI-compatible LLM client — implements LLMClient Protocol using stdlib urllib."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from ai_test_strategy_generator.llm_client import GenerationRequest, GenerationResponse
from ai_test_strategy_generator.models import ProviderConfig


class OpenAIClient:
    """LLMClient implementation for OpenAI-compatible REST APIs.

    API: POST {base_url}/v1/chat/completions
    Compatible with OpenAI, Azure OpenAI, and any OpenAI-compatible endpoint.
    """

    def __init__(self, config: ProviderConfig) -> None:
        if not config.api_key:
            raise ValueError(
                "OpenAIClient requires an api_key. "
                "Set the STRATEGY_LLM_API_KEY environment variable."
            )
        self._config = config
        self._url = f"{config.base_url.rstrip('/')}/v1/chat/completions"

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        body: dict[str, Any] = {
            "model": request.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens,
            "temperature": self._config.temperature,
        }
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            self._url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._config.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            raise RuntimeError(
                f"OpenAI API returned HTTP {exc.code}: {exc.msg}"
            ) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(
                f"OpenAI request to {self._url} failed: {exc}"
            ) from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"OpenAI returned non-JSON response: {raw[:200]!r}"
            ) from exc

        try:
            text: str = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(
                f"Unexpected OpenAI response structure: {payload}"
            ) from exc

        if not text:
            raise RuntimeError(f"OpenAI returned an empty content field: {payload}")

        return GenerationResponse(text=text, model=request.model)
