import unittest


class FakeTencentClient:
    def __init__(self) -> None:
        self.calls = []

    def call_json(self, action: str, payload: dict):
        self.calls.append((action, payload))
        return {"Response": {"JobId": "job-123"}}


class Hunyuan3DAdapterTestCase(unittest.TestCase):
    def test_submit_job_truncates_at_sentence_boundary_within_limit(self) -> None:
        from backend.adapters.hunyuan3d_adapter import Hunyuan3DAdapter

        client = FakeTencentClient()
        adapter = Hunyuan3DAdapter(
            secret_id="test-id",
            secret_key="test-key",
            client=client,
        )

        prompt = ("A" * 700) + ". " + ("B" * 500) + ". trailing sentence"

        job_id = adapter.submit_job(prompt)

        self.assertEqual(job_id, "job-123")
        action, payload = client.calls[0]
        self.assertEqual(action, "SubmitHunyuanTo3DProJob")
        self.assertLessEqual(len(payload["Prompt"]), 1024)
        self.assertTrue(payload["Prompt"].endswith("."))
        self.assertNotIn("trailing sentence", payload["Prompt"])


if __name__ == "__main__":
    unittest.main()
