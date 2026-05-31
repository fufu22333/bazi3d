import unittest
from unittest.mock import Mock, patch


class AssetApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        from backend.app import create_app

        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
                "JWT_SECRET_KEY": "asset-secret",
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

    def test_import_creates_asset_for_authenticated_user(self) -> None:
        from backend.models import SessionLocal
        from backend.models.model_asset import ModelAsset

        response = self.client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "source_url": "https://example.com/models/hero.glb",
                "file_format": "glb",
                "metadata": {"source": "manual-import"},
            },
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload["format"], "glb")
        self.assertEqual(payload["url"], "https://example.com/models/hero.glb")
        self.assertEqual(payload["metadata"]["source"], "manual-import")
        self.assertIn("id", payload)

        asset = SessionLocal().query(ModelAsset).filter_by(id=payload["id"]).one()
        self.assertEqual(asset.storage_url, "https://example.com/models/hero.glb")
        self.assertEqual(asset.file_format, "glb")

    def test_serialize_asset_marks_expired_signed_urls_unavailable(self) -> None:
        from backend.models.model_asset import ModelAsset
        from backend.services.asset_service import serialize_asset

        asset = ModelAsset(
            id=9,
            generation_task_id=1,
            asset_type="character",
            storage_url="https://cos.example.com/model.glb?q-sign-time=1;2",
            file_format="glb",
            asset_metadata={
                "thumbnail_url": "https://cos.example.com/preview.png?q-sign-time=1;2",
            },
        )

        payload = serialize_asset(asset)

        self.assertFalse(payload["is_available"])
        self.assertTrue(payload["is_signed_url_expired"])
        self.assertFalse(payload["metadata"]["thumbnail_available"])

    def test_serialize_asset_marks_local_urls_available(self) -> None:
        from backend.models.model_asset import ModelAsset
        from backend.services.asset_service import serialize_asset

        asset = ModelAsset(
            id=10,
            generation_task_id=1,
            asset_type="character",
            storage_url="/assets/generated/task1-character.glb",
            file_format="glb",
            asset_metadata={"thumbnail_url": "/assets/generated/task1-character-preview.png"},
        )

        payload = serialize_asset(asset)

        self.assertTrue(payload["is_available"])
        self.assertFalse(payload["is_signed_url_expired"])
        self.assertTrue(payload["metadata"]["thumbnail_available"])

    def test_serialize_asset_exposes_viewer_resource_type(self) -> None:
        from backend.models.model_asset import ModelAsset
        from backend.services.asset_service import serialize_asset

        guardian_asset = ModelAsset(
            id=11,
            generation_task_id=1,
            asset_type="guardian_spirit",
            storage_url="/assets/generated/task1-guardian.glb",
            file_format="glb",
            asset_metadata={},
        )

        payload = serialize_asset(guardian_asset)

        self.assertEqual(payload["asset_type"], "guardian_spirit")
        self.assertEqual(payload["type"], "guardian")

    def test_get_asset_requires_authentication(self) -> None:
        response = self.client.get("/api/assets/1")

        self.assertEqual(response.status_code, 401)

    def test_get_asset_returns_owner_asset(self) -> None:
        create_response = self.client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "source_url": "https://example.com/models/guardian.glb",
                "file_format": "glb",
                "metadata": {"label": "guardian"},
            },
        )
        asset_id = create_response.get_json()["id"]

        response = self.client.get(
            f"/api/assets/{asset_id}",
            headers={"Authorization": f"Bearer {self.owner_token}"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["id"], asset_id)
        self.assertEqual(payload["url"], "https://example.com/models/guardian.glb")
        self.assertEqual(payload["format"], "glb")

    def test_get_asset_rejects_non_owner(self) -> None:
        create_response = self.client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "source_url": "https://example.com/models/private.glb",
                "file_format": "glb",
                "metadata": {"scope": "owner-only"},
            },
        )
        asset_id = create_response.get_json()["id"]

        response = self.client.get(
            f"/api/assets/{asset_id}",
            headers={"Authorization": f"Bearer {self.other_token}"},
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_asset_rejects_non_owner(self) -> None:
        create_response = self.client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "source_url": "https://example.com/models/private-delete.glb",
                "file_format": "glb",
                "metadata": {"scope": "owner-only"},
            },
        )
        asset_id = create_response.get_json()["id"]

        response = self.client.delete(
            f"/api/assets/{asset_id}",
            headers={"Authorization": f"Bearer {self.other_token}"},
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_asset_removes_owner_asset(self) -> None:
        from backend.models import SessionLocal
        from backend.models.model_asset import ModelAsset

        create_response = self.client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "source_url": "https://example.com/models/delete-me.glb",
                "file_format": "glb",
                "metadata": {"delete": True},
            },
        )
        asset_id = create_response.get_json()["id"]

        response = self.client.delete(
            f"/api/assets/{asset_id}",
            headers={"Authorization": f"Bearer {self.owner_token}"},
        )

        self.assertEqual(response.status_code, 204)
        asset = SessionLocal().query(ModelAsset).filter_by(id=asset_id).first()
        self.assertIsNone(asset)

    def test_proxy_glb_returns_binary_with_cors_header(self) -> None:
        fake_response = Mock()
        fake_response.content = b"glb-bytes"
        fake_response.raise_for_status.return_value = None

        with patch("backend.routes.proxy.requests.get", return_value=fake_response) as mock_get:
            response = self.client.get(
                "/api/proxy/glb",
                query_string={"url": "https://cos.example.com/model.glb"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"glb-bytes")
        self.assertEqual(response.headers["Content-Type"], "model/gltf-binary")
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
        mock_get.assert_called_once_with("https://cos.example.com/model.glb", timeout=30)


if __name__ == "__main__":
    unittest.main()
