#!/usr/bin/env python3
"""
run_server.py

Development server runner for the ShipIt API.
Use this script to start the API server locally for testing and development.
"""

import uvicorn
import sys
import os

# Add the project root directory to the Python path to resolve imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

if __name__ == "__main__":
    print("🚀 Starting ShipIt API server...")
    print("📚 API Documentation will be available at:")
    print("   • Swagger UI: http://localhost:8000/docs")
    print("   • ReDoc: http://localhost:8000/redoc")
    print("   • OpenAPI JSON: http://localhost:8000/openapi.json")
    print()
    print("🔑 For testing, you can use this demo token:")
    from backend.api.auth import DEMO_TOKEN
    print(f"   Authorization: Bearer {DEMO_TOKEN}")
    print()
    
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 