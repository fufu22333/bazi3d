import unittest

from backend.app import create_app


class FrontendServingTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
        self.client = self.app.test_client()

    def test_app_route_serves_frontend_index(self) -> None:
        response = self.client.get("/app")
        try:
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/html", response.content_type)
            self.assertIn('id="task-form"', response.get_data(as_text=True))
        finally:
            response.close()

    def test_frontend_route_serves_static_asset(self) -> None:
        response = self.client.get("/frontend/js/api.js")
        try:
            self.assertEqual(response.status_code, 200)
            self.assertIn("javascript", response.content_type)
            self.assertIn("requestJson", response.get_data(as_text=True))
        finally:
            response.close()

    def test_root_relative_frontend_paths_resolve_from_app_shell(self) -> None:
        asset_response = self.client.get("/js/viewer/main.js")
        try:
            self.assertEqual(asset_response.status_code, 200)
            self.assertIn("javascript", asset_response.content_type)
            self.assertIn("loadSelectedModel", asset_response.get_data(as_text=True))
        finally:
            asset_response.close()

        page_response = self.client.get("/auth.html")
        try:
            self.assertEqual(page_response.status_code, 200)
            self.assertIn("text/html", page_response.content_type)
            self.assertIn('id="login-form"', page_response.get_data(as_text=True))
        finally:
            page_response.close()


if __name__ == "__main__":
    unittest.main()
