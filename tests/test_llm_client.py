import os
import unittest
from unittest.mock import patch

import httpx


class DeepSeekClientTestCase(unittest.TestCase):
    def test_client_reads_api_key_from_environment(self) -> None:
        from backend.prompt.llm_client import DeepSeekClient

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "env-key"}, clear=True):
            client = DeepSeekClient()

        self.assertEqual(client.api_key, "env-key")

    def test_generate_json_retries_and_parses_response(self) -> None:
        from backend.prompt.llm_client import DeepSeekClient

        client = DeepSeekClient(api_key="test-key", retry_count=2)
        attempts = {"count": 0}

        def fake_post(**_: dict):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise httpx.TimeoutException("timeout")
            return '{"version":"v1","status":"ok"}'

        result = client.generate_json("hello", post_callable=fake_post)

        self.assertEqual(attempts["count"], 2)
        self.assertEqual(result["version"], "v1")
        self.assertEqual(result["status"], "ok")

    def test_generate_json_strips_markdown_code_fences(self) -> None:
        from backend.prompt.llm_client import DeepSeekClient

        client = DeepSeekClient(api_key="test-key")

        result = client.generate_json(
            "hello",
            post_callable=lambda **_: '```json\n{"version":"v1","status":"ok"}\n```',
        )

        self.assertEqual(result["version"], "v1")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
