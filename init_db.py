from backend.app import create_app
from backend.models import Base, configure_session

app = create_app()

engine = configure_session(app.config["SQLALCHEMY_DATABASE_URI"])

Base.metadata.create_all(engine)

print("✅ tables created in bazi3d")