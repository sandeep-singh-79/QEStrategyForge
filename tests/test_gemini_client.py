from __future__ import annotations

import json
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from ai_test_strategy_generator.llm_client import GenerationRequest
from ai_test_strategy_generator.models import ProviderConfig
from ai_test_strategy_generator.gemini_client import GeminiClient


def _make_response(body: dict) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(body).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


_VALID_RESPONSE = {
    "candidates": [
        {
            "content": {
                "parts": [{"text": "Generated strategy text."}]
            }
        }
    ]
}


class TestGeminiClientSuccess(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ProviderConfig(
            provider="gemini",
            model="gemini-2.0-flash",
            base_url="https://generativelanguage.googleapis.com",
            api_key="AIza-test",
        )
        self.client = GeminiClient(self.config)
        self.request = GenerationRequest(
            prompt="Write a test strategy.",
            model="gemini-2.0-flash",
            max_tokens=512,
        )

    def test_returns_generation_response(self) -> None:
        with patch("urllib.request.urlopen", return_value=_make_response(_VALID_RESPONSE)):
            result = self.client.generate(self.request)
        self.assertEqual(result.text, "Generated strategy text.")
        self.assertEqual(result.model, "gemini-2.0-flash")

    def test_posts_to_correct_url(self) -> None:
        with patch("urllib.request.urlopen", return_value=_make_response(_VALID_RESPONSE)) as m:
            self.client.generate(self.request)
        req = m.call_args[0][0]
        self.assertIn("generateContent", req.full_url)
        self.assertIn("gemini-2.0-flash", req.full_url)
        self.assertIn("AIza-test", req.full_url)
        self.assertEqual(req.get_method(), "POST")

    def test_request_body_contains_prompt(self) -> None:
        with patch("urllib.request.urlopen", return_value=_make_response(_VALID_RESPONSE)) as m:
            self.client.generate(self.request)
        body = json.loads(m.call_args[0][0].data.decode())
        self.assertEqual(body["contents"][0]["parts"][0]["text"], "Write a test strategy.")
        self.assertEqual(body["generationConfig"]["maxOutputTokens"], 512)

    def test_temperature_passed_in_generation_config(self) -> None:
        config = ProviderConfig(
            provider="gemini",
            model="gemini-2.0-flash",
            api_key="key",
            temperature=0.5,
        )
        client = GeminiClient(config)
        with patch("urllib.request.urlopen", return_value=_make_response(_VALID_RESPONSE)) as m:
            client.generate(self.request)
        body = json.loads(m.call_args[0][0].data.decode())
        self.assertAlmostEqual(body["generationConfig"]["temperature"], 0.5)


class TestGeminiClientErrors(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ProviderConfig(
            provider="gemini",
            model="gemini-2.0-flash",
            api_key="AIza-test",
        )
        self.client = GeminiClient(self.config)
        self.request = GenerationRequest(
            prompt="test", model="gemini-2.0-flash", max_tokens=256
        )

    def test_missing_api_key_raises_value_error(self) -> None:
        config = ProviderConfig(provider="gemini", model="gemini-2.0-flash", api_key=None)
        with self.assertRaises(ValueError) as ctx:
            GeminiClient(config)
        self.assertIn("api_key", str(ctx.exception).lower())

    def test_empty_candidates_raises_runtime_error(self) -> None:
        bad = {"candidates": []}
        with patch("urllib.request.urlopen", return_value=_make_response(bad)):
            with self.assertRaises(RuntimeError):
                self.client.generate(self.request)

    def test_malformed_json_raises_runtime_error(self) -> None:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not-json"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            with self.assertRaises(RuntimeError):
                self.client.generate(self.request)

    def test_url_error_raises_runtime_error(self) -> None:
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("network unreachable"),
        ):
            with self.assertRaises(RuntimeError):
                self.client.generate(self.request)

    def test_http_error_raises_runtime_error(self) -> None:
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.HTTPError(
                url="https://generativelanguage.googleapis.com",
                code=403,
                msg="Forbidden",
                hdrs={},  # type: ignore[arg-type]
                fp=None,
            ),
        ):
            with self.assertRaises(RuntimeError):
                self.client.generate(self.request)


if __name__ == "__main__":
    unittest.main()
