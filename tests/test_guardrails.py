import unittest


class Task63GuardrailsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        from backend.app import create_app

        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
                "JWT_SECRET_KEY": "guardrails-secret",
            }
        )
        self.client = self.app.test_client()
        suffix = self.id().split(".")[-1]
        self.owner_token = self._register_user(
            email=f"owner-{suffix}@example.com",
            username=f"owner-{suffix}",
        )

    def tearDown(self) -> None:
        from backend.models import SessionLocal

        SessionLocal.remove()

    def _register_user(self, email: str, username: str) -> str:
        response = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "username": username,
                "password": "pass1234",
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()["token"]

    def _create_task(self) -> int:
        response = self.client.post(
            "/api/tasks",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "display_name": "Guard Test",
                "gender": "female",
                "birth_location": "Shanghai",
                "style_profile": {"fashion_style": "minimal", "spirit_style": "mist"},
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()["id"]

    def _create_asset(self) -> int:
        response = self.client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "source_url": "https://example.com/models/guardrails.glb",
                "file_format": "glb",
                "metadata": {"source": "test"},
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()["id"]

    def _assert_unified_error_shape(self, response, expected_status: int) -> dict:
        self.assertEqual(response.status_code, expected_status)
        payload = response.get_json()
        self.assertIn("error", payload)
        self.assertIn("code", payload["error"])
        self.assertIn("message", payload["error"])
        self.assertIn("request_id", payload["error"])
        self.assertIn("task_id", payload["error"])
        self.assertEqual(response.headers["X-Request-Id"], payload["error"]["request_id"])
        return payload

    def test_tasks_post_rejects_invalid_input_with_unified_error(self) -> None:
        response = self.client.post(
            "/api/tasks",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={"display_name": "", "style_profile": "bad"},
        )

        payload = self._assert_unified_error_shape(response, 400)
        self.assertEqual(payload["error"]["code"], "invalid_request")

    def test_assets_import_rejects_invalid_input_with_unified_error(self) -> None:
        response = self.client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "source_url": "https://example.com/models/bad.glb",
                "file_format": "glb",
                "metadata": "bad",
            },
        )

        payload = self._assert_unified_error_shape(response, 400)
        self.assertEqual(payload["error"]["code"], "invalid_request")

    def test_works_post_rejects_invalid_input_with_unified_error(self) -> None:
        asset_id = self._create_asset()

        response = self.client.post(
            "/api/works",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={"asset_id": asset_id, "title": ""},
        )

        payload = self._assert_unified_error_shape(response, 400)
        self.assertEqual(payload["error"]["code"], "invalid_request")

    def test_evaluations_post_rejects_invalid_input_and_logs_request_and_task_id(self) -> None:
        task_id = self._create_task()

        with self.assertLogs(self.app.logger.name, level="WARNING") as logs:
            response = self.client.post(
                "/api/evaluations",
                headers={"Authorization": f"Bearer {self.owner_token}"},
                json={
                    "generation_task_id": task_id,
                    "level": "audio",
                    "metrics": {"latency_ms": 100},
                },
            )

        payload = self._assert_unified_error_shape(response, 400)
        self.assertEqual(payload["error"]["task_id"], task_id)
        self.assertIn('"request_id"', logs.output[0])
        self.assertIn(f'"task_id": {task_id}', logs.output[0])

    def test_safe_generate_prompt_output_returns_fallback_and_logs_context(self) -> None:
        from backend.services.guardrails import safe_generate_prompt_output

        input_profile = {
            "display_name": "Fallback User",
            "style_profile": {
                "fashion_style": "minimal",
                "spirit_style": "mist",
            },
        }

        with self.assertLogs(self.app.logger.name, level="WARNING") as logs:
            result = safe_generate_prompt_output(
                input_profile=input_profile,
                llm_callable=lambda _: "{bad json",
                logger=self.app.logger,
                request_id="req-123",
                task_id=99,
            )

        self.assertEqual(result.version, "fallback-v1")
        self.assertEqual(result.character.style, "minimal")
        self.assertEqual(result.guardian_spirit.style, "mist")
        self.assertIn('"request_id": "req-123"', logs.output[0])
        self.assertIn('"task_id": 99', logs.output[0])

    def test_safe_normalize_model_output_uses_simple_fallback(self) -> None:
        from backend.adapters.model_adapter import ModelAdapter
        from backend.services.guardrails import safe_normalize_model_output

        class BrokenAdapter(ModelAdapter):
            def submit(self, prompt: dict, config: dict) -> str:
                return "x"

            def query(self, task_id: str) -> dict:
                return {}

            def normalize(self, result: dict) -> dict:
                raise ValueError("bad result")

        with self.assertLogs(self.app.logger.name, level="WARNING") as logs:
            normalized = safe_normalize_model_output(
                adapter=BrokenAdapter(),
                result={"model_urls": {"glb": "https://example.com/fallback.glb"}},
                logger=self.app.logger,
                request_id="req-456",
                task_id=7,
            )

        self.assertEqual(normalized["url"], "https://example.com/fallback.glb")
        self.assertEqual(normalized["format"], "glb")
        self.assertTrue(normalized["metadata"]["fallback"])
        self.assertEqual(normalized["metadata"]["task_id"], 7)
        self.assertIn('"request_id": "req-456"', logs.output[0])
        self.assertIn('"task_id": 7', logs.output[0])


if __name__ == "__main__":
    unittest.main()
