"""
patterns.py

Regex patterns for resume data extraction.
Contains compiled regex patterns for various resume sections and data types.
"""

import re
from typing import Dict


class RegexPatterns:
    """Collection of compiled regex patterns for resume parsing."""
    
    def __init__(self):
        """Initialize and compile all regex patterns."""
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for various data extraction."""
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone pattern (US format)
        self.phone_pattern = re.compile(
            r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
        )
        
        # LinkedIn profile pattern
        self.linkedin_pattern = re.compile(
            r'linkedin\.com/in/[\w-]+|linkedin\.com/pub/[\w-]+/[\w/]+'
        )
        
        # GitHub profile pattern
        self.github_pattern = re.compile(
            r'github\.com/[\w-]+'
        )
        
        # Education patterns
        self.degree_pattern = re.compile(
            r'\b(bachelor|master|phd|doctorate|associate|b\.?[sa]\.?|m\.?[sa]\.?|ph\.?d\.?)\b',
            re.IGNORECASE
        )
        
        # GPA pattern
        self.gpa_pattern = re.compile(
            r'gpa[:\s]*(\d\.?\d*)[/\s]*(?:4\.0)?',
            re.IGNORECASE
        )
        
        # Year pattern (for graduation years)
        self.year_pattern = re.compile(r'\b(19\d{2}|20\d{2})\b')
        
        # Common university/college indicators
        self.institution_pattern = re.compile(
            r'\b(university|college|institute|school)\b',
            re.IGNORECASE
        )
        
        # Job entry patterns for enhanced parsing
        # Job entry pattern with pipe separator: "Role | Company Location"
        self.job_pipe_pattern = re.compile(
            r'^(.+?)\s*\|\s*(.+?)$'
        )
        
        # Company with domain extension pattern  
        self.company_domain_pattern = re.compile(
            r'\b(\w+(?:\.\w+)*\.(com|ai|io|net|org|co|inc|llc|corp))\b',
            re.IGNORECASE
        )
        
        # Location pattern (City, State) - matches 1-3 word city names
        self.location_pattern = re.compile(
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}),\s*([A-Z]{2})\b'
        )
    
    def get_all_patterns(self) -> Dict[str, re.Pattern]:
        """
        Get a dictionary of all compiled patterns.
        
        Returns:
            Dict mapping pattern names to compiled regex objects
        """
        return {
            'email': self.email_pattern,
            'phone': self.phone_pattern,
            'linkedin': self.linkedin_pattern,
            'github': self.github_pattern,
            'degree': self.degree_pattern,
            'gpa': self.gpa_pattern,
            'year': self.year_pattern,
            'institution': self.institution_pattern,
            'job_pipe': self.job_pipe_pattern,
            'company_domain': self.company_domain_pattern,
            'location': self.location_pattern
        }


# Singleton instance for easy import
patterns = RegexPatterns() 