from __future__ import annotations

import json
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch

from ai_test_strategy_generator.llm_client import GenerationRequest
from ai_test_strategy_generator.models import ProviderConfig
from ai_test_strategy_generator.ollama_client import OllamaClient


def _make_response(body: dict) -> MagicMock:
    """Return a mock that looks like an http.client.HTTPResponse."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(body).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


class TestOllamaClientSuccess(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ProviderConfig(
            provider="ollama",
            model="glm4:latest",
            base_url="http://localhost:11434",
        )
        self.client = OllamaClient(self.config)
        self.request = GenerationRequest(
            prompt="Write a test strategy.",
            model="glm4:latest",
            max_tokens=512,
        )

    def test_returns_generation_response(self) -> None:
        mock_resp = _make_response({"response": "Generated strategy text."})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = self.client.generate(self.request)
        self.assertEqual(result.text, "Generated strategy text.")
        self.assertEqual(result.model, "glm4:latest")

    def test_posts_to_correct_url(self) -> None:
        mock_resp = _make_response({"response": "ok"})
        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            self.client.generate(self.request)
        call_args = mock_open.call_args
        req = call_args[0][0]
        self.assertIn("/api/generate", req.full_url)
        self.assertEqual(req.get_method(), "POST")

    def test_request_body_contains_model_and_prompt(self) -> None:
        mock_resp = _make_response({"response": "ok"})
        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            self.client.generate(self.request)
        req = mock_open.call_args[0][0]
        body = json.loads(req.data.decode())
        self.assertEqual(body["model"], "glm4:latest")
        self.assertEqual(body["prompt"], "Write a test strategy.")
        self.assertFalse(body["stream"])

    def test_max_tokens_passed_in_options(self) -> None:
        mock_resp = _make_response({"response": "ok"})
        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            self.client.generate(self.request)
        body = json.loads(mock_open.call_args[0][0].data.decode())
        self.assertEqual(body["options"]["num_predict"], 512)


class TestOllamaClientErrors(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ProviderConfig(provider="ollama", model="glm4:latest")
        self.client = OllamaClient(self.config)
        self.request = GenerationRequest(
            prompt="test", model="glm4:latest", max_tokens=256
        )

    def test_connection_error_raises_runtime_error(self) -> None:
        import urllib.error

        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            with self.assertRaises(RuntimeError) as ctx:
                self.client.generate(self.request)
        self.assertIn("Ollama", str(ctx.exception))

    def test_malformed_json_raises_runtime_error(self) -> None:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not-json"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            with self.assertRaises(RuntimeError):
                self.client.generate(self.request)

    def test_empty_response_field_raises_runtime_error(self) -> None:
        mock_resp = _make_response({"response": ""})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            with self.assertRaises(RuntimeError):
                self.client.generate(self.request)

    def test_missing_response_key_raises_runtime_error(self) -> None:
        mock_resp = _make_response({"other": "data"})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            with self.assertRaises(RuntimeError):
                self.client.generate(self.request)


if __name__ == "__main__":
    unittest.main()
