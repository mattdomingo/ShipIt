"""
uploads.py

Router for handling resume file uploads.
Provides the /v1/uploads/resume endpoint with file validation.
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import uuid
import os
import shutil
import json
import redis
from typing import Dict
from datetime import datetime

from ..models import UploadResponse, StatusEnum
from ..auth import get_current_user, User
from ..exceptions import FileValidationException
from ..jobs import enqueue_parse_resume

router = APIRouter()

# Redis client for shared storage
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Configuration
UPLOAD_DIR = "uploads/resumes"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_MIME_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory storage for demo purposes (replace with database in production)
upload_records: Dict[str, Dict] = {}
parsed_data_store: Dict[str, Dict] = {}


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
    
    # Check MIME type (some platforms send application/octet-stream)
    if file.content_type not in ALLOWED_MIME_TYPES:
        # Fall back to extension check – allow if extension is valid
        file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
        if file_ext in ALLOWED_EXTENSIONS:
            # Accept file even if MIME type is generic
            pass
        else:
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
        # Debug logging
        print(f"Received file upload: filename={file.filename}, content_type={file.content_type}, size={getattr(file, 'size', 'unknown')}")
        
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
        
        # Enqueue parsing job
        try:
            task_id = enqueue_parse_resume(upload_id, file_path, current_user.user_id)
            upload_record["task_id"] = task_id
            print(f"Successfully enqueued parsing job with task_id: {task_id}")
        except Exception as e:
            # If job enqueueing fails, we can still return the upload response
            # The parsing can be attempted later
            print(f"Failed to enqueue parsing job: {e}")
            pass
        
        # Return response
        response = UploadResponse(
            upload_id=upload_id,
            filename=file.filename,
            mime_type=file.content_type,
            status=StatusEnum.PENDING
        )
        
        return response
        
    except FileValidationException as e:
        # Log validation errors for debugging
        print(f"File validation failed: {e}")
        # Re-raise validation exceptions to be handled by exception handlers
        raise
    except Exception as e:
        # Handle unexpected errors
        print(f"Upload failed with error: {e}")
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
    # Check Redis for parsed data (shared between Celery and API server)
    redis_parsed_key = f"parsed_data:{upload_id}"
    redis_upload_key = f"upload_record:{upload_id}"
    
    parsed_data_json = redis_client.get(redis_parsed_key)
    upload_record_json = redis_client.get(redis_upload_key)
    
    # Check if upload exists in memory or Redis
    if upload_id not in upload_records:
        # Check if we have parsed data in Redis (Celery completed)
        if parsed_data_json:
            print(f"Upload record missing but parsed data exists in Redis for {upload_id}")
            parsed_data = json.loads(parsed_data_json)
            # Create recovery upload record
            upload_records[upload_id] = {
                "id": upload_id,
                "filename": parsed_data.get("filename", "recovered_upload.pdf"),
                "mime_type": "application/pdf",
                "status": StatusEnum.PARSED,
                "created_at": datetime.utcnow(),
                "user_id": current_user.user_id
            }
        # Check if upload record exists in Redis
        elif upload_record_json:
            print(f"Restoring upload record from Redis for {upload_id}")
            upload_record = json.loads(upload_record_json)
            upload_record["created_at"] = datetime.fromisoformat(upload_record["created_at"])
            upload_records[upload_id] = upload_record
        else:
            raise HTTPException(
                status_code=404,
                detail="Upload not found"
            )
    
    upload_record = upload_records[upload_id]
    
    # Check user authorization (skip for recovery records since we can't verify original user)
    if "recovered" not in upload_record.get("filename", "") and upload_record.get("user_id") != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
    # Check if parsing has completed but status wasn't updated
    if upload_record["status"] == StatusEnum.PENDING and (parsed_data_json or upload_id in parsed_data_store):
        print(f"Found parsed data for upload {upload_id}, updating status to PARSED")
        upload_record["status"] = StatusEnum.PARSED
    
    # Return current status
    return UploadResponse(
        upload_id=upload_id,
        filename=upload_record["filename"],
        mime_type=upload_record["mime_type"],
        status=upload_record["status"]
    )


@router.get("/resume/{upload_id}/parsed-data")
async def get_parsed_resume_data(
    upload_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the parsed resume data for a successfully processed upload.
    
    - **upload_id**: Unique identifier of the upload
    
    Returns the structured parsed resume data including contact info, 
    education, experience, skills, and additional sections.
    """
    # Check if upload exists
    if upload_id not in upload_records:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    upload_record = upload_records[upload_id]
    
    # Check user authorization
    if upload_record["user_id"] != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if parsing is complete
    if upload_record["status"] != StatusEnum.PARSED:
        raise HTTPException(
            status_code=400,
            detail=f"Resume parsing not complete. Current status: {upload_record['status']}"
        )
    
    # Retrieve parsed data from the in-memory store
    parsed_data = parsed_data_store.get(upload_id)
    
    if not parsed_data:
        raise HTTPException(
            status_code=404,
            detail="Parsed data not found for this upload"
        )
        
    return parsed_data




@router.get("/resume/{upload_id}/file")
async def get_resume_file(
    upload_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download or view the original resume file.
    
    - **upload_id**: Unique identifier of the upload
    
    Returns the original uploaded file for viewing or download.
    """
    # Check Redis for upload record (shared between Celery and API server)
    redis_upload_key = f"upload_record:{upload_id}"
    upload_record_json = redis_client.get(redis_upload_key)
    
    # Check if upload exists in memory or Redis
    if upload_id not in upload_records:
        if upload_record_json:
            print(f"Restoring upload record from Redis for file access: {upload_id}")
            upload_record = json.loads(upload_record_json)
            upload_record["created_at"] = datetime.fromisoformat(upload_record["created_at"])
            upload_records[upload_id] = upload_record
        else:
            raise HTTPException(
                status_code=404,
                detail="Upload not found"
            )
    
    upload_record = upload_records[upload_id]
    
    # Check user authorization (skip for recovery records since we can't verify original user)
    if "recovered" not in upload_record.get("filename", "") and upload_record.get("user_id") != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
    # Get the file path
    file_path = upload_record.get("file_path")
    if not file_path or not os.path.exists(file_path):
        # Try to reconstruct file path if missing
        file_ext = ".pdf" if upload_record.get("mime_type") == "application/pdf" else ".docx"
        reconstructed_path = os.path.join(UPLOAD_DIR, f"{upload_id}{file_ext}")
        
        if os.path.exists(reconstructed_path):
            file_path = reconstructed_path
        else:
            raise HTTPException(
                status_code=404,
                detail="File not found on disk"
            )
    
    # Return the file
    return FileResponse(
        path=file_path,
        filename=upload_record["filename"],
        media_type=upload_record.get("mime_type", "application/pdf")
    ) 