import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite file lives alongside the backend package by default; overridable via env
# var so tests can point at an isolated, throwaway database file.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./acme_salary.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a request-scoped DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
