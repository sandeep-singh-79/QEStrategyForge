from __future__ import annotations

import json
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from ai_test_strategy_generator.llm_client import GenerationRequest
from ai_test_strategy_generator.models import ProviderConfig
from ai_test_strategy_generator.openai_client import OpenAIClient


def _make_response(body: dict) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(body).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


_VALID_RESPONSE = {
    "choices": [{"message": {"content": "Generated strategy text."}}],
    "model": "gpt-4o",
}


class TestOpenAIClientSuccess(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ProviderConfig(
            provider="openai",
            model="gpt-4o",
            base_url="https://api.openai.com",
            api_key="sk-test",
        )
        self.client = OpenAIClient(self.config)
        self.request = GenerationRequest(
            prompt="Write a test strategy.",
            model="gpt-4o",
            max_tokens=512,
        )

    def test_returns_generation_response(self) -> None:
        with patch("urllib.request.urlopen", return_value=_make_response(_VALID_RESPONSE)):
            result = self.client.generate(self.request)
        self.assertEqual(result.text, "Generated strategy text.")
        self.assertEqual(result.model, "gpt-4o")

    def test_posts_to_correct_url(self) -> None:
        with patch("urllib.request.urlopen", return_value=_make_response(_VALID_RESPONSE)) as m:
            self.client.generate(self.request)
        req = m.call_args[0][0]
        self.assertIn("/v1/chat/completions", req.full_url)
        self.assertEqual(req.get_method(), "POST")

    def test_authorization_header_set(self) -> None:
        with patch("urllib.request.urlopen", return_value=_make_response(_VALID_RESPONSE)) as m:
            self.client.generate(self.request)
        req = m.call_args[0][0]
        self.assertEqual(req.get_header("Authorization"), "Bearer sk-test")

    def test_request_body_contains_messages(self) -> None:
        with patch("urllib.request.urlopen", return_value=_make_response(_VALID_RESPONSE)) as m:
            self.client.generate(self.request)
        body = json.loads(m.call_args[0][0].data.decode())
        self.assertEqual(body["model"], "gpt-4o")
        self.assertEqual(body["messages"][0]["role"], "user")
        self.assertEqual(body["messages"][0]["content"], "Write a test strategy.")
        self.assertEqual(body["max_tokens"], 512)


class TestOpenAIClientErrors(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ProviderConfig(
            provider="openai",
            model="gpt-4o",
            api_key="sk-test",
        )
        self.client = OpenAIClient(self.config)
        self.request = GenerationRequest(prompt="test", model="gpt-4o", max_tokens=256)

    def test_missing_api_key_raises_value_error(self) -> None:
        config = ProviderConfig(provider="openai", model="gpt-4o", api_key=None)
        with self.assertRaises(ValueError) as ctx:
            OpenAIClient(config)
        self.assertIn("api_key", str(ctx.exception).lower())

    def test_http_error_raises_runtime_error(self) -> None:
        import http.client
        from io import BytesIO

        err_resp = MagicMock()
        err_resp.read.return_value = b'{"error": "unauthorized"}'
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.HTTPError(
                url="https://api.openai.com",
                code=401,
                msg="Unauthorized",
                hdrs={},  # type: ignore[arg-type]
                fp=None,
            ),
        ):
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

    def test_malformed_choices_raises_runtime_error(self) -> None:
        bad = {"choices": []}
        with patch("urllib.request.urlopen", return_value=_make_response(bad)):
            with self.assertRaises(RuntimeError):
                self.client.generate(self.request)

    def test_url_error_raises_runtime_error(self) -> None:
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            with self.assertRaises(RuntimeError):
                self.client.generate(self.request)


if __name__ == "__main__":
    unittest.main()
