"""
jobs.py

Background job processing for the resume tailor feature.
Uses Celery for asynchronous task processing.
Now integrates with parser, aggregator, and matcher modules.
"""

import os
import sys
import logging
import json
import redis
from datetime import datetime
from typing import Dict, Any
from celery import Celery

# Add the project root to the path so we can import from backend modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.parser.extractor import extract_resume_data_smart
from backend.aggregator.scraper import scrape_job_posting
from backend.matcher.tailor import generate_patch_plan

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    'shipit_jobs',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Redis client for shared storage
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(bind=True, name='parse_resume_job')
def parse_resume_job(self, upload_id: str, file_path: str, user_id: str) -> Dict[str, Any]:
    """
    Background job to parse a resume file using the parser module.
    
    Args:
        upload_id: Unique identifier for the upload
        file_path: Path to the uploaded resume file
        user_id: ID of the user who uploaded the resume
        
    Returns:
        Job result with parsed data
    """
    logger.info(f"Starting resume parsing job for upload_id: {upload_id}")
    
    try:
        # Import upload_records to update status
        from .routers.uploads import upload_records, parsed_data_store
        
        # Fix file path - ensure we're looking from the project root
        if not os.path.isabs(file_path):
            # Try multiple possible paths
            possible_paths = [
                file_path,  # Original path
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), file_path),  # From project root
                os.path.join("/Users/matthewdomingo/Documents/Personal/Project/ShipIt", file_path),  # Absolute project root
            ]
            
            actual_file_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    actual_file_path = path
                    break
            
            if actual_file_path:
                file_path = actual_file_path
                logger.info(f"Found file at: {file_path}")
            else:
                logger.error(f"File not found. Tried paths: {possible_paths}")
                raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        # Use the actual parser module to extract resume data
        resume_data = extract_resume_data_smart(file_path)
        
        # Convert to serializable format for storage
        parsed_data = resume_data.to_dict()
        
        # --- DEBUG LOGGING START ---
        logger.info("--- DETAILED PARSED DATA ---")
        logger.info(f"PARSED EDUCATION: {parsed_data.get('education')}")
        logger.info(f"PARSED EXPERIENCE: {parsed_data.get('experience')}")
        logger.info("--- END DETAILED PARSED DATA ---")
        # --- DEBUG LOGGING END ---
        
        # Store parsed data and update upload record status
        parsed_data_for_storage = {
            "upload_id": upload_id,
            "filename": upload_records.get(upload_id, {}).get("filename", "unknown.pdf"),
            "contact": parsed_data.get('contact', {}),
            "education": parsed_data.get('education', []),
            "experience": parsed_data.get('experience', []),
            "skills": parsed_data.get('skills', []),
            "additional_sections": parsed_data.get('additional_sections', {}),
            "summary": {
                "contact_fields_detected": sum([
                    bool(parsed_data.get('contact', {}).get('name')),
                    bool(parsed_data.get('contact', {}).get('email')),
                    bool(parsed_data.get('contact', {}).get('phone')),
                    bool(parsed_data.get('contact', {}).get('linkedin')),
                    bool(parsed_data.get('contact', {}).get('github'))
                ]),
                "education_entries": len(parsed_data.get('education', [])),
                "experience_entries": len(parsed_data.get('experience', [])),
                "skills_count": len(parsed_data.get('skills', [])),
                "additional_sections_count": len(parsed_data.get('additional_sections', {})),
                "total_data_points": sum([
                    bool(parsed_data.get('contact', {}).get('name')),
                    bool(parsed_data.get('contact', {}).get('email')),
                    bool(parsed_data.get('contact', {}).get('phone')),
                    bool(parsed_data.get('contact', {}).get('linkedin')),
                    bool(parsed_data.get('contact', {}).get('github'))
                ]) + len(parsed_data.get('education', [])) + len(parsed_data.get('experience', [])) + len(parsed_data.get('skills', []))
            }
        }
        
        # Store in Redis for shared access between Celery and API server
        redis_parsed_key = f"parsed_data:{upload_id}"
        redis_upload_key = f"upload_record:{upload_id}"
        
        # Store parsed data in Redis
        redis_client.setex(redis_parsed_key, 86400, json.dumps(parsed_data_for_storage))  # Expires in 24 hours
        logger.info(f"Stored parsed data in Redis for upload_id: {upload_id}")
        
        # Also store in local memory for backward compatibility
        parsed_data_store[upload_id] = parsed_data_for_storage
        
        # Update upload record status to PARSED (if record exists)
        if upload_id in upload_records:
            upload_records[upload_id]["status"] = "PARSED"
            # Store updated upload record in Redis
            upload_record_for_redis = upload_records[upload_id].copy()
            upload_record_for_redis["created_at"] = upload_record_for_redis["created_at"].isoformat()
            redis_client.setex(redis_upload_key, 86400, json.dumps(upload_record_for_redis))
            logger.info(f"Updated upload record status to PARSED for upload_id: {upload_id}")
        else:
            logger.warning(f"Upload record not found for upload_id: {upload_id} (server may have restarted)")
            # Create a minimal upload record so the parsed data can be accessed
            recovery_record = {
                "id": upload_id,
                "filename": "recovered_upload.pdf",
                "mime_type": "application/pdf",
                "status": "PARSED",
                "created_at": datetime.utcnow(),
                "user_id": user_id
            }
            upload_records[upload_id] = recovery_record
            # Store recovery record in Redis
            recovery_record_for_redis = recovery_record.copy()
            recovery_record_for_redis["created_at"] = recovery_record_for_redis["created_at"].isoformat()
            redis_client.setex(redis_upload_key, 86400, json.dumps(recovery_record_for_redis))
        
        result = {
            "upload_id": upload_id,
            "status": "PARSED",
            "parsed_data": parsed_data,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Resume parsing completed for upload_id: {upload_id}")
        return result
        
    except Exception as e:
        logger.error(f"Resume parsing failed for upload_id: {upload_id}, error: {str(e)}")
        
        # Update upload record status to FAILED
        try:
            from .routers.uploads import upload_records
            if upload_id in upload_records:
                upload_records[upload_id]["status"] = "FAILED"
                logger.info(f"Updated upload record status to FAILED for upload_id: {upload_id}")
        except Exception as status_error:
            logger.error(f"Failed to update upload record status: {status_error}")
        
        return {
            "upload_id": upload_id,
            "status": "FAILED",
            "error": str(e),
            "processed_at": datetime.utcnow().isoformat()
        }


@celery_app.task(bind=True, name='scrape_job_posting_job')
def scrape_job_posting_job(self, job_id: str, url: str, user_id: str) -> Dict[str, Any]:
    """
    Background job to scrape a job posting using the aggregator module.
    
    Args:
        job_id: Unique identifier for the job
        url: URL of the job posting to scrape
        user_id: ID of the user who requested the scraping
        
    Returns:
        Job result with scraped data
    """
    logger.info(f"Starting job scraping for job_id: {job_id}, url: {url}")
    
    try:
        # Use the actual aggregator module to scrape job posting
        job_posting = scrape_job_posting(url)
        
        # Convert to serializable format for storage
        scraped_data = {
            "title": job_posting.title,
            "company": job_posting.company,
            "location": job_posting.location,
            "description": job_posting.description,
            "requirements": job_posting.requirements,
            "salary": job_posting.salary,
            "employment_type": job_posting.employment_type,
            "url": job_posting.url
        }
        
        result = {
            "job_id": job_id,
            "url": url,
            "status": "READY",
            "scraped_data": scraped_data,
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Job scraping completed for job_id: {job_id}")
        return result
        
    except Exception as e:
        logger.error(f"Job scraping failed for job_id: {job_id}, error: {str(e)}")
        return {
            "job_id": job_id,
            "status": "FAILED",
            "error": str(e),
            "scraped_at": datetime.utcnow().isoformat()
        }


@celery_app.task(bind=True, name='generate_patch_plan_job')
def generate_patch_plan_job(self, plan_id: str, upload_id: str, job_id: str, user_id: str) -> Dict[str, Any]:
    """
    Background job to generate a patch plan using the matcher module.
    
    Args:
        plan_id: Unique identifier for the patch plan
        upload_id: ID of the uploaded resume
        job_id: ID of the job posting
        user_id: ID of the user requesting the plan
        
    Returns:
        Job result with generated patch plan
    """
    logger.info(f"Starting patch plan generation for plan_id: {plan_id}")
    
    try:
        # Handle imports for schemas - same pattern as above
        try:
            from ..parser.schemas import ResumeData, ContactInfo, Education, WorkExperience
            from ..aggregator.scraper import JobPosting
        except ImportError:
            from parser.schemas import ResumeData, ContactInfo, Education, WorkExperience
            from aggregator.scraper import JobPosting
        
        # Create dummy resume data (in production, this would come from storage)
        dummy_resume = ResumeData(
            contact=ContactInfo(name="John Doe", email="john@example.com"),
            education=[Education(degree="Bachelor's", field="Computer Science", institution="University")],
            experience=[WorkExperience(company="Tech Co", role="Developer", description="Built web applications")],
            skills=["Python", "JavaScript"],
            additional_sections={},
            raw_text="John Doe resume content..."
        )
        
        # Create dummy job posting (in production, this would come from storage)
        dummy_job = JobPosting(
            title="Software Engineer Intern",
            company="Example Corp",
            location="San Francisco, CA",
            description="Looking for a software engineering intern...",
            requirements=["Python", "JavaScript", "React"],
            salary="$25-30/hour",
            employment_type="Internship",
            url="https://example.com/jobs/123"
        )
        
        # Use the actual matcher module to generate patch plan
        patch_plan = generate_patch_plan(dummy_resume, dummy_job)
        
        result = {
            "plan_id": plan_id,
            "upload_id": upload_id,
            "job_id": job_id,
            "status": "READY",
            "patch_plan": patch_plan.to_dict(),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Patch plan generation completed for plan_id: {plan_id}")
        return result
        
    except Exception as e:
        logger.error(f"Patch plan generation failed for plan_id: {plan_id}, error: {str(e)}")
        return {
            "plan_id": plan_id,
            "status": "FAILED",
            "error": str(e),
            "generated_at": datetime.utcnow().isoformat()
        }


# Helper functions for enqueueing jobs
def enqueue_parse_resume(upload_id: str, file_path: str, user_id: str) -> str:
    """
    Enqueue a resume parsing job.
    
    Args:
        upload_id: Unique identifier for the upload
        file_path: Path to the uploaded resume file
        user_id: ID of the user who uploaded the resume
        
    Returns:
        Task ID for tracking the job
    """
    task = parse_resume_job.delay(upload_id, file_path, user_id)
    return task.id


def enqueue_scrape_job(job_id: str, url: str, user_id: str) -> str:
    """
    Enqueue a job scraping task.
    
    Args:
        job_id: Unique identifier for the job
        url: URL of the job posting to scrape
        user_id: ID of the user who requested the scraping
        
    Returns:
        Task ID for tracking the job
    """
    task = scrape_job_posting_job.delay(job_id, url, user_id)
    return task.id


def enqueue_generate_plan(plan_id: str, upload_id: str, job_id: str, user_id: str) -> str:
    """
    Enqueue a patch plan generation task.
    
    Args:
        plan_id: Unique identifier for the patch plan
        upload_id: ID of the uploaded resume
        job_id: ID of the job posting
        user_id: ID of the user requesting the plan
        
    Returns:
        Task ID for tracking the job
    """
    task = generate_patch_plan_job.delay(plan_id, upload_id, job_id, user_id)
    return task.id


def get_job_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a Celery task.
    
    Args:
        task_id: The task ID returned by enqueue functions
        
    Returns:
        Dictionary containing task status and result
    """
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "successful": result.successful() if result.ready() else None,
        "failed": result.failed() if result.ready() else None
    }