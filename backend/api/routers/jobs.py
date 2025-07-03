"""
jobs.py

Router for handling job posting scraping.
Provides the /v1/jobs/scrape endpoint for job URL processing.
"""

from fastapi import APIRouter, Depends, HTTPException
import uuid
from typing import Dict
from datetime import datetime

from ..models import ScrapeJobRequest, ScrapeResponse, StatusEnum
from ..auth import get_current_user, User
from ..exceptions import ValidationException
from ..jobs import enqueue_scrape_job

router = APIRouter()

# In-memory storage for demo purposes (replace with database in production)
job_records: Dict[str, Dict] = {}


@router.post("/scrape", response_model=ScrapeResponse, status_code=201)
async def scrape_job_posting(
    request: ScrapeJobRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger scraping of a job posting URL.
    
    - **url**: HTTPS URL of the job posting to scrape
    
    Returns scraping job confirmation with unique ID for tracking.
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Create job record (in production, save to database)
        job_record = {
            "id": job_id,
            "url": str(request.url),
            "status": StatusEnum.PENDING,
            "scraped_data": None,
            "created_at": datetime.utcnow(),
            "user_id": current_user.user_id
        }
        job_records[job_id] = job_record
        
        # Enqueue scraping job
        try:
            task_id = enqueue_scrape_job(job_id, str(request.url), current_user.user_id)
            job_record["task_id"] = task_id
        except Exception as e:
            # If job enqueueing fails, we can still return the response
            # The scraping can be attempted later
            pass
        
        # Return response
        response = ScrapeResponse(
            job_id=job_id,
            url=str(request.url),
            status=StatusEnum.PENDING
        )
        
        return response
        
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate job scraping: {str(e)}"
        )


@router.get("/scrape/{job_id}", response_model=ScrapeResponse)
async def get_scrape_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a job scraping operation.
    
    - **job_id**: Unique identifier of the scraping job
    
    Returns the current status of the scraping process.
    """
    # Check if job exists
    if job_id not in job_records:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    job_record = job_records[job_id]
    
    # Check user authorization
    if job_record["user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
    # Return current status
    return ScrapeResponse(
        job_id=job_id,
        url=job_record["url"],
        status=job_record["status"]
    ) 