import unittest


class FakeRegistry:
    def __init__(self, adapters: dict):
        self.adapters = adapters

    def get(self, provider_key: str):
        return self.adapters[provider_key]


class FakeAdapter:
    def __init__(self, provider_name: str, fail_attempts: int = 0):
        self.provider_name = provider_name
        self.fail_attempts = fail_attempts
        self.submit_calls = 0
        self.submitted_prompts = []

    def submit(self, prompt: dict, config: dict) -> str:
        self.submit_calls += 1
        self.submitted_prompts.append(prompt)
        if self.fail_attempts > 0:
            self.fail_attempts -= 1
            raise RuntimeError(f"{self.provider_name} submit failed")
        return f"{self.provider_name}-task-{self.submit_calls}"

    def query(self, task_id: str) -> dict:
        return {
            "task_id": task_id,
            "url": f"https://assets.example.com/{task_id}.glb",
            "metadata": {"provider": self.provider_name},
        }

    def normalize(self, result: dict) -> dict:
        return {
            "url": result["url"],
            "format": "glb",
            "metadata": {
                "provider": self.provider_name,
                "task_id": result["task_id"],
            },
        }


class GenerationWorkerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        from backend.models import Base, SessionLocal, configure_session

        self.engine = configure_session("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = SessionLocal()

        from backend.models.generation_task import GenerationTask
        from backend.models.input_profile import InputProfile
        from backend.models.user import User

        user = User(
            email="worker@example.com",
            username="worker-user",
            password_hash="hashed-password",
        )
        self.session.add(user)
        self.session.commit()

        profile = InputProfile(user_id=user.id)
        self.session.add(profile)
        self.session.commit()

        task = GenerationTask(user_id=user.id, input_profile_id=profile.id)
        self.session.add(task)
        self.session.commit()

        self.task_id = task.id
        self.prompt_output = {
            "character": {"style": "modern casual", "description": "person prompt"},
            "guardian_spirit": {
                "style": "dreamy water",
                "description": "guardian prompt",
            },
        }

    def tearDown(self) -> None:
        from backend.models import Base, SessionLocal

        self.session.close()
        SessionLocal.remove()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_same_provider_completes_and_writes_two_assets(self) -> None:
        from backend.models import SessionLocal
        from backend.models.generation_task import GenerationTask
        from backend.models.model_asset import ModelAsset
        from backend.services.generation_worker import run_generation_task

        shared_adapter = FakeAdapter("shared")
        registry = FakeRegistry({"shared": shared_adapter})

        run_generation_task(
            task_id=self.task_id,
            prompt_output=self.prompt_output,
            provider_plan={
                "person": {"provider": "shared", "config": {}},
                "guardian": {"provider": "shared", "config": {}},
            },
            provider_registry=registry,
        )

        session = SessionLocal()
        task = session.get(GenerationTask, self.task_id)
        assets = session.query(ModelAsset).order_by(ModelAsset.asset_type.asc()).all()

        self.assertEqual(task.status, "completed")
        self.assertEqual(task.provider, "shared")
        self.assertEqual(len(assets), 2)
        self.assertEqual([asset.asset_type for asset in assets], ["guardian", "person"])
        self.assertEqual(shared_adapter.submit_calls, 2)

    def test_different_providers_complete_and_write_two_assets(self) -> None:
        from backend.models import SessionLocal
        from backend.models.generation_task import GenerationTask
        from backend.models.model_asset import ModelAsset
        from backend.services.generation_worker import run_generation_task

        person_adapter = FakeAdapter("meshy")
        guardian_adapter = FakeAdapter("hunyuan")
        registry = FakeRegistry(
            {"meshy": person_adapter, "hunyuan": guardian_adapter}
        )

        run_generation_task(
            task_id=self.task_id,
            prompt_output=self.prompt_output,
            provider_plan={
                "person": {"provider": "meshy", "config": {}},
                "guardian": {"provider": "hunyuan", "config": {}},
            },
            provider_registry=registry,
        )

        session = SessionLocal()
        task = session.get(GenerationTask, self.task_id)
        assets = session.query(ModelAsset).order_by(ModelAsset.asset_type.asc()).all()

        self.assertEqual(task.status, "completed")
        self.assertEqual(task.provider, "multiple")
        self.assertEqual(len(assets), 2)
        self.assertEqual(assets[0].asset_metadata["provider"], "hunyuan")
        self.assertEqual(assets[1].asset_metadata["provider"], "meshy")

    def test_failure_marks_task_failed_and_skips_asset_write(self) -> None:
        from backend.models import SessionLocal
        from backend.models.generation_task import GenerationTask
        from backend.models.model_asset import ModelAsset
        from backend.services.generation_worker import run_generation_task

        failing_adapter = FakeAdapter("shared", fail_attempts=3)
        registry = FakeRegistry({"shared": failing_adapter})

        run_generation_task(
            task_id=self.task_id,
            prompt_output=self.prompt_output,
            provider_plan={
                "person": {"provider": "shared", "config": {}},
                "guardian": {"provider": "shared", "config": {}},
            },
            provider_registry=registry,
            retry_count=2,
        )

        session = SessionLocal()
        task = session.get(GenerationTask, self.task_id)
        asset_count = session.query(ModelAsset).count()

        self.assertEqual(task.status, "failed")
        self.assertIsNotNone(task.error_message)
        self.assertEqual(asset_count, 0)


if __name__ == "__main__":
    unittest.main()
