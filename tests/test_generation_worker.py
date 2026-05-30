import unittest
import tempfile
from datetime import datetime
from pathlib import Path
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
            style="tailored ceremonial wear",
            material="matte silk",
            pose_keywords=["standing", "hands lowered"],
            visual_keywords=["clean silhouette"],
            description="Character prompt.",
        )
        self.guardian_spirit = FakePromptSection(
            style="misty crane spirit",
            material="glass feathers",
            pose_keywords=["hovering"],
            visual_keywords=["soft glow"],
            description="Guardian prompt.",
        )


class FakeLlmClient:
    def generate_json(self, prompt: str):
        return {
            "version": "v1",
            "image_reference": None,
            "character": {
                "style": "tailored ceremonial wear",
                "material": "matte silk",
                "pose_keywords": ["standing", "hands lowered"],
                "visual_keywords": ["clean silhouette"],
                "description": "Character prompt.",
            },
            "guardian_spirit": {
                "style": "misty crane spirit",
                "material": "glass feathers",
                "pose_keywords": ["hovering"],
                "visual_keywords": ["soft glow"],
                "description": "Guardian prompt.",
            },
        }


class FakeAdapter:
    def __init__(self, fail_on_submit: bool = False) -> None:
        self.fail_on_submit = fail_on_submit
        self.submitted_prompts = []

    def submit_job(self, prompt: str) -> str:
        if self.fail_on_submit:
            raise RuntimeError("provider submit failed")
        self.submitted_prompts.append(prompt)
        return f"job-{len(self.submitted_prompts)}"

    def query_job(self, job_id: str) -> dict:
        return {"url": f"https://assets.example.com/{job_id}.glb"}

    def normalize(self, result: dict) -> dict:
        return {
            "url": result["url"],
            "format": "glb",
            "metadata": {"provider": "fake"},
        }


class FakeTruncatingAdapter(FakeAdapter):
    def _truncate_prompt(self, prompt: str) -> str:
        return f"submitted::{prompt[:32]}"


class FakeRegistry:
    def __init__(self, adapter) -> None:
        self.adapter = adapter

    def get(self, provider_key: str):
        return self.adapter


class GenerationWorkerTestCase(unittest.TestCase):
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
                email="worker@example.com",
                username="worker-user",
                password_hash="hashed-password",
            )
            session.add(user)
            session.commit()

            profile = InputProfile(
                user_id=user.id,
                display_name="Aster",
                birth_datetime=datetime(2024, 1, 2, 3, 4, 5),
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

    def test_successful_run_persists_two_assets_and_task_refs(self) -> None:
        from backend.models import SessionLocal
        from backend.models.generation_task import GenerationTask
        from backend.models.model_asset import ModelAsset
        from backend.models.work import Work
        from backend.services.generation_worker import run_generation_task

        fake_adapter = FakeAdapter()

        with self.app.app_context():
            with patch(
                "backend.services.generation_worker._create_llm_client",
                return_value=FakeLlmClient(),
            ), patch(
                "backend.services.generation_worker._build_provider_registry",
                return_value=FakeRegistry(fake_adapter),
            ):
                task = run_generation_task(self.task_id)

            session = SessionLocal()
            stored_task = session.get(GenerationTask, self.task_id)
            assets = session.query(ModelAsset).order_by(ModelAsset.asset_type.asc()).all()
            works = session.query(Work).order_by(Work.id.asc()).all()

        self.assertEqual(task.status, "completed")
        self.assertEqual(stored_task.status, "completed")
        self.assertEqual(stored_task.provider, "hunyuan3d")
        self.assertEqual(stored_task.external_task_id, "job-1")
        self.assertEqual(stored_task.character_task_ref, "job-1")
        self.assertEqual(stored_task.spirit_task_ref, "job-2")
        self.assertEqual([asset.asset_type for asset in assets], ["character", "guardian_spirit"])
        self.assertEqual(len(works), 1)
        self.assertEqual(works[0].user_id, stored_task.user_id)
        self.assertEqual(works[0].primary_asset_id, assets[0].id)
        self.assertEqual(works[0].visibility, "public")
        self.assertIn("Aster", works[0].title)
        self.assertEqual(len(fake_adapter.submitted_prompts), 2)

    def test_character_prompt_front_loads_full_body_constraints(self) -> None:
        from backend.adapters.hunyuan3d_adapter import Hunyuan3DAdapter
        from backend.services.generation_worker import _build_asset_prompt

        section = FakePromptSection(
            style="minimalist water dreamlike, muted tones",
            material="matte crepe, translucent organza, brushed silver hardware",
            pose_keywords=["standing upright", "arms relaxed"],
            visual_keywords=["asymmetric silhouette", "soft draping"],
            description=(
                "The character stands with a slender, elegant frame, approximately 165-172cm tall. "
                "The outfit features an asymmetric top with a single long sleeve in matte crepe, "
                "layered over a translucent organza underlayer that catches light softly. "
                "The left shoulder is bare, with a thin brushed silver strap. "
                "The waist is cinched by a wide belt of matte black leather with a geometric silver buckle. "
                "High-waisted wide-leg trousers in the same crepe fabric flow down to brush the floor. "
                "Shoes are simple low-heeled mules in matte charcoal leather. "
                "High detail render, realistic fabric texture, full-body 3D model, cinematic lighting."
            ),
        )

        prompt = _build_asset_prompt(
            "character",
            section,
            {
                "display_name": "Aster",
                "gender": "female",
                "birth_location": "Shanghai",
                "birth_datetime": "1995-06-15T09:30",
            },
        )
        submitted_prompt = Hunyuan3DAdapter._truncate_prompt(prompt)

        self.assertIn("full-body", submitted_prompt)
        self.assertIn("not a bust", submitted_prompt)
        self.assertIn("not a half-body", submitted_prompt)
        self.assertIn("feet and footwear", submitted_prompt)

    def test_successful_run_writes_prompt_debug_artifact(self) -> None:
        from backend.services.generation_worker import run_generation_task

        fake_adapter = FakeAdapter()

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.app.app_context():
                self.app.config["PROMPT_DEBUG_DIR"] = temp_dir
                with patch(
                    "backend.services.generation_worker._create_llm_client",
                    return_value=FakeLlmClient(),
                ), patch(
                    "backend.services.generation_worker._build_provider_registry",
                    return_value=FakeRegistry(fake_adapter),
                ):
                    run_generation_task(self.task_id)

            debug_path = Path(temp_dir) / f"task-{self.task_id}-prompts.json"
            self.assertTrue(debug_path.exists())
            debug_text = debug_path.read_text(encoding="utf-8")
            self.assertIn('"prompt_output"', debug_text)
            self.assertIn('"asset_prompts"', debug_text)
            self.assertIn("Create a high-quality stylized 3D character", debug_text)

    def test_successful_run_submits_provider_ready_prompts(self) -> None:
        from backend.services.generation_worker import run_generation_task

        fake_adapter = FakeTruncatingAdapter()

        with self.app.app_context():
            with patch(
                "backend.services.generation_worker._create_llm_client",
                return_value=FakeLlmClient(),
            ), patch(
                "backend.services.generation_worker._build_provider_registry",
                return_value=FakeRegistry(fake_adapter),
            ):
                run_generation_task(self.task_id)

        self.assertEqual(len(fake_adapter.submitted_prompts), 2)
        self.assertTrue(
            all(prompt.startswith("submitted::") for prompt in fake_adapter.submitted_prompts)
        )

    def test_failed_run_marks_task_failed_without_assets(self) -> None:
        from backend.models import SessionLocal
        from backend.models.generation_task import GenerationTask
        from backend.models.model_asset import ModelAsset
        from backend.services.generation_worker import run_generation_task

        with self.app.app_context():
            with patch(
                "backend.services.generation_worker._create_llm_client",
                return_value=FakeLlmClient(),
            ), patch(
                "backend.services.generation_worker._build_provider_registry",
                return_value=FakeRegistry(FakeAdapter(fail_on_submit=True)),
            ):
                task = run_generation_task(self.task_id)

            session = SessionLocal()
            stored_task = session.get(GenerationTask, self.task_id)
            asset_count = session.query(ModelAsset).count()

        self.assertEqual(stored_task.status, "failed")
        self.assertIn("provider submit failed", stored_task.error_message)
        self.assertEqual(asset_count, 0)


if __name__ == "__main__":
    unittest.main()
