import unittest


class EvaluationApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        from backend.app import create_app

        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
                "JWT_SECRET_KEY": "evaluation-secret",
            }
        )
        self.client = self.app.test_client()
        suffix = self.id().split(".")[-1]
        self.owner_token = self._register_user(
            email=f"owner-{suffix}@example.com",
            username=f"owner-{suffix}",
        )
        self.other_token = self._register_user(
            email=f"other-{suffix}@example.com",
            username=f"other-{suffix}",
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

    def _create_task(self, token: str) -> int:
        response = self.client.post(
            "/api/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "display_name": "Eval User",
                "gender": "female",
                "birth_location": "Shanghai",
                "style_profile": {"fashion_style": "minimal"},
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()["id"]

    def _create_work(self, token: str, url: str) -> int:
        asset_response = self.client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "source_url": url,
                "file_format": "glb",
                "metadata": {"source": "eval-test"},
            },
        )
        self.assertEqual(asset_response.status_code, 201)
        asset_id = asset_response.get_json()["id"]

        work_response = self.client.post(
            "/api/works",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "asset_id": asset_id,
                "title": "Eval Work",
                "visibility": "public",
            },
        )
        self.assertEqual(work_response.status_code, 201)
        return work_response.get_json()["id"]

    def test_create_task_evaluation_log(self) -> None:
        task_id = self._create_task(self.owner_token)

        response = self.client.post(
            "/api/evaluations",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "generation_task_id": task_id,
                "level": "text",
                "metrics": {"latency_ms": 1200, "schema_valid": True},
                "subjective_score": 4,
            },
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload["level"], "text")
        self.assertEqual(payload["generation_task_id"], task_id)
        self.assertEqual(payload["metrics"]["latency_ms"], 1200)
        self.assertEqual(payload["subjective_score"], 4)

    def test_create_work_evaluation_log(self) -> None:
        work_id = self._create_work(
            self.owner_token,
            "https://example.com/models/eval-work.glb",
        )

        response = self.client.post(
            "/api/evaluations",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "work_id": work_id,
                "level": "3d",
                "metrics": {"triangle_count": 1024, "format": "glb"},
            },
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload["level"], "3d")
        self.assertEqual(payload["work_id"], work_id)
        self.assertEqual(payload["metrics"]["triangle_count"], 1024)

    def test_list_evaluations_by_task(self) -> None:
        task_id = self._create_task(self.owner_token)
        self.client.post(
            "/api/evaluations",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "generation_task_id": task_id,
                "level": "pipeline",
                "metrics": {"total_latency_ms": 3000},
            },
        )

        response = self.client.get(
            f"/api/evaluations?generation_task_id={task_id}",
            headers={"Authorization": f"Bearer {self.owner_token}"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(len(payload["items"]), 1)
        self.assertEqual(payload["items"][0]["level"], "pipeline")

    def test_create_evaluation_rejects_invalid_level(self) -> None:
        task_id = self._create_task(self.owner_token)

        response = self.client.post(
            "/api/evaluations",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "generation_task_id": task_id,
                "level": "audio",
                "metrics": {"latency_ms": 100},
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_create_evaluation_rejects_non_owner_target(self) -> None:
        task_id = self._create_task(self.owner_token)

        response = self.client.post(
            "/api/evaluations",
            headers={"Authorization": f"Bearer {self.other_token}"},
            json={
                "generation_task_id": task_id,
                "level": "text",
                "metrics": {"latency_ms": 100},
            },
        )

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
