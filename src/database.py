import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Load DATABASE_URL from the .env file located next to this module.
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing. Check your .env file.")

# Sync engine (no async / no greenlet dependency).
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# SQLAlchemy model base
Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_db_schema() -> None:
    """
    Apply minimal schema upgrades for local/dev environments.

    `Base.metadata.create_all()` does NOT alter existing tables, so if you already
    have a persisted Postgres volume from an older model, new columns may be
    missing and the app will crash on startup.
    """
    insp = inspect(engine)
    tables = set(insp.get_table_names())

    with engine.begin() as conn:
        if "users" in tables:
            user_cols = {c["name"] for c in insp.get_columns("users")}
            if "created_at" not in user_cols:
                conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT now()"
                    )
                )

        if "properties" in tables:
            prop_cols = {c["name"] for c in insp.get_columns("properties")}
            if "created_at" not in prop_cols:
                conn.execute(
                    text(
                        "ALTER TABLE properties ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT now()"
                    )
                )

        if "applications" in tables:
            app_cols = {c["name"] for c in insp.get_columns("applications")}
            if "user_id" not in app_cols:
                conn.execute(text("ALTER TABLE applications ADD COLUMN user_id INTEGER"))
            if "created_at" not in app_cols:
                conn.execute(
                    text(
                        "ALTER TABLE applications ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT now()"
                    )
                )