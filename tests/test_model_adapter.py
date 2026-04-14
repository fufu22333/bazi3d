import unittest


class FakeAdapterContractTestCase(unittest.TestCase):
    def test_fake_adapter_satisfies_interface_contract(self) -> None:
        from backend.adapters.model_adapter import ModelAdapter

        class FakeAdapter(ModelAdapter):
            def submit(self, prompt: dict, config: dict) -> str:
                return "task-123"

            def query(self, task_id: str) -> dict:
                return {"raw_task_id": task_id}

        adapter = FakeAdapter()

        self.assertEqual(adapter.submit({"prompt": "demo"}, {}), "task-123")
        self.assertEqual(adapter.query("task-123"), {"raw_task_id": "task-123"})

        normalized = adapter.normalize(
            {
                "url": "https://example.com/model.glb",
                "format": "glb",
                "metadata": {"provider_task_id": "task-123"},
            }
        )

        self.assertEqual(
            normalized,
            {
                "url": "https://example.com/model.glb",
                "format": "glb",
                "metadata": {"provider_task_id": "task-123"},
            },
        )

    def test_normalize_rejects_invalid_payload(self) -> None:
        from backend.adapters.model_adapter import ModelAdapter

        class FakeAdapter(ModelAdapter):
            def submit(self, prompt: dict, config: dict) -> str:
                return "task-123"

            def query(self, task_id: str) -> dict:
                return {"raw_task_id": task_id}

        adapter = FakeAdapter()

        with self.assertRaises(ValueError):
            adapter.normalize({"url": "https://example.com/model.glb", "format": "glb"})


if __name__ == "__main__":
    unittest.main()
