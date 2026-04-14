import unittest

import httpx


class MeshyAdapterTestCase(unittest.TestCase):
    def test_submit_returns_task_id(self) -> None:
        from backend.adapters.meshy_adapter import MeshyAdapter

        def fake_request(method: str, url: str, **kwargs):
            self.assertEqual(method, "POST")
            self.assertEqual(url, "https://api.meshy.ai/openapi/v2/text-to-3d")
            self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-key")
            self.assertEqual(kwargs["json"]["prompt"], "a floating spirit")
            self.assertEqual(kwargs["json"]["mode"], "preview")
            return {"result": "task-123"}

        adapter = MeshyAdapter(api_key="test-key", request_callable=fake_request)

        task_id = adapter.submit({"prompt": "a floating spirit"}, {"mode": "preview"})

        self.assertEqual(task_id, "task-123")

    def test_query_returns_raw_provider_payload(self) -> None:
        from backend.adapters.meshy_adapter import MeshyAdapter

        def fake_request(method: str, url: str, **kwargs):
            self.assertEqual(method, "GET")
            self.assertEqual(
                url, "https://api.meshy.ai/openapi/v2/text-to-3d/task-123"
            )
            self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-key")
            return {
                "id": "task-123",
                "status": "SUCCEEDED",
                "model_urls": {"glb": "https://assets.meshy.ai/model.glb"},
            }

        adapter = MeshyAdapter(api_key="test-key", request_callable=fake_request)

        result = adapter.query("task-123")

        self.assertEqual(result["id"], "task-123")
        self.assertEqual(result["status"], "SUCCEEDED")

    def test_normalize_returns_unified_structure(self) -> None:
        from backend.adapters.meshy_adapter import MeshyAdapter

        adapter = MeshyAdapter(api_key="test-key")

        normalized = adapter.normalize(
            {
                "id": "task-123",
                "status": "SUCCEEDED",
                "model_urls": {"glb": "https://assets.meshy.ai/model.glb"},
                "thumbnail_url": "https://assets.meshy.ai/preview.png",
            }
        )

        self.assertEqual(
            normalized,
            {
                "url": "https://assets.meshy.ai/model.glb",
                "format": "glb",
                "metadata": {
                    "provider": "meshy",
                    "task_id": "task-123",
                    "status": "SUCCEEDED",
                    "thumbnail_url": "https://assets.meshy.ai/preview.png",
                },
            },
        )

    def test_http_error_is_mapped_to_unified_exception(self) -> None:
        from backend.adapters.meshy_adapter import MeshyAdapter, ModelProviderError

        def fake_request(method: str, url: str, **kwargs):
            raise httpx.HTTPError("network error")

        adapter = MeshyAdapter(api_key="test-key", request_callable=fake_request)

        with self.assertRaises(ModelProviderError):
            adapter.submit({"prompt": "a floating spirit"}, {"mode": "preview"})


if __name__ == "__main__":
    unittest.main()
