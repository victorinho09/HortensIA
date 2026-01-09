"""
Health Check Router
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Service is running"
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}
