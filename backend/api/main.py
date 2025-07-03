"""
main.py

Main FastAPI application entry point for the ShipIt API.
Sets up the core API infrastructure with authentication, error handling, and routing.
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
import uvicorn
from typing import Dict, Any
import os

from .models import ErrorResponse
from .routers import uploads, jobs, tailor
from .auth import get_current_user, create_demo_token
from .exceptions import setup_exception_handlers

# Initialize FastAPI app
app = FastAPI(
    title="ShipIt API",
    description="Resume-powered internship finder with AI tailoring capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:19006",
        "http://172.16.0.169:3000",
        "http://172.16.0.169:19006",
        "exp://172.16.0.169:8081",  # Expo dev server
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Security scheme
security = HTTPBearer()

# Include routers
app.include_router(uploads.router, prefix="/v1/uploads", tags=["uploads"])
app.include_router(jobs.router, prefix="/v1/jobs", tags=["jobs"])
app.include_router(tailor.router, prefix="/v1/tailor", tags=["tailor"])

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "ShipIt API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "shipit-api"}

@app.api_route("/v1/auth/demo-token", methods=["GET", "POST"], tags=["auth"])
async def get_demo_token():
    """
    Obtain a demo authentication token (GET or POST).
    This avoids CORS pre-flight failures by allowing a simple GET request.
    """
    token = create_demo_token()
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 86400  # 24 hours
    }

# Explicit OPTIONS handler (usually handled by CORSMiddleware, but kept for platforms
# that still send a pre-flight to this no-body endpoint).
@app.options("/v1/auth/demo-token")
async def demo_token_options():
    return JSONResponse(status_code=200)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 