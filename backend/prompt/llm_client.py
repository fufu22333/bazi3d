import json
import os
from typing import Callable

import httpx


JSON_ONLY_SYSTEM_MESSAGE = (
    "你只能输出纯 JSON 对象，不能有任何 Markdown、不能有 ```json 代码块、"
    "不能有任何前缀或后缀文字，只有 JSON 本身"
)


class DeepSeekClient:
    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 30.0,
        retry_count: int = 3,
        endpoint: str = "https://api.deepseek.com/chat/completions",
    ) -> None:
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.timeout = timeout
        self.retry_count = retry_count
        self.endpoint = endpoint

    def _post(self, *, messages: list[dict[str, str]]) -> str:
        response = httpx.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": messages,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]

    def generate_text(self, prompt: str) -> str:
        return self._post(messages=[{"role": "user", "content": prompt}])

    def generate_json(
        self,
        prompt: str,
        system_message: str = JSON_ONLY_SYSTEM_MESSAGE,
        post_callable: Callable[..., str] | None = None,
    ) -> dict:
        post_callable = post_callable or self._post
        last_error: Exception | None = None
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]

        for _ in range(self.retry_count):
            try:
                raw_response = post_callable(messages=messages)
                cleaned = raw_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[len("```json") :].strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned[len("```") :].strip()
                if cleaned.endswith("```"):
                    cleaned = cleaned[: -len("```")].strip()
                return json.loads(cleaned)
            except (httpx.HTTPError, httpx.TimeoutException, json.JSONDecodeError) as exc:
                last_error = exc

        if last_error is not None:
            raise last_error
        raise RuntimeError("DeepSeek request failed")
