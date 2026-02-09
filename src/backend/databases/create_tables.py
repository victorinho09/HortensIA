"""
Database initialization script

Run this to create all database tables.
"""

from sqlalchemy import text
from backend.databases.connection import init_db, engine
from backend.databases.models import Base

if __name__ == "__main__":
    print("Creating database tables...")
    
    # Enable citext extension for case-insensitive text fields
    with engine.connect() as conn:
        print("Enabling citext extension...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext;"))
        conn.commit()
        print("✓ citext extension enabled")
    
    # Create all tables
    init_db()
    print("✓ Database tables created successfully!")
    print(f"Connected to: {engine.url}")
