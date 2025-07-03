"""
exceptions.py

Exception handling and error response utilities for the ShipIt API.
Provides unified error responses with the {code, message, details} format.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging
from typing import Union

from .models import ErrorResponse

logger = logging.getLogger(__name__)


class ShipItException(Exception):
    """Base exception class for ShipIt API."""
    
    def __init__(self, code: str, message: str, details: Union[str, dict] = None, status_code: int = 400):
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(ShipItException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: Union[str, dict] = None):
        super().__init__("VALIDATION_ERROR", message, details, 400)


class FileValidationException(ShipItException):
    """Exception for file validation errors."""
    
    def __init__(self, message: str, details: Union[str, dict] = None):
        super().__init__("FILE_VALIDATION_ERROR", message, details, 400)


class NotFoundException(ShipItException):
    """Exception for resource not found errors."""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} not found"
        details = f"{resource} with ID '{identifier}' does not exist"
        super().__init__("NOT_FOUND", message, details, 404)


class AuthenticationException(ShipItException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__("AUTHENTICATION_ERROR", message, None, 401)


class AuthorizationException(ShipItException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__("AUTHORIZATION_ERROR", message, None, 403)


class ServiceUnavailableException(ShipItException):
    """Exception for service unavailable errors."""
    
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__("SERVICE_UNAVAILABLE", message, None, 503)


async def shipit_exception_handler(request: Request, exc: ShipItException) -> JSONResponse:
    """Handle ShipIt custom exceptions."""
    error_response = ErrorResponse(
        code=exc.code,
        message=exc.message,
        details=exc.details
    )
    
    logger.warning(f"ShipIt exception: {exc.code} - {exc.message}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    error_response = ErrorResponse(
        code="HTTP_ERROR",
        message=exc.detail,
        details=None
    )
    
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation exceptions."""
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = ErrorResponse(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details=error_details
    )
    
    logger.warning(f"Validation error: {error_details}")
    
    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    error_response = ErrorResponse(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        details=None
    )
    
    logger.error(f"Unexpected exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup all exception handlers for the FastAPI app."""
    app.add_exception_handler(ShipItException, shipit_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler) 