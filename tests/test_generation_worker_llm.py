import unittest
from datetime import datetime
from unittest.mock import patch


class FakePromptSection:
    def __init__(self, style, material, pose_keywords, visual_keywords, description):
        self.style = style
        self.material = material
        self.pose_keywords = pose_keywords
        self.visual_keywords = visual_keywords
        self.description = description


class FakePromptOutput:
    def __init__(self):
        self.character = FakePromptSection(
            style="minimalist tailoring",
            material="matte wool and brushed steel",
            pose_keywords=["standing upright", "arms relaxed"],
            visual_keywords=["layered coat", "structured shoulders"],
            description="Character description.",
        )
        self.guardian_spirit = FakePromptSection(
            style="luminous fox spirit",
            material="translucent crystal and silver trim",
            pose_keywords=["floating", "curled tail"],
            visual_keywords=["inner glow", "compact silhouette"],
            description="Guardian description.",
        )


class FakeLlmClient:
    def __init__(self) -> None:
        self.generate_json_calls = []

    def _post(self, *args, **kwargs):
        raise AssertionError("_post should not be called directly")

    def generate_json(self, prompt: str):
        self.generate_json_calls.append(prompt)
        return {
            "version": "v1",
            "image_reference": None,
            "character": {
                "style": "minimalist tailoring",
                "material": "matte wool and brushed steel",
                "pose_keywords": ["standing upright", "arms relaxed"],
                "visual_keywords": ["layered coat", "structured shoulders"],
                "description": "Character description.",
            },
            "guardian_spirit": {
                "style": "luminous fox spirit",
                "material": "translucent crystal and silver trim",
                "pose_keywords": ["floating", "curled tail"],
                "visual_keywords": ["inner glow", "compact silhouette"],
                "description": "Guardian description.",
            },
        }


class FakeAdapter:
    def __init__(self) -> None:
        self.submitted_prompts = []

    def submit_job(self, prompt: str) -> str:
        self.submitted_prompts.append(prompt)
        return f"job-{len(self.submitted_prompts)}"

    def query_job(self, job_id: str) -> dict:
        return {"url": f"https://example.com/{job_id}.glb"}

    def normalize(self, result: dict) -> dict:
        return {
            "url": result["url"],
            "format": "glb",
            "metadata": {"provider": "fake"},
        }


class FakeRegistry:
    def __init__(self, adapter) -> None:
        self.adapter = adapter

    def get(self, provider_key: str):
        return self.adapter


class GenerationWorkerLlmTestCase(unittest.TestCase):
    def setUp(self) -> None:
        from backend.app import create_app
        from backend.models import SessionLocal
        from backend.models.generation_task import GenerationTask
        from backend.models.input_profile import InputProfile
        from backend.models.user import User

        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:",
                "JWT_SECRET_KEY": "worker-secret",
            }
        )

        with self.app.app_context():
            session = SessionLocal()
            user = User(
                email="worker-llm@example.com",
                username="worker-llm",
                password_hash="hashed-password",
            )
            session.add(user)
            session.commit()

            profile = InputProfile(
                user_id=user.id,
                display_name="Aster",
                gender="female",
                birth_location="Shanghai",
                birth_datetime=datetime(2024, 1, 2, 3, 4, 5),
                style_profile={
                    "fashion_style": "minimalist",
                    "spirit_style": "water_dreamlike",
                },
                extra_payload={},
            )
            session.add(profile)
            session.commit()

            task = GenerationTask(user_id=user.id, input_profile_id=profile.id)
            session.add(task)
            session.commit()
            self.task_id = task.id

    def tearDown(self) -> None:
        from backend.models import SessionLocal

        SessionLocal.remove()

    def test_run_generation_task_uses_generate_json_instead_of_post(self) -> None:
        from backend.services.generation_worker import run_generation_task

        fake_client = FakeLlmClient()
        fake_adapter = FakeAdapter()

        with self.app.app_context():
            with patch(
                "backend.services.generation_worker._create_llm_client",
                return_value=fake_client,
            ), patch(
                "backend.services.generation_worker._build_provider_registry",
                return_value=FakeRegistry(fake_adapter),
            ):
                task = run_generation_task(self.task_id)

        self.assertEqual(task.status, "completed")
        self.assertEqual(len(fake_client.generate_json_calls), 1)
        self.assertEqual(len(fake_adapter.submitted_prompts), 2)


if __name__ == "__main__":
    unittest.main()
