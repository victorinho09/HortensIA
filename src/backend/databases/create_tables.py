"""
Database initialization script

Run this to reset and create all database tables.
"""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy import inspect, text
from backend.databases.connection import init_db, engine


def reset_existing_tables() -> None:
    """
    Drop every existing table in the current schema before recreating it.

    This keeps the database aligned with the current SQLAlchemy models even
    when old tables no longer exist in the metadata, such as auth_identities.
    """
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if not existing_tables:
        print("No existing tables found. Skipping reset.")
        return

    print(f"Resetting {len(existing_tables)} existing table(s)...")
    with engine.connect() as conn:
        for table_name in existing_tables:
            print(f"Dropping table: {table_name}")
            conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;'))
        conn.commit()

if __name__ == "__main__":
    print("Resetting and creating database tables...")
    
    # Enable citext extension for case-insensitive text fields
    with engine.connect() as conn:
        print("Enabling citext extension...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext;"))
        conn.commit()
        print("✓ citext extension enabled")

    reset_existing_tables()
    
    # Create all tables
    init_db()
    print("✓ Database tables created successfully!")
    print(f"Connected to: {engine.url}")
