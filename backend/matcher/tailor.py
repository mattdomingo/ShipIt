"""
tailor.py

Resume tailoring logic for generating patch plans.
This module handles the AI-powered resume customization that was previously in the API layer.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

import sys
import os

# Add backend path for imports
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from parser.schemas import ResumeData
    from aggregator.scraper import JobPosting
except ImportError:
    # Fallback for when modules aren't available
    ResumeData = None
    JobPosting = None

logger = logging.getLogger(__name__)


class ActionEnum(str, Enum):
    """Action enum for patch plan items."""
    KEEP = "KEEP"
    DELETE = "DELETE"
    EDIT = "EDIT"
    INSERT_AFTER = "INSERT_AFTER"


@dataclass
class PatchPlanItem:
    """Individual item in a patch plan."""
    id: str
    action: ActionEnum
    suggested_text: str = None
    rationale: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization."""
        return {
            "id": self.id,
            "action": self.action.value,
            "suggested_text": self.suggested_text,
            "rationale": self.rationale
        }


@dataclass
class PatchPlan:
    """Complete patch plan for resume tailoring."""
    items: List[PatchPlanItem]
    resume_id: str
    job_id: str
    match_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization."""
        return {
            "items": [item.to_dict() for item in self.items],
            "resume_id": self.resume_id,
            "job_id": self.job_id,
            "match_score": self.match_score
        }


class ResumeTailor:
    """
    Main class for generating resume tailoring suggestions.
    """
    
    def __init__(self):
        self.skill_keywords = self._load_skill_keywords()
    
    def generate_patch_plan(self, resume_data: ResumeData, job_posting: JobPosting) -> PatchPlan:
        """
        Generate a patch plan to tailor the resume for the specific job.
        
        Args:
            resume_data: Parsed resume data
            job_posting: Scraped job posting data
            
        Returns:
            PatchPlan: List of suggested modifications
        """
        logger.info(f"Generating patch plan for job: {job_posting.title}")
        
        patch_items = []
        
        # Analyze skill gaps
        skill_patches = self._analyze_skills_gap(resume_data, job_posting)
        patch_items.extend(skill_patches)
        
        # Analyze experience relevance
        experience_patches = self._analyze_experience_relevance(resume_data, job_posting)
        patch_items.extend(experience_patches)
        
        # Analyze keywords alignment
        keyword_patches = self._analyze_keyword_alignment(resume_data, job_posting)
        patch_items.extend(keyword_patches)
        
        # Calculate match score
        match_score = self._calculate_match_score(resume_data, job_posting)
        
        return PatchPlan(
            items=patch_items,
            resume_id="resume_data",  # This would be the actual resume ID in production
            job_id="job_posting",     # This would be the actual job ID in production
            match_score=match_score
        )
    
    def _analyze_skills_gap(self, resume_data: ResumeData, job_posting: JobPosting) -> List[PatchPlanItem]:
        """Analyze skills gap between resume and job requirements."""
        patches = []
        
        resume_skills = [skill.lower() for skill in resume_data.skills]
        job_requirements = [req.lower() for req in job_posting.requirements]
        
        # Find missing skills
        missing_skills = []
        for req in job_requirements:
            if not any(req in resume_skill for resume_skill in resume_skills):
                missing_skills.append(req)
        
        if missing_skills:
            patches.append(PatchPlanItem(
                id="skills_section",
                action=ActionEnum.INSERT_AFTER,
                suggested_text=", ".join(missing_skills[:3]),  # Add top 3 missing skills
                rationale=f"Add key skills mentioned in job requirements: {', '.join(missing_skills[:3])}"
            ))
        
        return patches
    
    def _analyze_experience_relevance(self, resume_data: ResumeData, job_posting: JobPosting) -> List[PatchPlanItem]:
        """Analyze and suggest improvements to experience descriptions."""
        patches = []
        
        job_keywords = self._extract_keywords_from_job(job_posting)
        
        for i, experience in enumerate(resume_data.experience):
            if experience.description:
                # Check if experience description contains job-relevant keywords
                exp_words = experience.description.lower().split()
                keyword_matches = sum(1 for keyword in job_keywords if keyword in exp_words)
                
                if keyword_matches < 2:  # If less than 2 relevant keywords
                    # Suggest enhancing the description
                    relevant_keywords = job_keywords[:2]  # Take top 2 keywords
                    patches.append(PatchPlanItem(
                        id=f"experience_{i}_description",
                        action=ActionEnum.EDIT,
                        suggested_text=f"{experience.description} Utilized {', '.join(relevant_keywords)} to deliver results.",
                        rationale=f"Enhance experience description to highlight {', '.join(relevant_keywords)} mentioned in job posting"
                    ))
        
        return patches
    
    def _analyze_keyword_alignment(self, resume_data: ResumeData, job_posting: JobPosting) -> List[PatchPlanItem]:
        """Analyze overall keyword alignment and suggest improvements."""
        patches = []
        
        job_keywords = self._extract_keywords_from_job(job_posting)
        resume_text = resume_data.raw_text.lower()
        
        # Find important keywords missing from resume
        missing_keywords = []
        for keyword in job_keywords:
            if keyword not in resume_text:
                missing_keywords.append(keyword)
        
        # If too many keywords are missing, suggest adding them to a summary or objective
        if len(missing_keywords) >= 3:
            patches.append(PatchPlanItem(
                id="summary_section",
                action=ActionEnum.INSERT_AFTER,
                suggested_text=f"Experienced in {', '.join(missing_keywords[:3])} with strong problem-solving abilities.",
                rationale="Add professional summary highlighting key job requirements"
            ))
        
        return patches
    
    def _extract_keywords_from_job(self, job_posting: JobPosting) -> List[str]:
        """Extract important keywords from job posting."""
        keywords = []
        
        # Add requirements as keywords
        if job_posting.requirements:
            keywords.extend([req.lower() for req in job_posting.requirements])
        
        # Extract keywords from description (simplified approach)
        if job_posting.description:
            # This is a simplified keyword extraction
            # In a real implementation, you'd use NLP techniques
            common_tech_terms = [
                'python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker',
                'kubernetes', 'machine learning', 'data analysis', 'agile', 'scrum'
            ]
            
            description_lower = job_posting.description.lower()
            for term in common_tech_terms:
                if term in description_lower and term not in keywords:
                    keywords.append(term)
        
        return keywords[:10]  # Return top 10 keywords
    
    def _calculate_match_score(self, resume_data: ResumeData, job_posting: JobPosting) -> float:
        """Calculate a match score between resume and job posting."""
        if not job_posting.requirements:
            return 0.5  # Default score if no requirements
        
        resume_skills = [skill.lower() for skill in resume_data.skills]
        job_requirements = [req.lower() for req in job_posting.requirements]
        
        matches = 0
        for req in job_requirements:
            if any(req in resume_skill for resume_skill in resume_skills):
                matches += 1
        
        return min(matches / len(job_requirements), 1.0)
    
    def _load_skill_keywords(self) -> Dict[str, List[str]]:
        """Load skill keywords for better matching."""
        # This would typically load from a file or database
        return {
            'programming': ['python', 'java', 'javascript', 'c++', 'go', 'rust'],
            'web': ['react', 'angular', 'vue', 'html', 'css', 'nodejs'],
            'database': ['sql', 'postgresql', 'mysql', 'mongodb', 'redis'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'data': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn']
        }


# Convenience function
def generate_patch_plan(resume_data: ResumeData, job_posting: JobPosting) -> PatchPlan:
    """
    Convenience function to generate a patch plan.
    
    Args:
        resume_data: Parsed resume data
        job_posting: Job posting data
        
    Returns:
        PatchPlan: Generated patch plan
    """
    tailor = ResumeTailor()
    return tailor.generate_patch_plan(resume_data, job_posting) 