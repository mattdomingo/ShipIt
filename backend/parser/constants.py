"""
constants.py

Constants used throughout the resume parsing module.
Contains section headers, keywords, and other static data.
"""

from typing import List


class SectionHeaders:
    """Common section headers found in resumes."""
    
    EDUCATION = ['education', 'academic', 'academic background']
    EXPERIENCE = ['experience', 'work', 'employment', 'internship', 'work experience', 'professional experience']
    SKILLS = ['skills', 'technical', 'competencies', 'technical skills', 'core competencies']
    PROJECTS = ['projects', 'personal projects', 'academic projects']
    CERTIFICATIONS = ['certifications', 'certificates', 'credentials']
    REFERENCES = ['references']
    
    # All possible section headers for detecting section boundaries
    ALL_SECTIONS = (
        EDUCATION + EXPERIENCE + SKILLS + PROJECTS + 
        CERTIFICATIONS + REFERENCES
    )


class RoleKeywords:
    """Common role keywords found in job titles."""
    
    COMMON_ROLES = [
        'intern', 'engineer', 'developer', 'analyst', 'coordinator',
        'assistant', 'associate', 'manager', 'specialist', 'consultant',
        'director', 'lead', 'senior', 'junior', 'supervisor'
    ]
    
    TECHNICAL_ROLES = [
        'software engineer', 'data scientist', 'web developer',
        'frontend developer', 'backend developer', 'full stack developer',
        'devops engineer', 'qa engineer', 'security analyst',
        'database administrator', 'system administrator'
    ]


class ValidationConstants:
    """Constants used for data validation."""
    
    # Name validation
    MAX_NAME_LENGTH = 50
    MAX_NAME_WORDS = 4
    
    # Section header validation
    MAX_SECTION_HEADER_LENGTH = 50
    
    # Year range for graduation years
    MIN_GRADUATION_YEAR = 1970
    MAX_GRADUATION_YEAR = 2030
    
    # GPA validation
    MIN_GPA = 0.0
    MAX_GPA = 4.0 