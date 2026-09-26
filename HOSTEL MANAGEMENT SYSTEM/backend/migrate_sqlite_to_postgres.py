"""Copy every reflected SQLite table into an empty PostgreSQL database.

Set SQLITE_URL and DATABASE_URL, then run this script from backend/. It never
deletes target data and refuses to run if any target application table has rows.
"""
import os

from sqlalchemy import MetaData, create_engine, func, inspect, select


def normalize_postgres_url(value):
    if value.startswith("postgres://"):
        return "postgresql://" + value[len("postgres://"):]
    return value


def main():
    source_url = os.getenv("SQLITE_URL", "sqlite:///hostel.db")
    target_url = normalize_postgres_url(os.getenv("DATABASE_URL", "").strip())
    if not target_url or target_url.startswith("sqlite:"):
        raise SystemExit("Set DATABASE_URL to the destination PostgreSQL connection string.")

    source = create_engine(source_url)
    target = create_engine(target_url, pool_pre_ping=True)
    source_meta, target_meta = MetaData(), MetaData()
    source_meta.reflect(bind=source)
    target_meta.reflect(bind=target)
    table_names = [table.name for table in source_meta.sorted_tables if table.name in target_meta.tables]
    missing = set(source_meta.tables) - set(target_meta.tables)
    if missing:
        raise SystemExit("Destination is missing tables. Start the app once to create schema: " + ", ".join(sorted(missing)))

    with target.begin() as conn:
        for name in table_names:
            table = target_meta.tables[name]
            if conn.execute(select(func.count()).select_from(table)).scalar_one():
                raise SystemExit(f"Destination table {name!r} is not empty; migration stopped without changing data.")

    copied = {}
    with source.connect() as source_conn, target.begin() as target_conn:
        for name in table_names:
            src_table, dst_table = source_meta.tables[name], target_meta.tables[name]
            rows = source_conn.execute(select(src_table)).mappings().all()
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
