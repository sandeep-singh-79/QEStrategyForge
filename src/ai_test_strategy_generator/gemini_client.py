"""Gemini LLM client — implements LLMClient Protocol using stdlib urllib."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from ai_test_strategy_generator.llm_client import GenerationRequest, GenerationResponse
from ai_test_strategy_generator.models import ProviderConfig


class GeminiClient:
    """LLMClient implementation for Google Gemini REST API.

    API: POST {base_url}/v1beta/models/{model}:generateContent?key={api_key}
    Docs: https://ai.google.dev/api/generate-content
    """

    def __init__(self, config: ProviderConfig) -> None:
        if not config.api_key:
            raise ValueError(
                "GeminiClient requires an api_key. "
                "Set the STRATEGY_LLM_API_KEY environment variable."
            )
        self._config = config

    def __repr__(self) -> str:
        return (
            f"GeminiClient(provider={self._config.provider!r}, "
            f"model={self._config.model!r}, "
            f"base_url={self._config.base_url!r}, "
            f"api_key=***)"
        )

    def _build_url(self, model: str) -> str:
        # Google Gemini REST API requires the key as a query parameter.
        # Do NOT log or include this URL in error messages — it contains the API key.
        base = self._config.base_url.rstrip("/")
        return (
            f"{base}/v1beta/models/{model}:generateContent"
            f"?key={self._config.api_key}"
        )

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        url = self._build_url(request.model)
        body: dict[str, Any] = {
            "contents": [{"parts": [{"text": request.prompt}]}],
            "generationConfig": {
                "maxOutputTokens": request.max_tokens,
                "temperature": self._config.temperature,
            },
        }
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            raise RuntimeError(
                f"Gemini API returned HTTP {exc.code}: {exc.msg}"
            ) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(
                f"Gemini request failed: {exc}"
            ) from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Gemini returned non-JSON response: {raw[:200]!r}"
            ) from exc

        try:
            text: str = payload["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(
                f"Unexpected Gemini response structure: {payload}"
            ) from exc

        if not text:
            raise RuntimeError(f"Gemini returned an empty text field: {payload}")

        return GenerationResponse(text=text, model=request.model)
