"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from .routers import health, users, items

app = FastAPI(
    title="FastAPI Service",
    version="1.0.0",
    description="REST API with FastAPI"
)

# Incluir routers
app.include_router(health.router, tags=["health"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(items.router, prefix="/api/items", tags=["items"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FastAPI",
        "version": "1.0.0",
        "docs": "/docs"
    }
