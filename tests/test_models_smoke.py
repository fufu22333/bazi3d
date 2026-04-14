import unittest

from sqlalchemy.exc import IntegrityError


class ModelsSmokeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        from backend.models import Base, SessionLocal, configure_session

        self.engine = configure_session("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = SessionLocal()

    def tearDown(self) -> None:
        from backend.models import Base, SessionLocal

        self.session.close()
        SessionLocal.remove()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_can_create_user_and_input_profile(self) -> None:
        from backend.models.input_profile import InputProfile
        from backend.models.user import User

        user = User(
            email="tester@example.com",
            username="tester",
            password_hash="hashed-password",
        )
        self.session.add(user)
        self.session.commit()

        profile = InputProfile(
            user_id=user.id,
            display_name="Test User",
            gender="female",
            extra_payload={"note": "placeholder"},
        )
        self.session.add(profile)
        self.session.commit()

        self.assertIsNotNone(user.id)
        self.assertIsNotNone(profile.id)
        self.assertEqual(profile.user_id, user.id)

    def test_generation_task_updates_timestamp_on_change(self) -> None:
        from backend.models.generation_task import GenerationTask
        from backend.models.input_profile import InputProfile
        from backend.models.user import User

        user = User(
            email="updater@example.com",
            username="updater",
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

        original_updated_at = task.updated_at
        task.status = "completed"
        self.session.commit()
        self.session.refresh(task)

        self.assertNotEqual(task.updated_at, original_updated_at)

    def test_evaluation_log_requires_task_or_work_reference(self) -> None:
        from backend.models.evaluation_log import EvaluationLog

        log = EvaluationLog(level="text", metrics={"score": 1})
        self.session.add(log)

        with self.assertRaises(ValueError):
            self.session.commit()
            self.session.rollback()


if __name__ == "__main__":
    unittest.main()
