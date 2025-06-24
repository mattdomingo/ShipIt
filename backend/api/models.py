"""
models.py

Pydantic models for API request/response schemas.
Defines all data structures for the resume tailor feature.
"""

from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List, Union
from enum import Enum
import uuid
from datetime import datetime


class StatusEnum(str, Enum):
    """Status enum for various operations."""
    PENDING = "PENDING"
    PARSED = "PARSED"
    READY = "READY"
    FAILED = "FAILED"


class ActionEnum(str, Enum):
    """Action enum for patch plan items."""
    KEEP = "KEEP"
    DELETE = "DELETE"
    EDIT = "EDIT"
    INSERT_AFTER = "INSERT_AFTER"


# Upload Models
class UploadResponse(BaseModel):
    """Response model for resume upload."""
    upload_id: str
    filename: str
    mime_type: str
    status: StatusEnum = StatusEnum.PENDING
    
    class Config:
        json_schema_extra = {
            "example": {
                "upload_id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "resume.pdf",
                "mime_type": "application/pdf",
                "status": "PENDING"
            }
        }


# Job Scraping Models
class ScrapeJobRequest(BaseModel):
    """Request model for job scraping."""
    url: HttpUrl
    
    @validator('url')
    def validate_https(cls, v):
        if v.scheme != 'https':
            raise ValueError('URL must use HTTPS')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://careers.google.com/jobs/results/123456789"
            }
        }


class ScrapeResponse(BaseModel):
    """Response model for job scraping."""
    job_id: str
    url: str
    status: StatusEnum = StatusEnum.PENDING
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174001",
                "url": "https://careers.google.com/jobs/results/123456789",
                "status": "PENDING"
            }
        }


# Patch Plan Models
class PatchPlanItem(BaseModel):
    """Individual item in a patch plan."""
    id: str
    action: ActionEnum
    suggested_text: Optional[str] = None
    rationale: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "experience_1_bullet_2",
                "action": "EDIT",
                "suggested_text": "Developed scalable Python applications using Django and PostgreSQL",
                "rationale": "Highlight specific technologies mentioned in job posting"
            }
        }


class CreatePlanRequest(BaseModel):
    """Request model for creating a patch plan."""
    upload_id: str
    job_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "upload_id": "123e4567-e89b-12d3-a456-426614174000",
                "job_id": "123e4567-e89b-12d3-a456-426614174001"
            }
        }


class PlanResponse(BaseModel):
    """Response model for patch plan."""
    plan_id: str
    patch: List[PatchPlanItem]
    status: StatusEnum = StatusEnum.PENDING
    created_at: datetime
    upload_id: str
    job_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "123e4567-e89b-12d3-a456-426614174002",
                "patch": [
                    {
                        "id": "experience_1_bullet_1",
                        "action": "EDIT",
                        "suggested_text": "Built RESTful APIs using FastAPI and PostgreSQL",
                        "rationale": "Emphasize API development skills mentioned in job requirements"
                    }
                ],
                "status": "READY",
                "created_at": "2024-01-15T10:30:00Z",
                "upload_id": "123e4567-e89b-12d3-a456-426614174000",
                "job_id": "123e4567-e89b-12d3-a456-426614174001"
            }
        }


# Error Models
class ErrorResponse(BaseModel):
    """Standard error response model."""
    code: str
    message: str
    details: Optional[Union[str, dict]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid file type",
                "details": "Only PDF and DOCX files are allowed"
            }
        }


# Database Models (for internal use)
class UploadRecord(BaseModel):
    """Internal model for upload records."""
    id: str
    filename: str
    mime_type: str
    file_path: str
    status: StatusEnum
    created_at: datetime
    user_id: str


class JobRecord(BaseModel):
    """Internal model for job records."""
    id: str
    url: str
    status: StatusEnum
    scraped_data: Optional[dict] = None
    created_at: datetime
    user_id: str


class PlanRecord(BaseModel):
    """Internal model for plan records."""
    id: str
    upload_id: str
    job_id: str
    patch_data: List[dict]
    status: StatusEnum
    created_at: datetime
    user_id: str 