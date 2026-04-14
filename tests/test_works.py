import unittest


class WorkApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        from backend.app import create_app

        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
                "JWT_SECRET_KEY": "work-secret",
            }
        )
        self.client = self.app.test_client()
        suffix = self.id().split(".")[-1]
        self.suffix = suffix
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

    def _import_asset(self, token: str, url: str) -> int:
        response = self.client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "source_url": url,
                "file_format": "glb",
                "metadata": {"source": "test"},
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()["id"]

    def _create_work(
        self,
        *,
        token: str,
        title: str,
        visibility: str = "public",
        description: str | None = None,
        allow_remix: bool = False,
        url: str = "https://example.com/models/work.glb",
    ) -> int:
        asset_id = self._import_asset(token, url)
        response = self.client.post(
            "/api/works",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "asset_id": asset_id,
                "title": title,
                "description": description,
                "visibility": visibility,
                "allow_remix": allow_remix,
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()["id"]

    def test_publish_work_from_owned_asset(self) -> None:
        asset_id = self._import_asset(
            self.owner_token,
            "https://example.com/models/publish.glb",
        )

        response = self.client.post(
            "/api/works",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "asset_id": asset_id,
                "title": "First Work",
                "description": "Minimal public release",
                "visibility": "public",
                "allow_remix": False,
            },
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload["title"], "First Work")
        self.assertEqual(payload["visibility"], "public")
        self.assertEqual(payload["asset"]["id"], asset_id)
        self.assertEqual(payload["asset"]["url"], "https://example.com/models/publish.glb")

    def test_publish_work_rejects_non_owner_asset(self) -> None:
        asset_id = self._import_asset(
            self.owner_token,
            "https://example.com/models/private-asset.glb",
        )

        response = self.client.post(
            "/api/works",
            headers={"Authorization": f"Bearer {self.other_token}"},
            json={
                "asset_id": asset_id,
                "title": "Not Allowed",
                "visibility": "public",
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_list_works_returns_public_entries_only(self) -> None:
        public_asset_id = self._import_asset(
            self.owner_token,
            "https://example.com/models/public.glb",
        )
        private_asset_id = self._import_asset(
            self.owner_token,
            "https://example.com/models/private.glb",
        )

        public_response = self.client.post(
            "/api/works",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "asset_id": public_asset_id,
                "title": "Public Work",
                "visibility": "public",
            },
        )
        self.assertEqual(public_response.status_code, 201)

        private_response = self.client.post(
            "/api/works",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "asset_id": private_asset_id,
                "title": "Private Work",
                "visibility": "private",
            },
        )
        self.assertEqual(private_response.status_code, 201)

        response = self.client.get("/api/works")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(len(payload["items"]), 1)
        self.assertEqual(payload["items"][0]["title"], "Public Work")
        self.assertEqual(
            payload["items"][0]["asset"]["url"],
            "https://example.com/models/public.glb",
        )

    def test_get_public_work_detail_returns_minimum_readonly_fields(self) -> None:
        asset_id = self._import_asset(
            self.owner_token,
            "https://example.com/models/detail.glb",
        )

        create_response = self.client.post(
            "/api/works",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "asset_id": asset_id,
                "title": "Detail Work",
                "description": "Readable work detail",
                "visibility": "public",
                "allow_remix": True,
            },
        )
        self.assertEqual(create_response.status_code, 201)
        work_id = create_response.get_json()["id"]

        response = self.client.get(f"/api/works/{work_id}")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["id"], work_id)
        self.assertEqual(payload["title"], "Detail Work")
        self.assertEqual(payload["description"], "Readable work detail")
        self.assertEqual(payload["visibility"], "public")
        self.assertTrue(payload["allow_remix"])
        self.assertEqual(payload["asset"]["url"], "https://example.com/models/detail.glb")
        self.assertEqual(payload["author"]["username"], f"owner-{self.suffix}")
        self.assertIn("created_at", payload)
        self.assertIn("style_tags", payload)

    def test_get_private_work_detail_is_not_exposed(self) -> None:
        work_id = self._create_work(
            token=self.owner_token,
            title="Private Detail Work",
            visibility="private",
            url="https://example.com/models/private-detail.glb",
        )

        response = self.client.get(f"/api/works/{work_id}")

        self.assertEqual(response.status_code, 404)

    def test_owner_can_get_private_work_detail_with_auth(self) -> None:
        work_id = self._create_work(
            token=self.owner_token,
            title="Owner Private Work",
            visibility="private",
            description="Only owner should see this",
            allow_remix=True,
            url="https://example.com/models/private-owner.glb",
        )

        response = self.client.get(
            f"/api/works/{work_id}",
            headers={"Authorization": f"Bearer {self.owner_token}"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["title"], "Owner Private Work")
        self.assertEqual(payload["visibility"], "private")
        self.assertTrue(payload["allow_remix"])

    def test_non_owner_cannot_get_private_work_detail_with_auth(self) -> None:
        work_id = self._create_work(
            token=self.owner_token,
            title="Hidden Private Work",
            visibility="private",
            url="https://example.com/models/private-hidden.glb",
        )

        response = self.client.get(
            f"/api/works/{work_id}",
            headers={"Authorization": f"Bearer {self.other_token}"},
        )

        self.assertEqual(response.status_code, 404)

    def test_owner_can_patch_work_metadata(self) -> None:
        work_id = self._create_work(
            token=self.owner_token,
            title="Patch Me",
            description="Before patch",
            visibility="public",
            allow_remix=False,
            url="https://example.com/models/patch.glb",
        )

        response = self.client.patch(
            f"/api/works/{work_id}",
            headers={"Authorization": f"Bearer {self.owner_token}"},
            json={
                "title": "Patched Title",
                "description": "After patch",
                "visibility": "private",
                "allow_remix": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["title"], "Patched Title")
        self.assertEqual(payload["description"], "After patch")
        self.assertEqual(payload["visibility"], "private")
        self.assertTrue(payload["allow_remix"])

    def test_non_owner_cannot_patch_work_metadata(self) -> None:
        work_id = self._create_work(
            token=self.owner_token,
            title="Protected Patch",
            visibility="public",
            url="https://example.com/models/protected-patch.glb",
        )

        response = self.client.patch(
            f"/api/works/{work_id}",
            headers={"Authorization": f"Bearer {self.other_token}"},
            json={"title": "Nope"},
        )

        self.assertEqual(response.status_code, 403)

    def test_owner_can_delete_work(self) -> None:
        work_id = self._create_work(
            token=self.owner_token,
            title="Delete Me",
            visibility="public",
            url="https://example.com/models/delete-work.glb",
        )

        delete_response = self.client.delete(
            f"/api/works/{work_id}",
            headers={"Authorization": f"Bearer {self.owner_token}"},
        )

        self.assertEqual(delete_response.status_code, 204)

        fetch_response = self.client.get(f"/api/works/{work_id}")
        self.assertEqual(fetch_response.status_code, 404)

    def test_non_owner_cannot_delete_work(self) -> None:
        work_id = self._create_work(
            token=self.owner_token,
            title="Protected Delete",
            visibility="public",
            url="https://example.com/models/protected-delete.glb",
        )

        response = self.client.delete(
            f"/api/works/{work_id}",
            headers={"Authorization": f"Bearer {self.other_token}"},
        )

        self.assertEqual(response.status_code, 403)

    def test_owner_can_list_only_their_own_works(self) -> None:
        owned_public_id = self._create_work(
            token=self.owner_token,
            title="Owner Public Work",
            visibility="public",
            url="https://example.com/models/owner-public.glb",
        )
        owned_private_id = self._create_work(
            token=self.owner_token,
            title="Owner Private Work",
            visibility="private",
            url="https://example.com/models/owner-private.glb",
        )
        self._create_work(
            token=self.other_token,
            title="Other User Work",
            visibility="public",
            url="https://example.com/models/other-public.glb",
        )

        response = self.client.get(
            "/api/works/mine",
            headers={"Authorization": f"Bearer {self.owner_token}"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(len(payload["items"]), 2)
        returned_ids = {item["id"] for item in payload["items"]}
        self.assertSetEqual(returned_ids, {owned_public_id, owned_private_id})
        self.assertTrue(
            all(item["author"]["username"] == f"owner-{self.suffix}" for item in payload["items"])
        )


if __name__ == "__main__":
    unittest.main()
