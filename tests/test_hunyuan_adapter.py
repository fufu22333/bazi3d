import unittest

import httpx


class HunyuanAdapterTestCase(unittest.TestCase):
    def test_submit_returns_job_id(self) -> None:
        from backend.adapters.hunyuan_adapter import HunyuanAdapter

        def fake_request(method: str, url: str, **kwargs):
            self.assertEqual(method, "POST")
            self.assertEqual(url, "https://ai3d.tencentcloudapi.com/")
            self.assertEqual(kwargs["headers"]["X-TC-Action"], "SubmitHunyuanTo3DProJob")
            self.assertEqual(kwargs["json"]["Prompt"], "一只发光的守护灵")
            return {"Response": {"JobId": "job-123"}}

        adapter = HunyuanAdapter(
            secret_id="test-id",
            secret_key="test-key",
            request_callable=fake_request,
        )

        job_id = adapter.submit({"Prompt": "一只发光的守护灵"}, {"Model": "3.0"})

        self.assertEqual(job_id, "job-123")

    def test_query_returns_raw_provider_payload(self) -> None:
        from backend.adapters.hunyuan_adapter import HunyuanAdapter

        def fake_request(method: str, url: str, **kwargs):
            self.assertEqual(method, "POST")
            self.assertEqual(url, "https://ai3d.tencentcloudapi.com/")
            self.assertEqual(kwargs["headers"]["X-TC-Action"], "QueryHunyuanTo3DProJob")
            self.assertEqual(kwargs["json"]["JobId"], "job-123")
            return {
                "Response": {
                    "Status": "DONE",
                    "ResultFile3Ds": [
                        {
                            "Type": "GLB",
                            "Url": "https://cos.tencent.com/model.glb",
                            "PreviewImageUrl": "https://cos.tencent.com/preview.png",
                        }
                    ],
                }
            }

        adapter = HunyuanAdapter(
            secret_id="test-id",
            secret_key="test-key",
            request_callable=fake_request,
        )

        result = adapter.query("job-123")

        self.assertEqual(result["Response"]["Status"], "DONE")

    def test_normalize_returns_unified_structure(self) -> None:
        from backend.adapters.hunyuan_adapter import HunyuanAdapter

        adapter = HunyuanAdapter(secret_id="test-id", secret_key="test-key")

        normalized = adapter.normalize(
            {
                "Response": {
                    "Status": "DONE",
                    "ResultFile3Ds": [
                        {
                            "Type": "GLB",
                            "Url": "https://cos.tencent.com/model.glb",
                            "PreviewImageUrl": "https://cos.tencent.com/preview.png",
                        }
                    ],
                    "JobId": "job-123",
                }
            }
        )

        self.assertEqual(
            normalized,
            {
                "url": "https://cos.tencent.com/model.glb",
                "format": "glb",
                "metadata": {
                    "provider": "hunyuan",
                    "task_id": "job-123",
                    "status": "DONE",
                    "thumbnail_url": "https://cos.tencent.com/preview.png",
                },
            },
        )

    def test_http_error_is_mapped_to_unified_exception(self) -> None:
        from backend.adapters.hunyuan_adapter import HunyuanAdapter, ModelProviderError

        def fake_request(method: str, url: str, **kwargs):
            raise httpx.HTTPError("network error")

        adapter = HunyuanAdapter(
            secret_id="test-id",
            secret_key="test-key",
            request_callable=fake_request,
        )

        with self.assertRaises(ModelProviderError):
            adapter.query("job-123")


if __name__ == "__main__":
    unittest.main()
