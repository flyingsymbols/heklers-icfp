"""
DB connection management
"""
from sqlmodel import Session, SQLModel, create_engine

from .config import DATABASE_CONFIG

engine = create_engine(**DATABASE_CONFIG)


def create_db_and_tables():
    """
    Create the database and schema idempotently
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependency injection session management
    Use with fastapi Depends
    """
    with Session(engine) as session:
        yield session
