"""
Database Connection and Session Management

Handles SQLAlchemy engine creation and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import json
from pathlib import Path


__all__ = ["get_db", "get_db_context", "init_db", "drop_db", "engine", "SessionLocal"]


# Load database configuration from config.json
def load_db_config():
    """Load database configuration from config.json"""
    config_path = Path(__file__).parent.parent.parent / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['database']['postgresql']

db_config = load_db_config()

# Build DATABASE_URL from config
db_password = ""
DATABASE_URL = (
    f"postgresql://{db_config['user'] + ':'}"
    f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True, 
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Create sessionmaker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Session:
    """
    Dependency function for FastAPI to provide database sessions.
    
    Usage in routes:
        @router.post("/")
        async def endpoint(db: Session = Depends(get_db)):
            # Use db here
    
    Yields:
        Database session that auto-closes after request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined in models.py.
    """
    from .models import Base
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all database tables.
    WARNING: This deletes all data!
    """
    from .models import Base
    Base.metadata.drop_all(bind=engine)
