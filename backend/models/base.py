from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker


class Base(DeclarativeBase):
    pass


SessionLocal = scoped_session(sessionmaker(autoflush=False, autocommit=False))


def configure_session(database_uri: str, **engine_kwargs):
    engine = create_engine(database_uri, **engine_kwargs)
    SessionLocal.configure(bind=engine)
    return engine
