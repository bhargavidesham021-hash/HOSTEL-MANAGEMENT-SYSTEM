"""Copy every reflected SQLite table into an empty PostgreSQL database.

Set SQLITE_URL and DATABASE_URL, then run this script from backend/. It never
deletes target data and refuses to run if any target application table has rows.
"""
import os

from sqlalchemy import MetaData, create_engine, func, select
from sqlalchemy.engine import make_url
from werkzeug.security import generate_password_hash

LEGACY_UNUSED_TABLES = {"password_reset_otp"}


def normalize_postgres_url(value):
    if value.startswith("postgres://"):
        value = "postgresql://" + value[len("postgres://"):]
    parsed = make_url(value)
    if not parsed.drivername.startswith("postgresql"):
        raise SystemExit("DATABASE_URL must point to PostgreSQL.")
    if "sslmode" not in parsed.query:
        parsed = parsed.set(query={**parsed.query, "sslmode": "require"})
    return parsed.render_as_string(hide_password=False)


def main():
    source_url = os.getenv("SQLITE_URL", "").strip()
    if not source_url:
        raise SystemExit("Set SQLITE_URL explicitly to the SQLite database that should be migrated.")
    raw_target_url = os.getenv("DATABASE_URL", "").strip()
    if not raw_target_url or raw_target_url.startswith("sqlite:"):
        raise SystemExit("Set DATABASE_URL to the destination PostgreSQL connection string.")
    target_url = normalize_postgres_url(raw_target_url)

    source = create_engine(source_url)
    target = create_engine(target_url, pool_pre_ping=True, pool_size=1, max_overflow=0)
    source_meta, target_meta = MetaData(), MetaData()
    source_meta.reflect(bind=source)
    target_meta.reflect(bind=target)
    table_names = [table.name for table in source_meta.sorted_tables if table.name in target_meta.tables and table.name not in LEGACY_UNUSED_TABLES]
    missing = set(source_meta.tables) - set(target_meta.tables) - LEGACY_UNUSED_TABLES
    if missing:
        raise SystemExit("Destination schema is incomplete. Run initialize_postgres_schema.py first: " + ", ".join(sorted(missing)))

    source_rows = {}
    with source.connect() as source_conn:
        for name in table_names:
            source_rows[name] = source_conn.execute(select(source_meta.tables[name])).mappings().all()

    # Never carry the local owner's password hash into production. Require a
    # separately chosen production password and hash it before inserting.
    if "user" in source_rows and "role" in source_meta.tables["user"].columns:
        owners = [row for row in source_rows["user"] if row.get("role") == "owner"]
        if owners:
            owner_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
            owner_password = os.getenv("ADMIN_PASSWORD", "")
            if not owner_email or not owner_password:
                raise SystemExit("Set ADMIN_EMAIL and a new strong ADMIN_PASSWORD before migrating an existing owner account.")
            if len(owners) != 1 or str(owners[0].get("email", "")).lower() != owner_email:
                raise SystemExit("ADMIN_EMAIL must match the single existing local owner account; no data was copied.")
            owner_id = owners[0]["id"]
            source_rows["user"] = [
                {**row, "password_hash": generate_password_hash(owner_password) if row["id"] == owner_id else row["password_hash"]}
                for row in source_rows["user"]
            ]

    with target.begin() as conn:
        for name in table_names:
            table = target_meta.tables[name]
            if conn.execute(select(func.count()).select_from(table)).scalar_one():
                raise SystemExit(f"Destination table {name!r} is not empty; migration stopped without changing data.")

    copied = {}
    with target.begin() as target_conn:
        for name in table_names:
            src_table, dst_table = source_meta.tables[name], target_meta.tables[name]
            rows = source_rows[name]
            if rows:
                target_columns = set(dst_table.columns.keys())
                target_conn.execute(
                    dst_table.insert(),
                    [{key: value for key, value in row.items() if key in target_columns} for row in rows],
                )
            copied[name] = len(rows)

    # Preserve auto-increment behavior after importing explicit SQLite IDs.
    with target.begin() as conn:
        for name in table_names:
            table = target_meta.tables[name]
            pk = next(iter(table.primary_key.columns), None)
            if pk is not None and pk.autoincrement:
                conn.exec_driver_sql(
                    "SELECT setval(pg_get_serial_sequence(%s, %s), "
                    "COALESCE((SELECT MAX(%s) FROM %s), 1), "
                    "EXISTS (SELECT 1 FROM %s))" % (
                        "'" + name + "'", "'" + pk.name + "'", '"' + pk.name + '"',
                        '"' + name + '"', '"' + name + '"',
                    )
                )
    for name, count in copied.items():
        print(f"{name}: {count} rows")


if __name__ == "__main__":
    main()
