import unittest
from unittest.mock import patch


class TaskApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        from backend.app import create_app

        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
                "JWT_SECRET_KEY": "task-secret",
            }
        )
        self.client = self.app.test_client()
        register_response = self.client.post(
            "/api/auth/register",
            json={
                "email": "tasker@example.com",
                "username": "tasker",
                "password": "pass1234",
            },
        )
        self.token = register_response.get_json()["token"]

    def test_create_task_then_fetch_pending_status(self) -> None:
        create_response = self.client.post(
            "/api/tasks",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "display_name": "Aster",
                "gender": "female",
                "birth_location": "Shanghai",
                "style_profile": {
                    "fashion_style": "modern casual",
                    "spirit_style": "dreamy water",
                },
                "extra_payload": {"scene_preference": "misty lakeside"},
            },
        )

        self.assertEqual(create_response.status_code, 201)
        create_payload = create_response.get_json()
        self.assertEqual(create_payload["status"], "pending")
        self.assertIn("id", create_payload)

        task_id = create_payload["id"]
        fetch_response = self.client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {self.token}"},
        )

        self.assertEqual(fetch_response.status_code, 200)
        fetch_payload = fetch_response.get_json()
        self.assertEqual(fetch_payload["id"], task_id)
        self.assertEqual(fetch_payload["status"], "pending")
        self.assertEqual(fetch_payload["assets"], [])
        self.assertEqual(fetch_payload["input_profile"]["display_name"], "Aster")
        self.assertEqual(fetch_payload["input_profile"]["birth_location"], "Shanghai")
        self.assertEqual(
            fetch_payload["input_profile"]["style_profile"]["fashion_style"],
            "modern casual",
        )
        self.assertEqual(
            fetch_payload["input_profile"]["extra_payload"]["scene_preference"],
            "misty lakeside",
        )

    def test_create_task_does_not_start_background_worker_during_tests(self) -> None:
        with patch("backend.services.task_service._start_generation_thread") as start_thread:
            create_response = self.client.post(
                "/api/tasks",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"display_name": "Aster"},
            )

        self.assertEqual(create_response.status_code, 201)
        start_thread.assert_not_called()

    def test_create_task_can_explicitly_start_background_worker_in_tests(self) -> None:
        self.app.config["AUTO_START_GENERATION_WORKER"] = True

        with patch("backend.services.task_service._start_generation_thread") as start_thread:
            create_response = self.client.post(
                "/api/tasks",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"display_name": "Aster"},
            )

        self.assertEqual(create_response.status_code, 201)
        start_thread.assert_called_once_with(create_response.get_json()["id"])


if __name__ == "__main__":
    unittest.main()
