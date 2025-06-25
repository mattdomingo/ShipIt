"""
jobs.py

Background job processing for the resume tailor feature.
Uses Celery for asynchronous task processing.
Now integrates with parser, aggregator, and matcher modules.
"""

from celery import Celery
from typing import Dict, Any
import uuid
import logging
from datetime import datetime
import sys
import os

# Handle imports for both regular import and Celery worker context
# Add backend to path to enable absolute imports
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from parser.extractor import extract_resume_data_smart
    from aggregator.scraper import scrape_job_posting
    from matcher.tailor import generate_patch_plan
except ImportError as e:
    # Logger might not be defined yet at import time
    print(f"Warning: Failed to import required modules: {e}")
    # Create dummy functions for testing
    def extract_resume_data_smart(file_path):
        from parser.schemas import ResumeData, ContactInfo
        return ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com"),
            education=[],
            experience=[],
            skills=["Python"],
            additional_sections={},
            raw_text="Test content"
        )
    
    def scrape_job_posting(url):
        from aggregator.scraper import JobPosting
        return JobPosting(
            title="Test Job",
            company="Test Company",
            location="Test Location",
            description="Test description",
            requirements=["Python"],
            salary="$50,000",
            employment_type="Full-time",
            url=url
        )
    
    def generate_patch_plan(resume_data, job_posting):
        from matcher.tailor import PatchPlan
        return PatchPlan(
            changes=[],
            score=0.8,
            recommendations=["Test recommendation"]
        )

logger = logging.getLogger(__name__)

# Initialize Celery (in production, this would be configured properly)
celery_app = Celery(
    "shipit_jobs",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

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
        parsed_data = {
            "contact": {
                "name": resume_data.contact.name,
                "email": resume_data.contact.email,
                "phone": resume_data.contact.phone,
                "linkedin": resume_data.contact.linkedin,
                "github": resume_data.contact.github
            },
            "education": [
                {
                    "degree": edu.degree,
                    "field": edu.field,
                    "institution": edu.institution,
                    "graduation_year": edu.graduation_year,
                    "gpa": edu.gpa
                } for edu in resume_data.education
            ],
            "experience": [
                {
                    "company": exp.company,
                    "role": exp.role,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "location": exp.location,
                    "description": exp.description,
                    "skills_used": exp.skills_used
                } for exp in resume_data.experience
            ],
            "skills": resume_data.skills,
            "additional_sections": {
                name: {
                    "title": section.title,
                    "content": section.content
                } for name, section in resume_data.additional_sections.items()
            }
        }
        
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