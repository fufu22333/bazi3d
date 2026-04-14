import os
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
            "mysql+pymysql://root:change_me@127.0.0.1:3306/bazi3d",
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
            "mysql+pymysql://demo:secret@db.internal:3307/custom_db",
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


if __name__ == "__main__":
    unittest.main()
