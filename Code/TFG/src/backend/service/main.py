"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from .routers import health, signup

app = FastAPI(
    title="FastAPI Service",
    version="1.0.0",
    description="REST API with FastAPI"
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(signup.router, prefix="/signup", tags=["signup"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FastAPI",
        "version": "1.0.0",
        "docs": "/docs"
    }
