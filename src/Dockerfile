# =============================================================================
# HortensIA - Detection server (Docker image)
# =============================================================================
# Self-contained image to run the FastAPI detection/risk-assessment server and
# the WebSocket simulator client. Designed so the TFG jury can launch the server
# with a single command and test detection using stored sample images, without
# Xcode, a physical device, PostgreSQL or a GPU.
#
# Build context is the `src/` directory (see docker-compose.yml).
# CPU-only: Apple MPS is not available inside Docker, so torch CPU is installed.
# =============================================================================

FROM python:3.11-slim

# ----------------------------------------------------------------------------
# System dependencies required by ultralytics/opencv (image decoding & OpenGL).
# ----------------------------------------------------------------------------
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Keep Python lean and unbuffered for live logs.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    # Tell ultralytics not to phone home / write config in random places.
    YOLO_CONFIG_DIR=/tmp/Ultralytics

WORKDIR /app

# ----------------------------------------------------------------------------
# Python dependencies.
# Install the CPU build of torch FIRST from the dedicated index so the much
# larger CUDA wheels are never pulled in. The backend requirements then reuse
# this already-satisfied torch.
# ----------------------------------------------------------------------------
RUN pip install --upgrade pip \
    && pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision

# Copy only the backend package (the build context already excludes the
# frontend, virtualenvs and caches via .dockerignore).
COPY backend/ ./backend/
COPY config.json ./config.json
COPY yolo26s.pt ./yolo26s.pt

# Install backend + simulator dependencies. The aggregator pulls models,
# service, databases, tests and ai (ultralytics/pillow) requirements.
RUN pip install -r backend/requirements.txt \
    && pip install -r backend/demo/requirements.txt

# Run the detection pipeline without the database-backed session validation.
ENV HORTENSIA_DEMO_MODE=1

EXPOSE 8888

# Default command: start the FastAPI server bound to all interfaces so it is
# reachable from the host and from the simulator container.
CMD ["uvicorn", "backend.service.main:app", "--host", "0.0.0.0", "--port", "8888"]
