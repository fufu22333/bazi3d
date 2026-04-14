import unittest
from uuid import uuid4
from unittest.mock import patch


class CharacterChatApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        from backend.app import create_app
        from backend.models import SessionLocal

        SessionLocal.remove()

        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
                "JWT_SECRET_KEY": "chat-secret",
            }
        )
        self.client = self.app.test_client()
        self.token = self._register_user()

    def tearDown(self) -> None:
        from backend.models import SessionLocal

        SessionLocal.remove()

    def _register_user(self) -> str:
        suffix = uuid4().hex
        response = self.client.post(
            "/api/auth/register",
            json={
                "email": f"{suffix}@example.com",
                "username": f"user-{suffix}",
                "password": "pass1234",
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()["token"]

    def test_chat_returns_single_reply_from_existing_llm_path(self) -> None:
        self.app.config["CHAT_LLM_CALLABLE"] = (
            lambda prompt: "You sound thoughtful. Keep moving forward."
        )

        response = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "message": "How should I begin?",
                "role": "person",
                "input_profile": {
                    "display_name": "Aster",
                    "gender": "female",
                    "birth_location": "Shanghai",
                    "style_profile": {
                        "fashion_style": "modern casual",
                        "spirit_style": "dreamy water",
                    },
                },
                "recent_messages": [{"role": "user", "content": "Hello there"}],
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(
            payload["reply"],
            "You sound thoughtful. Keep moving forward.",
        )
        self.assertFalse(payload["fallback_used"])
        self.assertEqual(payload["role"], "person")

    def test_chat_falls_back_when_llm_call_fails(self) -> None:
        def failing_llm(_: str) -> str:
            raise RuntimeError("llm offline")

        self.app.config["CHAT_LLM_CALLABLE"] = failing_llm

        response = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "message": "Can you help me?",
                "role": "guardian",
                "input_profile": {
                    "display_name": "Aster",
                    "style_profile": {
                        "fashion_style": "modern casual",
                        "spirit_style": "dreamy water",
                    },
                },
                "recent_messages": [],
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["fallback_used"])
        self.assertEqual(payload["reply"], '"..." （守护灵轻轻环绕了你一圈）')

    def test_chat_uses_default_llm_text_generation_path(self) -> None:
        captured = {}

        def fake_generate_text(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "我听见你了。"

        with patch(
            "backend.services.chat_service.DeepSeekClient.generate_text",
            new=fake_generate_text,
        ):
            response = self.client.post(
                "/api/chat",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "message": "今天我有点迷茫",
                    "role": "person",
                    "input_profile": {
                        "display_name": "Aster",
                        "gender": "female",
                        "birth_location": "Shanghai",
                        "style_profile": {
                            "fashion_style": "modern casual",
                            "spirit_style": "dreamy water",
                        },
                    },
                    "recent_messages": [
                        {"role": "user", "content": "你是谁？"},
                        {"role": "character", "content": "我是Aster。"},
                    ],
                },
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["reply"], "我听见你了。")
        self.assertFalse(payload["fallback_used"])
        self.assertEqual(payload["role"], "person")
        self.assertIn(
            "You are a 3D character brought to life by the user's birth chart and style preferences.",
            captured["prompt"],
        )
        self.assertIn("Your name is Aster.", captured["prompt"])
        self.assertIn("born in Shanghai", captured["prompt"])
        self.assertIn("your style is modern casual", captured["prompt"])
        self.assertIn("User: 今天我有点迷茫", captured["prompt"])

    def test_chat_guardian_prompt_uses_guardian_spirit_system_prompt(self) -> None:
        captured = {}

        def fake_generate_text(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "我会守着你。"

        with patch(
            "backend.services.chat_service.DeepSeekClient.generate_text",
            new=fake_generate_text,
        ):
            response = self.client.post(
                "/api/chat",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "message": "请指引我",
                    "role": "guardian",
                    "input_profile": {
                        "display_name": "Aster",
                        "birth_location": "Shanghai",
                        "style_profile": {
                            "spirit_style": "dreamy water",
                        },
                    },
                    "recent_messages": [],
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You are a guardian spirit — a mystical non-human companion created from the user's inner world.",
            captured["prompt"],
        )
        self.assertIn("Your spirit style is dreamy water.", captured["prompt"])
        self.assertIn("You protect and guide your owner.", captured["prompt"])
        self.assertIn("User: 请指引我", captured["prompt"])

    def test_chat_fallback_uses_in_character_copy(self) -> None:
        def failing_llm(_: str) -> str:
            raise RuntimeError("llm offline")

        self.app.config["CHAT_LLM_CALLABLE"] = failing_llm

        person_response = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "message": "Hello?",
                "role": "person",
                "input_profile": {
                    "display_name": "Aster",
                    "style_profile": {},
                },
                "recent_messages": [],
            },
        )
        guardian_response = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "message": "Hello?",
                "role": "guardian",
                "input_profile": {
                    "display_name": "Aster",
                    "style_profile": {},
                },
                "recent_messages": [],
            },
        )

        self.assertEqual(
            person_response.get_json()["reply"],
            '"..." （沉默三秒，然后微微点头）',
        )
        self.assertEqual(
            guardian_response.get_json()["reply"],
            '"..." （守护灵轻轻环绕了你一圈）',
        )


if __name__ == "__main__":
    unittest.main()
