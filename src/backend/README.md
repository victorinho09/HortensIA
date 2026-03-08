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

## Running

Use the provided scripts from the `scripts/` directory:

```bash
# Start database + backend + iOS app (physical device)
sh scripts/start_device.sh

# Stop all services
sh scripts/stop_device.sh
```

### Viewing backend logs

The backend writes logs to `/tmp/backend.log`. To follow them in real time:

> **macOS**: `/tmp` is a symlink to `/private/tmp`, so `tail -f` requires the real path.

```bash
tail -f /private/tmp/backend.log
```
