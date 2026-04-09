from __future__ import annotations

import unittest


class GenerationRequestTests(unittest.TestCase):
    def test_request_created_with_required_fields(self) -> None:
        from ai_test_strategy_generator.llm_client import GenerationRequest

        req = GenerationRequest(prompt="test prompt", model="gpt-5.4")

        self.assertEqual(req.prompt, "test prompt")
        self.assertEqual(req.model, "gpt-5.4")
        self.assertEqual(req.max_tokens, 4096)

    def test_request_accepts_custom_max_tokens(self) -> None:
        from ai_test_strategy_generator.llm_client import GenerationRequest

        req = GenerationRequest(prompt="test", model="gemini-pro", max_tokens=2048)

        self.assertEqual(req.max_tokens, 2048)


class GenerationResponseTests(unittest.TestCase):
    def test_response_created_with_required_fields(self) -> None:
        from ai_test_strategy_generator.llm_client import GenerationResponse

        resp = GenerationResponse(text="some text", model="gpt-5.4")

        self.assertEqual(resp.text, "some text")
        self.assertEqual(resp.model, "gpt-5.4")


class FakeLLMClientTests(unittest.TestCase):
    def test_fake_client_generate_returns_response(self) -> None:
        from ai_test_strategy_generator.llm_client import FakeLLMClient, GenerationRequest

        client = FakeLLMClient()
        req = GenerationRequest(prompt="ignored", model="fake")
        resp = client.generate(req)

        self.assertIsNotNone(resp)
        self.assertIsInstance(resp.text, str)
        self.assertGreater(len(resp.text), 0)

    def test_fake_client_response_text_passes_structural_validation(self) -> None:
        from ai_test_strategy_generator.llm_client import FakeLLMClient, GenerationRequest
        from ai_test_strategy_generator.output_validator import validate_output

        client = FakeLLMClient()
        req = GenerationRequest(prompt="ignored", model="fake")
        resp = client.generate(req)
        result = validate_output(resp.text)

        self.assertTrue(result.is_valid, f"FakeLLMClient output failed validation: {result.errors}")

    def test_fake_client_response_model_matches_request(self) -> None:
        from ai_test_strategy_generator.llm_client import FakeLLMClient, GenerationRequest

        client = FakeLLMClient()
        req = GenerationRequest(prompt="ignored", model="my-model")
        resp = client.generate(req)

        self.assertEqual(resp.model, "my-model")

    def test_fake_client_satisfies_llm_client_protocol(self) -> None:
        from ai_test_strategy_generator.llm_client import FakeLLMClient, LLMClient, GenerationRequest

        client: LLMClient = FakeLLMClient()
        req = GenerationRequest(prompt="test", model="fake")
        resp = client.generate(req)

        self.assertIsNotNone(resp.text)

    def test_fake_client_is_deterministic(self) -> None:
        from ai_test_strategy_generator.llm_client import FakeLLMClient, GenerationRequest

        client = FakeLLMClient()
        req = GenerationRequest(prompt="any", model="fake")

        resp1 = client.generate(req)
        resp2 = client.generate(req)

        self.assertEqual(resp1.text, resp2.text)


class LLMClientProtocolTests(unittest.TestCase):
    def test_protocol_accepts_any_implementing_class(self) -> None:
        from ai_test_strategy_generator.llm_client import (
            LLMClient,
            GenerationRequest,
            GenerationResponse,
        )

        class CustomClient:
            def generate(self, request: GenerationRequest) -> GenerationResponse:
                return GenerationResponse(text="custom", model=request.model)

        client: LLMClient = CustomClient()
        req = GenerationRequest(prompt="x", model="custom")
        resp = client.generate(req)

        self.assertEqual(resp.text, "custom")


if __name__ == "__main__":
    unittest.main()
