from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from src.settings.getters import get_database_url


SQLALCHEMY_DATABASE_URL = get_database_url()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = scoped_session(
    sessionmaker(
        bind=engine,
        autoflush=True,
        autocommit=False,
    )
)
