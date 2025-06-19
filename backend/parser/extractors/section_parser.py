"""
section_parser.py

Handles section identification and text preprocessing for resume parsing.
Provides utilities for finding and extracting specific sections from resume text.
"""

import re
from typing import Dict, List, Optional

from ..constants import SectionHeaders


class SectionParser:
    """
    Handles section identification and text preprocessing.
    """

    def __init__(self):
        """Initialize the section parser."""
        pass

    def clean_text(self, text: str) -> str:
        """Clean and normalize the resume text."""
        # Preserve line breaks for section detection but clean up extra whitespace
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Clean each line but preserve structure
            cleaned_line = re.sub(r'\s+', ' ', line.strip())
            if cleaned_line:  # Only add non-empty lines
                cleaned_lines.append(cleaned_line)
        return '\n'.join(cleaned_lines)

    def find_section(self, text: str, section_keywords: List[str]) -> Optional[str]:
        """
        Find a specific section in the resume text.
        
        Args:
            text (str): The resume text to search
            section_keywords (List[str]): Keywords that identify the section
            
        Returns:
            Optional[str]: The section content if found, None otherwise
        """
        lines = text.split('\n')
        section_start = None
        section_end = None
        
        # Find section start
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(keyword.lower() in line_lower for keyword in section_keywords):
                section_start = i
                break
        
        if section_start is None:
            return None
        
        # Find section end (next section or end of text)
        for i in range(section_start + 1, len(lines)):
            line = lines[i].strip()
            if line and self._is_section_header(line):
                section_end = i
                break
        
        if section_end is None:
            section_end = len(lines)
        
        # Extract section content
        section_lines = lines[section_start:section_end]
        return '\n'.join(section_lines)

    def find_all_sections(self, text: str) -> Dict[str, str]:
        """
        Find all major sections in the resume.
        
        Args:
            text (str): The resume text to parse
            
        Returns:
            Dict[str, str]: Dictionary mapping section names to their content
        """
        sections = {}
        
        # Try to find each major section type
        section_types = {
            'education': SectionHeaders.EDUCATION,
            'experience': SectionHeaders.EXPERIENCE,
            'skills': SectionHeaders.SKILLS,
            'projects': SectionHeaders.PROJECTS,
            'certifications': SectionHeaders.CERTIFICATIONS
        }
        
        for section_name, keywords in section_types.items():
            section_content = self.find_section(text, keywords)
            if section_content:
                sections[section_name] = section_content
        
        return sections

    def _is_section_header(self, line: str) -> bool:
        """
        Check if a line appears to be a section header.
        
        Args:
            line (str): The line to check
            
        Returns:
            bool: True if the line appears to be a section header
        """
        line_lower = line.lower().strip()
        
        # Common section header patterns
        common_headers = [
            'education', 'experience', 'work experience', 'employment',
            'skills', 'technical skills', 'core competencies',
            'projects', 'personal projects', 'key projects',
            'certifications', 'certificates', 'awards',
            'summary', 'objective', 'profile',
            'activities', 'volunteer', 'leadership'
        ]
        
        # Check if line contains common section keywords
        for header in common_headers:
            if header in line_lower:
                return True
        
        # Check if line is short and potentially a header (heuristic)
        if len(line.split()) <= 3 and len(line) < 50:
            # Check if it's in all caps or title case
            if line.isupper() or line.istitle():
                return True
        
        return False

    def get_section_boundaries(self, text: str) -> List[Dict[str, any]]:
        """
        Get boundaries of all sections in the text.
        
        Args:
            text (str): The resume text to analyze
            
        Returns:
            List[Dict]: List of section boundary information
        """
        lines = text.split('\n')
        sections = []
        
        for i, line in enumerate(lines):
            if self._is_section_header(line):
                sections.append({
                    'line_number': i,
                    'header': line.strip(),
                    'start_index': i
                })
        
        # Add end indices
        for i in range(len(sections)):
            if i < len(sections) - 1:
                sections[i]['end_index'] = sections[i + 1]['start_index']
            else:
                sections[i]['end_index'] = len(lines)
        
        return sections 