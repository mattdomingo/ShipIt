"""
uploads.py

Router for handling resume file uploads.
Provides the /v1/uploads/resume endpoint with file validation.
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uuid
import os
import shutil
from typing import Dict
from datetime import datetime

from ..models import UploadResponse, StatusEnum
from ..auth import get_current_user, User
from ..exceptions import FileValidationException
from ..jobs import enqueue_parse_resume

router = APIRouter()

# Configuration
UPLOAD_DIR = "uploads/resumes"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_MIME_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory storage for demo purposes (replace with database in production)
upload_records: Dict[str, Dict] = {}


def validate_file(file: UploadFile) -> None:
    """
    Validate uploaded file against requirements.
    
    Args:
        file: The uploaded file
        
    Raises:
        FileValidationException: If file doesn't meet requirements
    """
    # Check file size
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise FileValidationException(
            "File too large",
            {"max_size": "5MB", "received_size": f"{file.size / 1024 / 1024:.2f}MB"}
        )
    
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise FileValidationException(
            "Invalid file type",
            {
                "allowed_types": ["PDF", "DOCX"],
                "received_type": file.content_type,
                "message": "Only PDF and DOCX files are allowed"
            }
        )
    
    # Check file extension
    if file.filename:
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise FileValidationException(
                "Invalid file extension",
                {
                    "allowed_extensions": [".pdf", ".docx"],
                    "received_extension": file_ext,
                    "message": "File must have .pdf or .docx extension"
                }
            )


@router.post("/resume", response_model=UploadResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a resume file (PDF or DOCX).
    
    - **file**: Resume file (PDF or DOCX, max 5MB)
    
    Returns upload confirmation with unique ID for tracking.
    """
    try:
        # Validate file
        validate_file(file)
        
        # Generate unique upload ID
        upload_id = str(uuid.uuid4())
        
        # Create safe filename
        file_ext = os.path.splitext(file.filename)[1].lower()
        safe_filename = f"{upload_id}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create upload record (in production, save to database)
        upload_record = {
            "id": upload_id,
            "filename": file.filename,
            "mime_type": file.content_type,
            "file_path": file_path,
            "status": StatusEnum.PENDING,
            "created_at": datetime.utcnow(),
            "user_id": current_user.user_id
        }
        upload_records[upload_id] = upload_record
        
        # Enqueue parsing job (placeholder - just mark as parsed for now)
        try:
            task_id = enqueue_parse_resume(upload_id, file_path, current_user.user_id)
            upload_record["task_id"] = task_id
        except Exception as e:
            # If job enqueueing fails, we can still return the upload response
            # The parsing can be attempted later
            pass
        
        # Return response
        response = UploadResponse(
            upload_id=upload_id,
            filename=file.filename,
            mime_type=file.content_type,
            status=StatusEnum.PENDING
        )
        
        return response
        
    except FileValidationException:
        # Re-raise validation exceptions to be handled by exception handlers
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.get("/resume/{upload_id}", response_model=UploadResponse)
async def get_upload_status(
    upload_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of an uploaded resume.
    
    - **upload_id**: Unique identifier of the upload
    
    Returns the current status of the upload and parsing process.
    """
    # Check if upload exists
    if upload_id not in upload_records:
        raise HTTPException(
            status_code=404,
            detail="Upload not found"
        )
    
    upload_record = upload_records[upload_id]
    
    # Check user authorization
    if upload_record["user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
    # Return current status
    return UploadResponse(
        upload_id=upload_id,
        filename=upload_record["filename"],
        mime_type=upload_record["mime_type"],
        status=upload_record["status"]
    ) 