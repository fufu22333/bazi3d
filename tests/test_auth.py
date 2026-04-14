import unittest


class AuthApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        from backend.app import create_app

        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
                "JWT_SECRET_KEY": "test-secret",
            }
        )
        self.client = self.app.test_client()

    def test_register_creates_user_with_hashed_password_and_returns_token(self) -> None:
        from backend.models import SessionLocal
        from backend.models.user import User

        response = self.client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "username": "new-user",
                "password": "pass1234",
            },
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload["user"]["email"], "new@example.com")
        self.assertEqual(payload["user"]["username"], "new-user")
        self.assertIn("token", payload)
        self.assertNotIn("password_hash", payload["user"])

        user = SessionLocal().query(User).filter_by(email="new@example.com").one()
        self.assertNotEqual(user.password_hash, "pass1234")

    def test_login_returns_token_for_valid_credentials(self) -> None:
        register_response = self.client.post(
            "/api/auth/register",
            json={
                "email": "login@example.com",
                "username": "login-user",
                "password": "pass1234",
            },
        )
        self.assertEqual(register_response.status_code, 201)

        response = self.client.post(
            "/api/auth/login",
            json={"email": "login@example.com", "password": "pass1234"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["user"]["email"], "login@example.com")
        self.assertIn("token", payload)
        self.assertNotIn("password_hash", payload["user"])

    def test_protected_placeholder_route_accepts_bearer_token(self) -> None:
        register_response = self.client.post(
            "/api/auth/register",
            json={
                "email": "guard@example.com",
                "username": "guard-user",
                "password": "pass1234",
            },
        )
        token = register_response.get_json()["token"]

        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["user"]["email"], "guard@example.com")
        self.assertEqual(payload["user"]["username"], "guard-user")


if __name__ == "__main__":
    unittest.main()
