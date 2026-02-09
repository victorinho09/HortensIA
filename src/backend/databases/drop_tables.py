"""
Database cleanup script

Run this to drop all database tables.
WARNING: This will delete all data in the tables!
"""

from sqlalchemy import text, inspect
from backend.databases.connection import drop_db, engine

if __name__ == "__main__":
    print("\n" + "="*60)
    print("⚠️  WARNING: DATABASE TABLE DELETION")
    print("="*60)
    
    # Show existing tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if not existing_tables:
        print("No tables found in the database.")
        print("="*60 + "\n")
        exit(0)
    
    print(f"Found {len(existing_tables)} table(s) in the database:")
    for table in existing_tables:
        print(f"  - {table}")
    
    print("\nThis operation will:")
    print("  1. Drop all tables with CASCADE (removes dependencies)")
    print("  2. Delete ALL data in these tables")
    print("  3. This action CANNOT be undone")
    print("="*60)
    
    # Prompt for confirmation
    confirmation = input("\nType 'DELETE' to confirm deletion: ")
    
    if confirmation != "DELETE":
        print("\n❌ Deletion cancelled. No changes made.")
        print("="*60 + "\n")
        exit(0)
    
    print("\nDropping database tables...")
    
    try:
        # Drop all tables (CASCADE ensures dependent objects are removed)
        # This handles foreign key constraints and data automatically
        drop_db()
        
        # Verify tables are dropped
        inspector = inspect(engine)
        remaining_tables = inspector.get_table_names()
        
        if remaining_tables:
            print(f"\n⚠️  Warning: {len(remaining_tables)} table(s) still exist:")
            for table in remaining_tables:
                print(f"  - {table}")
        else:
            print("✓ All database tables dropped successfully!")
            print("✓ All data has been deleted")
        
        print(f"Connected to: {engine.url}")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error dropping tables: {str(e)}")
        print("="*60 + "\n")
        raise
