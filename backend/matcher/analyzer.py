"""
analyzer.py

Resume and job posting analysis utilities.
Provides functionality for analyzing compatibility between resumes and job postings.
"""

from typing import Dict, List, Tuple
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


class ResumeJobAnalyzer:
    """
    Analyzer for comparing resumes against job postings.
    """
    
    def __init__(self):
        pass
    
    def analyze_compatibility(self, resume_data: ResumeData, job_posting: JobPosting) -> Dict[str, any]:
        """
        Analyze compatibility between a resume and job posting.
        
        Args:
            resume_data: Parsed resume data
            job_posting: Job posting data
            
        Returns:
            Dict containing analysis results
        """
        logger.info(f"Analyzing compatibility for job: {job_posting.title}")
        
        # Skill matching analysis
        skill_analysis = self._analyze_skills_match(resume_data, job_posting)
        
        # Experience relevance analysis
        experience_analysis = self._analyze_experience_relevance(resume_data, job_posting)
        
        # Overall compatibility score
        compatibility_score = self._calculate_compatibility_score(skill_analysis, experience_analysis)
        
        return {
            "compatibility_score": compatibility_score,
            "skill_analysis": skill_analysis,
            "experience_analysis": experience_analysis,
            "recommendations": self._generate_recommendations(skill_analysis, experience_analysis)
        }
    
    def _analyze_skills_match(self, resume_data: ResumeData, job_posting: JobPosting) -> Dict[str, any]:
        """Analyze how well resume skills match job requirements."""
        if not job_posting.requirements:
            return {"match_percentage": 0, "matched_skills": [], "missing_skills": []}
        
        resume_skills = [skill.lower() for skill in resume_data.skills]
        job_requirements = [req.lower() for req in job_posting.requirements]
        
        matched_skills = []
        missing_skills = []
        
        for req in job_requirements:
            if any(req in resume_skill for resume_skill in resume_skills):
                matched_skills.append(req)
            else:
                missing_skills.append(req)
        
        match_percentage = len(matched_skills) / len(job_requirements) * 100 if job_requirements else 0
        
        return {
            "match_percentage": round(match_percentage, 2),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "total_requirements": len(job_requirements)
        }
    
    def _analyze_experience_relevance(self, resume_data: ResumeData, job_posting: JobPosting) -> Dict[str, any]:
        """Analyze how relevant the resume experience is to the job."""
        if not resume_data.experience:
            return {"relevance_score": 0, "relevant_experiences": []}
        
        job_keywords = self._extract_job_keywords(job_posting)
        relevant_experiences = []
        
        for i, experience in enumerate(resume_data.experience):
            relevance_score = self._calculate_experience_relevance(experience, job_keywords)
            if relevance_score > 0.3:  # Threshold for relevance
                relevant_experiences.append({
                    "index": i,
                    "company": experience.company,
                    "role": experience.role,
                    "relevance_score": relevance_score
                })
        
        overall_relevance = sum(exp["relevance_score"] for exp in relevant_experiences) / len(resume_data.experience)
        
        return {
            "relevance_score": round(overall_relevance, 2),
            "relevant_experiences": relevant_experiences,
            "total_experiences": len(resume_data.experience)
        }
    
    def _calculate_experience_relevance(self, experience, job_keywords: List[str]) -> float:
        """Calculate relevance score for a single experience."""
        if not experience.description:
            return 0.0
        
        description_words = experience.description.lower().split()
        keyword_matches = sum(1 for keyword in job_keywords if keyword in description_words)
        
        return min(keyword_matches / len(job_keywords), 1.0) if job_keywords else 0.0
    
    def _extract_job_keywords(self, job_posting: JobPosting) -> List[str]:
        """Extract relevant keywords from job posting."""
        keywords = []
        
        # Add requirements
        if job_posting.requirements:
            keywords.extend([req.lower() for req in job_posting.requirements])
        
        # Add title keywords
        if job_posting.title:
            title_words = job_posting.title.lower().split()
            keywords.extend([word for word in title_words if len(word) > 3])
        
        return list(set(keywords))  # Remove duplicates
    
    def _calculate_compatibility_score(self, skill_analysis: Dict, experience_analysis: Dict) -> float:
        """Calculate overall compatibility score."""
        skill_weight = 0.6
        experience_weight = 0.4
        
        skill_score = skill_analysis["match_percentage"] / 100
        experience_score = experience_analysis["relevance_score"]
        
        return round(skill_score * skill_weight + experience_score * experience_weight, 2)
    
    def _generate_recommendations(self, skill_analysis: Dict, experience_analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Skill-based recommendations
        if skill_analysis["missing_skills"]:
            missing_count = len(skill_analysis["missing_skills"])
            if missing_count > 3:
                recommendations.append(f"Consider adding {missing_count} missing key skills to your resume")
            else:
                recommendations.append(f"Add these missing skills: {', '.join(skill_analysis['missing_skills'][:3])}")
        
        # Experience-based recommendations
        if experience_analysis["relevance_score"] < 0.5:
            recommendations.append("Consider highlighting more relevant experience that aligns with job requirements")
        
        # Overall recommendations
        if not recommendations:
            recommendations.append("Your resume shows good alignment with this job posting")
        
        return recommendations 