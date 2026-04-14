import unittest


class HealthCheckTestCase(unittest.TestCase):
    def test_health_endpoint_returns_ok_status(self) -> None:
        from backend.app import create_app

        app = create_app()
        client = app.test_client()

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
