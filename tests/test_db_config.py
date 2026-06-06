import os
import threading
import unittest
from unittest.mock import patch

from sqlalchemy import text


class DatabaseConfigTestCase(unittest.TestCase):
    def test_database_uri_defaults_to_local_mysql(self) -> None:
        from backend.config import get_config

        with patch.dict(os.environ, {}, clear=True):
            config = get_config()

        self.assertEqual(
            config["SQLALCHEMY_DATABASE_URI"],
            "mysql+pymysql://root:change_me@127.0.0.1:3306/bazi3d?charset=utf8mb4",
        )

    def test_database_uri_can_be_overridden_by_environment(self) -> None:
        from backend.config import get_config

        env = {
            "MYSQL_HOST": "db.internal",
            "MYSQL_PORT": "3307",
            "MYSQL_DATABASE": "custom_db",
            "MYSQL_USER": "demo",
            "MYSQL_PASSWORD": "secret",
        }

        with patch.dict(os.environ, env, clear=True):
            config = get_config()

        self.assertEqual(
            config["SQLALCHEMY_DATABASE_URI"],
            "mysql+pymysql://demo:secret@db.internal:3307/custom_db?charset=utf8mb4",
        )

    def test_production_requires_explicit_jwt_secret(self) -> None:
        from backend.config import get_config

        with patch.dict(os.environ, {"APP_ENV": "production"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "JWT_SECRET_KEY"):
                get_config()

    def test_cors_origins_can_be_configured_from_environment(self) -> None:
        from backend.config import get_config

        env = {
            "CORS_ALLOWED_ORIGINS": "https://staging.example.com, https://app.example.com",
        }

        with patch.dict(os.environ, env, clear=True):
            config = get_config()

        self.assertEqual(
            config["CORS_ALLOWED_ORIGINS"],
            ["https://staging.example.com", "https://app.example.com"],
        )


class DatabaseSessionTestCase(unittest.TestCase):
    def test_configured_scoped_session_can_execute_sql(self) -> None:
        from backend.models import SessionLocal, configure_session

        engine = configure_session("sqlite+pysqlite:///:memory:")

        try:
            result = SessionLocal().execute(text("SELECT 1")).scalar_one()
        finally:
            SessionLocal.remove()
            engine.dispose()

        self.assertEqual(result, 1)

    def test_in_memory_sqlite_session_is_shared_across_threads(self) -> None:
        from backend.models import Base, SessionLocal, configure_session
        from backend.models.generation_task import GenerationTask
        from backend.models.input_profile import InputProfile
        from backend.models.user import User

        engine = configure_session("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(engine)

        session = SessionLocal()
        user = User(
            email="thread-db@example.com",
            username="thread-db",
            password_hash="hashed-password",
        )
        session.add(user)
        session.commit()

        profile = InputProfile(user_id=user.id)
        session.add(profile)
        session.commit()

        task = GenerationTask(user_id=user.id, input_profile_id=profile.id)
        session.add(task)
        session.commit()
        task_id = task.id
        session.close()

        result: dict[str, int | str | None] = {"task_id": None, "error": None}

        def fetch_task() -> None:
            worker_session = SessionLocal()
            try:
                fetched_task = worker_session.get(GenerationTask, task_id)
                result["task_id"] = fetched_task.id if fetched_task else None
            except Exception as exc:  # pragma: no cover - exercised in failing state
                result["error"] = str(exc)
            finally:
                worker_session.close()
                SessionLocal.remove()

        thread = threading.Thread(target=fetch_task)
        thread.start()
        thread.join()

        try:
            self.assertIsNone(result["error"])
            self.assertEqual(result["task_id"], task_id)
        finally:
            SessionLocal.remove()
            Base.metadata.drop_all(engine)
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
