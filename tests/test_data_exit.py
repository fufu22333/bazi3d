import unittest


class DataExitApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        from backend.app import create_app

        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
                "JWT_SECRET_KEY": "data-exit-secret",
            }
        )
        self.client = self.app.test_client()
        register_response = self.client.post(
            "/api/auth/register",
            json={
                "email": "exit@example.com",
                "username": "exit-user",
                "password": "pass1234",
            },
        )
        self.assertEqual(register_response.status_code, 201)
        self.token = register_response.get_json()["token"]

    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    def test_export_returns_user_profile_tasks_works_and_asset_references(self) -> None:
        task_response = self.client.post(
            "/api/tasks",
            headers=self._auth_headers(),
            json={
                "display_name": "Export User",
                "gender": "female",
                "birth_location": "Shanghai",
                "style_profile": {"fashion_style": "minimal"},
            },
        )
        self.assertEqual(task_response.status_code, 201)
        asset_response = self.client.post(
            "/api/assets/import",
            headers=self._auth_headers(),
            json={
                "source_url": "https://example.com/export.glb",
                "file_format": "glb",
                "metadata": {"thumbnail_url": "https://example.com/export.png"},
            },
        )
        self.assertEqual(asset_response.status_code, 201)
        work_response = self.client.post(
            "/api/works",
            headers=self._auth_headers(),
            json={
                "asset_id": asset_response.get_json()["id"],
                "title": "Export Work",
                "visibility": "private",
            },
        )
        self.assertEqual(work_response.status_code, 201)

        response = self.client.get("/api/auth/export", headers=self._auth_headers())

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["user"]["email"], "exit@example.com")
        self.assertEqual(len(payload["input_profiles"]), 2)
        self.assertEqual(len(payload["tasks"]), 2)
        self.assertEqual(len(payload["works"]), 1)
        self.assertEqual(len(payload["assets"]), 1)
        self.assertEqual(payload["assets"][0]["url"], "https://example.com/export.glb")

    def test_delete_account_removes_user_owned_records_and_blocks_old_token(self) -> None:
        task_response = self.client.post(
            "/api/tasks",
            headers=self._auth_headers(),
            json={"display_name": "Delete User"},
        )
        self.assertEqual(task_response.status_code, 201)

        response = self.client.delete("/api/auth/me", headers=self._auth_headers())

        self.assertEqual(response.status_code, 204)
        me_response = self.client.get("/api/auth/me", headers=self._auth_headers())
        self.assertEqual(me_response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
