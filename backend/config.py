import os

from dotenv import load_dotenv


load_dotenv()


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
    return {
        "SQLALCHEMY_DATABASE_URI": build_database_uri(),
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "dev-secret-key"),
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
