from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


SessionLocal = scoped_session(sessionmaker(autoflush=False, autocommit=False))


def configure_session(database_uri: str, **engine_kwargs):
    if database_uri.startswith("sqlite") and ":memory:" in database_uri:
        engine_kwargs.setdefault("connect_args", {})
        engine_kwargs["connect_args"].setdefault("check_same_thread", False)
        engine_kwargs.setdefault("poolclass", StaticPool)
    engine = create_engine(database_uri, **engine_kwargs)
    SessionLocal.configure(bind=engine)
    return engine
