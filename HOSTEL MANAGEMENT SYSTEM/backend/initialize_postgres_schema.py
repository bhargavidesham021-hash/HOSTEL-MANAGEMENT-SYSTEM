"""Create the PostgreSQL model schema without inserting seed data."""
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from app.extensions import db
from app import models  # noqa: F401 - registers all model tables in metadata


def main():
    value = os.getenv("DATABASE_URL", "").strip()
    if value.startswith("postgres://"):
        value = "postgresql://" + value[len("postgres://"):]
    if not value:
        raise SystemExit("Set DATABASE_URL to the Supabase PostgreSQL connection string.")
    url = make_url(value)
    if not url.drivername.startswith("postgresql"):
        raise SystemExit("DATABASE_URL must point to PostgreSQL.")
    if "sslmode" not in url.query:
        url = url.set(query={**url.query, "sslmode": "require"})
    engine = create_engine(url, pool_pre_ping=True, pool_size=1, max_overflow=0)
    db.metadata.create_all(engine)
    print("PostgreSQL schema created (existing tables and rows were preserved).")
    engine.dispose()


if __name__ == "__main__":
    main()
