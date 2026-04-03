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
            # If the old integer-ID schema is detected, drop and let
            # create_all() rebuild with the new string-ID schema.
            id_col = next(
                (c for c in insp.get_columns("applications") if c["name"] == "id"),
                None,
            )
            if id_col and "INTEGER" in str(id_col["type"]).upper():
                conn.execute(text("DROP TABLE applications"))
            else:
                if "community" not in app_cols:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN community VARCHAR"))
                if "property_type" not in app_cols:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN property_type VARCHAR"))
                if "size_sqft" not in app_cols:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN size_sqft FLOAT"))
                if "monthly_income_aed" not in app_cols:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN monthly_income_aed FLOAT"))
                if "credit_score" not in app_cols:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN credit_score INTEGER"))
                if "credit_utilization_pct" not in app_cols:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN credit_utilization_pct FLOAT"))
                if "existing_mortgage" not in app_cols:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN existing_mortgage BOOLEAN"))
                if "monthly_mortgage_payment_aed" not in app_cols:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN monthly_mortgage_payment_aed FLOAT"))
                if "user_id" not in app_cols:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN user_id INTEGER"))
                if "created_at" not in app_cols:
                    conn.execute(
                        text(
                            "ALTER TABLE applications ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT now()"
                        )
                    )

        if "contracts" in tables:
            contract_cols = {c["name"] for c in insp.get_columns("contracts")}
            if "status" not in contract_cols:
                conn.execute(text("ALTER TABLE contracts ADD COLUMN status VARCHAR DEFAULT 'draft'"))
            if "signature_data" not in contract_cols:
                conn.execute(text("ALTER TABLE contracts ADD COLUMN signature_data VARCHAR"))
            if "signed_at" not in contract_cols:
                conn.execute(text("ALTER TABLE contracts ADD COLUMN signed_at TIMESTAMPTZ"))