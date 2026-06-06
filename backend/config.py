import os

from dotenv import load_dotenv


load_dotenv()


def _is_production() -> bool:
    return os.getenv("APP_ENV", os.getenv("FLASK_ENV", "development")).lower() in {
        "production",
        "prod",
    }


def _parse_cors_origins(value: str | None) -> list[str] | str:
    if not value:
        return []
    origins = [origin.strip() for origin in value.split(",") if origin.strip()]
    if origins == ["*"]:
        return "*"
    return origins


def build_database_uri() -> str:
    database_uri = os.getenv("SQLALCHEMY_DATABASE_URI")
    if database_uri:
        return database_uri

    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = os.getenv("MYSQL_PORT", "3306")
    database = os.getenv("MYSQL_DATABASE", "bazi3d")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "change_me")

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


def get_config() -> dict:
    jwt_secret_key = os.getenv("JWT_SECRET_KEY")
    if _is_production() and not jwt_secret_key:
        raise RuntimeError("JWT_SECRET_KEY is required when APP_ENV is production")

    cors_allowed_origins = _parse_cors_origins(os.getenv("CORS_ALLOWED_ORIGINS"))
    if _is_production() and cors_allowed_origins in ("*", []):
        raise RuntimeError(
            "CORS_ALLOWED_ORIGINS must list explicit origins in production"
        )

    return {
        "SQLALCHEMY_DATABASE_URI": build_database_uri(),
        "JWT_SECRET_KEY": jwt_secret_key or "dev-secret-key",
        "CORS_ALLOWED_ORIGINS": cors_allowed_origins or "*",
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "ASSET_STORAGE_BUCKET": os.getenv("ASSET_STORAGE_BUCKET", ""),
        "ASSET_STORAGE_REGION": os.getenv("ASSET_STORAGE_REGION", ""),
        "ASSET_STORAGE_PUBLIC_BASE_URL": os.getenv(
            "ASSET_STORAGE_PUBLIC_BASE_URL", ""
        ),
        "SENTRY_DSN": os.getenv("SENTRY_DSN", ""),
        "MESHY_API_KEY": os.getenv("MESHY_API_KEY", ""),
        "MESHY_BASE_URL": os.getenv("MESHY_BASE_URL", "https://api.meshy.ai"),
        "TENCENTCLOUD_SECRET_ID": os.getenv(
            "TENCENTCLOUD_SECRET_ID", os.getenv("HUNYUAN_SECRET_ID", "")
        ),
        "TENCENTCLOUD_SECRET_KEY": os.getenv(
            "TENCENTCLOUD_SECRET_KEY", os.getenv("HUNYUAN_SECRET_KEY", "")
        ),
        "TENCENTCLOUD_REGION": os.getenv("TENCENTCLOUD_REGION", "ap-guangzhou"),
        "HUNYUAN_ENDPOINT": os.getenv(
            "HUNYUAN_ENDPOINT", "ai3d.tencentcloudapi.com"
        ),
    }
