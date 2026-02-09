# Backend

Backend services for TFG application.

## Requirements

- PostgreSQL 15+ installed and running
- Python dependencies from requirements.txt files

### Verify PostgreSQL is running

To check if PostgreSQL is running, use:

```bash
brew services info postgresql@15
```

The output should show `Running: ✔` if the database is active.

## Structure

```
backend/
├── service/              # REST API (FastAPI)
└── databases/
    ├── data_storage/     # Relational database (PostgreSQL)
    └── media_storage/    # Media files storage
```

## Services

### REST API Service

FastAPI application providing REST endpoints.

**Location:** `service/`  
**Port:** 8000  
**Documentation:** http://localhost:8000/docs

### Data Storage

PostgreSQL database for structured data.

**Location:** `databases/data_storage/`  
**Dependencies:** SQLAlchemy

### Media Storage

Storage service for media files (images, videos).

**Location:** `databases/media_storage/`  
**Dependencies:** boto3, Pillow
