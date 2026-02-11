"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .routers import health, users, auth

app = FastAPI(
    title="FastAPI Service",
    version="1.0.0",
    description="REST API with FastAPI"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom validation error handler that returns 400 status code
    with detailed field-level validation information.
    """
    errors = exc.errors()
    
    # Get the request body to identify valid fields
    try:
        body = await request.json()
    except:
        body = {}
    
    # Collect invalid field names
    invalid_fields = set()
    formatted_errors = []
    for error in errors:
        # Extract field name from location path
        field_location = error["loc"]
        field_name = field_location[-1] if len(field_location) > 1 else str(field_location)
        invalid_fields.add(field_name)
        
        formatted_errors.append({
            "field": field_name,
            "message": error["msg"],
            "type": error["type"],
            "status": "invalid"
        })
    
    # Add valid fields
    for field_name in body.keys():
        if field_name not in invalid_fields:
            formatted_errors.append({
                "field": field_name,
                "message": "Field is valid",
                "type": "valid",
                "status": "valid"
            })
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "message": "Validation failed",
            "endpoint": request.url.path,
            "method": request.method,
            "errors": formatted_errors
        }
    )

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FastAPI",
        "version": "1.0.0",
        "docs": "/docs"
    }
