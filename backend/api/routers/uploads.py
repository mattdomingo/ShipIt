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


@router.post("/resume/{upload_id}/parse-now", status_code=202, tags=["development"])
async def trigger_parsing(
    upload_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger the parsing process for an uploaded resume.
    
    **Note:** This is a temporary endpoint for development and testing.
    In a production environment, this would be handled by a background worker.
    """
    from ...parser.extractor import extract_resume_data_smart
    
    # Check if upload exists
    if upload_id not in upload_records:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    upload_record = upload_records[upload_id]
    
    # Check user authorization
    if upload_record["user_id"] != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Prevent re-parsing
    if upload_record["status"] == StatusEnum.PARSED:
        return JSONResponse(
            status_code=200,
            content={"message": "Resume already parsed"}
        )
    
    try:
        # Update status to PROCESSING
        upload_record["status"] = StatusEnum.PROCESSING
        
        # Parse the uploaded file
        file_path = upload_record["file_path"]
        resume_data = extract_resume_data_smart(file_path)
        
        # Convert to dictionary for JSON response
        parsed_data = {
            "upload_id": upload_id,
            "filename": upload_record["filename"],
            "contact": {
                "name": resume_data.contact.name,
                "email": resume_data.contact.email,
                "phone": resume_data.contact.phone,
                "linkedin": resume_data.contact.linkedin,
                "github": resume_data.contact.github,
            },
            "education": [
                {
                    "degree": edu.degree,
                    "institution": edu.institution,
                    "graduation_year": edu.graduation_year,
                    "gpa": edu.gpa,
                    "field": getattr(edu, 'field', None),
                } for edu in resume_data.education
            ],
            "experience": [
                {
                    "role": exp.role,
                    "company": exp.company,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "location": getattr(exp, 'location', None),
                    "description": exp.description,
                } for exp in resume_data.experience
            ],
            "skills": resume_data.skills,
            "additional_sections": {
                name: {
                    "title": section.title,
                    "content": section.content
                } for name, section in resume_data.additional_sections.items()
            },
            "summary": {
                "contact_fields_detected": sum([
                    bool(resume_data.contact.name),
                    bool(resume_data.contact.email),
                    bool(resume_data.contact.phone),
                    bool(resume_data.contact.linkedin),
                    bool(resume_data.contact.github)
                ]),
                "education_entries": len(resume_data.education),
                "experience_entries": len(resume_data.experience),
                "skills_count": len(resume_data.skills),
                "additional_sections_count": len(resume_data.additional_sections),
                "total_data_points": sum([
                    bool(resume_data.contact.name),
                    bool(resume_data.contact.email),
                    bool(resume_data.contact.phone),
                    bool(resume_data.contact.linkedin),
                    bool(resume_data.contact.github)
                ]) + len(resume_data.education) + len(resume_data.experience) + len(resume_data.skills)
            }
        }
        
        # Store parsed data and update status
        parsed_data_store[upload_id] = parsed_data
        upload_record["status"] = StatusEnum.PARSED
        
        return {"message": "Resume parsing initiated successfully"}
        
    except Exception as e:
        # If parsing fails, update status to FAILED
        upload_record["status"] = StatusEnum.FAILED
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse resume: {str(e)}"
        ) 