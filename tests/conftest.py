import os

import pytest
from sqlalchemy_utils import create_database, database_exists


@pytest.fixture(scope="session")
def prepare_db() -> None:
    os.environ["DB_USER"] = "root"
    os.environ["DB_PASS"] = os.environ["DB_ROOT_PASS"]
    os.environ["DB_NAME"] = "test"

    from src.database import engine
    from src.models import Base

    if not database_exists(engine.url):
        create_database(engine.url)

    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db(prepare_db):
    from src.database import Session

    session = Session()
    session.begin_nested()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
