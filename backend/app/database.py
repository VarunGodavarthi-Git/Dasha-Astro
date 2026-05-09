import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = ROOT_DIR / "data" / "vedic_astrology.db"
load_dotenv(ROOT_DIR / "backend" / ".env")


def _database_url() -> str:
    url = os.getenv("BACKEND_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        return f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"
    if url.startswith("file:"):
        raw_path = url.removeprefix("file:")
        return f"sqlite:///{(ROOT_DIR / raw_path).resolve().as_posix()}"
    return url


DATABASE_URL = _database_url()
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
