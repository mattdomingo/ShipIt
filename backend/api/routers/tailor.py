"""
tailor.py

Router for handling resume tailoring and patch plan generation.
Provides endpoints for creating and retrieving patch plans.
"""

from fastapi import APIRouter, Depends, HTTPException
import uuid
from typing import Dict
from datetime import datetime

from ..models import CreatePlanRequest, PlanResponse, StatusEnum, PatchPlanItem, ActionEnum
from ..auth import get_current_user, User
from ..exceptions import ValidationException, NotFoundException
from ..jobs import enqueue_generate_plan

router = APIRouter()

# In-memory storage for demo purposes (replace with database in production)
plan_records: Dict[str, Dict] = {}

# Mock external records access (in production, these would be database lookups)
from .uploads import upload_records
from .jobs import job_records


def validate_plan_request(request: CreatePlanRequest, user_id: str) -> None:
    """
    Validate that the upload and job exist and belong to the user.
    
    Args:
        request: The plan creation request
        user_id: ID of the requesting user
        
    Raises:
        NotFoundException: If upload or job not found
        ValidationException: If access denied
    """
    # Check upload exists
    if request.upload_id not in upload_records:
        raise NotFoundException("Upload", request.upload_id)
    
    # Check job exists  
    if request.job_id not in job_records:
        raise NotFoundException("Job", request.job_id)
    
    # Check ownership
    upload_record = upload_records[request.upload_id]
    job_record = job_records[request.job_id]
    
    if upload_record["user_id"] != user_id:
        raise ValidationException("Upload does not belong to user")
    
    if job_record["user_id"] != user_id:
        raise ValidationException("Job does not belong to user")
    
    # Check status (uploads should be parsed, jobs should be ready)
    if upload_record["status"] != StatusEnum.PARSED:
        raise ValidationException(
            "Resume must be parsed before creating plan",
            {"upload_status": upload_record["status"]}
        )
    
    if job_record["status"] != StatusEnum.READY:
        raise ValidationException(
            "Job must be scraped before creating plan",
            {"job_status": job_record["status"]}
        )


@router.post("/plan", response_model=PlanResponse, status_code=201)
async def create_patch_plan(
    request: CreatePlanRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a patch plan by combining a resume and job posting.
    
    - **upload_id**: ID of the uploaded and parsed resume
    - **job_id**: ID of the scraped job posting
    
    Returns a patch plan with suggested resume modifications.
    """
    try:
        # Validate request
        validate_plan_request(request, current_user.user_id)
        
        # Generate unique plan ID
        plan_id = str(uuid.uuid4())
        
        # Generate actual patch plan using matcher module
        # Note: In production, you would fetch actual parsed resume and job data
        # For now, we'll use the matcher with dummy data to demonstrate integration
        from ...matcher.tailor import generate_patch_plan
        from ...parser.schemas import ResumeData, ContactInfo, Education, WorkExperience
        from ...aggregator.scraper import JobPosting
        
        # Create dummy data (in production, fetch from storage using upload_id and job_id)
        dummy_resume = ResumeData(
            contact=ContactInfo(name="User", email="user@example.com"),
            education=[Education(degree="Bachelor's", institution="University")],
            experience=[WorkExperience(company="Company", role="Developer")],
            skills=["Python", "JavaScript"],
            additional_sections={},
            raw_text="Resume content..."
        )
        
        dummy_job = JobPosting(
            title="Software Engineer",
            company="Target Company",
            requirements=["Python", "React", "SQL"],
            description="Job description..."
        )
        
        # Generate actual patch plan
        patch_plan = generate_patch_plan(dummy_resume, dummy_job)
        mock_patch = [
            PatchPlanItem(
                id=item.id,
                action=ActionEnum(item.action),
                suggested_text=item.suggested_text,
                rationale=item.rationale
            ) for item in patch_plan.items
        ]
        
        # Create plan record (in production, save to database)
        plan_record = {
            "id": plan_id,
            "upload_id": request.upload_id,
            "job_id": request.job_id,
            "patch_data": [item.dict() for item in mock_patch],
            "status": StatusEnum.PENDING,
            "created_at": datetime.utcnow(),
            "user_id": current_user.user_id
        }
        plan_records[plan_id] = plan_record
        
        # Enqueue plan generation job
        try:
            task_id = enqueue_generate_plan(plan_id, request.upload_id, request.job_id, current_user.user_id)
            plan_record["task_id"] = task_id
        except Exception as e:
            # If job enqueueing fails, we can still return the response
            # The plan generation can be attempted later
            pass
        
        # Return response with mock data for now
        response = PlanResponse(
            plan_id=plan_id,
            patch=mock_patch,
            status=StatusEnum.READY,  # Mock as ready for demo
            created_at=plan_record["created_at"],
            upload_id=request.upload_id,
            job_id=request.job_id
        )
        
        return response
        
    except (NotFoundException, ValidationException):
        # Re-raise validation exceptions to be handled by exception handlers
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create patch plan: {str(e)}"
        )


@router.get("/plan/{plan_id}", response_model=PlanResponse)
async def get_patch_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a previously created patch plan.
    
    - **plan_id**: Unique identifier of the patch plan
    
    Returns the complete patch plan with all suggested modifications.
    """
    # Check if plan exists
    if plan_id not in plan_records:
        raise NotFoundException("Plan", plan_id)
    
    plan_record = plan_records[plan_id]
    
    # Check user authorization
    if plan_record["user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
    # Convert stored patch data back to PatchPlanItem objects
    patch_items = [PatchPlanItem(**item) for item in plan_record["patch_data"]]
    
    # Return plan response
    return PlanResponse(
        plan_id=plan_id,
        patch=patch_items,
        status=plan_record["status"],
        created_at=plan_record["created_at"],
        upload_id=plan_record["upload_id"],
        job_id=plan_record["job_id"]
    ) 