"""
Database initialization script

Run this to create all database tables.
"""

from backend.databases.connection import init_db, engine
from backend.databases.models import Base

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("✓ Database tables created successfully!")
    print(f"Connected to: {engine.url}")
