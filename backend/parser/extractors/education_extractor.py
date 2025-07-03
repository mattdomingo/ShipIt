"""
education_extractor.py

Extracts education information from resume text including degrees, institutions, graduation years, and GPA.
"""

import re
from typing import List, Dict

from ..schemas import Education
from ..patterns import patterns
from ..constants import SectionHeaders


class EducationExtractor:
    """
    Extracts education information from resume text.
    """

    def __init__(self):
        """Initialize the education extractor with patterns."""
        self.patterns = patterns

    def extract_education(self, text: str) -> List[Education]:
        """Extract education information from resume text."""
        from .section_parser import SectionParser
        
        education_list = []
        section_parser = SectionParser()
        
        # Look for education section
        education_section_text = section_parser.find_section(text, SectionHeaders.EDUCATION)
        
        if education_section_text:
            # Split the section into entries based on blank lines
            entries = re.split(r'\n\s*\n', education_section_text.strip())
            for entry_text in entries:
                if not entry_text.strip():
                    continue
                
                education = self._parse_single_education_entry(entry_text)
                if education:
                    education_list.append(education)
        
        return education_list

    def extract_education_with_layout(self, sections: List[Dict], full_text: str) -> List[Education]:
        """Extract education information using layout data."""
        education_list = []
        
        # Find education section in layout data
        education_sections = []
        for section in sections:
            header = section.get('header', '').lower()
            if any(keyword in header for keyword in ['education', 'academic', 'school']):
                education_sections.append(section)
        
        if not education_sections:
            # Fallback to text-based extraction
            return self.extract_education(full_text)
        
        for section in education_sections:
            content_lines = section.get('content', [])
            education_entries = self._parse_education_section(content_lines)
            education_list.extend(education_entries)
        
        return education_list

    def _parse_education_section(self, content_lines: List[Dict]) -> List[Education]:
        """
        Parse education section from layout data.
        
        Args:
            content_lines (List[Dict]): Lines of content with layout information
            
        Returns:
            List[Education]: Parsed education entries
        """
        education_list = []
        
        # Group lines by potential education entries
        current_entry = []
        all_text = []
        
        for line in content_lines:
            text = line.get('text', '').strip()
            if text:
                all_text.append(text)
                current_entry.append(line)
        
        # Join all text and extract information
        full_text = '\n'.join(all_text)
        
        # Extract using patterns
        education = Education()
        
        # Extract degree
        degree_matches = self.patterns.degree_pattern.findall(full_text)
        if degree_matches:
            education.degree = degree_matches[0].title()
        
        # Extract institution
        institution_lines = [line for line in all_text 
                           if self.patterns.institution_pattern.search(line)]
        if institution_lines:
            education.institution = institution_lines[0].strip()
        
        # Extract year
        year_matches = self.patterns.year_pattern.findall(full_text)
        if year_matches:
            education.graduation_year = int(max(year_matches))
        
        # Extract GPA
        gpa_matches = self.patterns.gpa_pattern.findall(full_text)
        if gpa_matches:
            try:
                education.gpa = float(gpa_matches[0])
            except ValueError:
                pass
        
        if any([education.degree, education.institution, education.graduation_year]):
            education_list.append(education)
        
        return education_list

    def _extract_multiple_education_entries(self, text: str) -> List[Education]:
        """
        Extract multiple education entries from text.
        
        Args:
            text (str): Education section text
            
        Returns:
            List[Education]: List of education entries
        """
        education_list = []
        lines = text.split('\n')
        
        # Try to identify separate education entries
        # This is a heuristic approach - look for degree patterns or institution patterns
        current_entry_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line starts a new education entry
            if (self.patterns.degree_pattern.search(line) or 
                self.patterns.institution_pattern.search(line)):
                # Process previous entry if exists
                if current_entry_lines:
                    entry_text = '\n'.join(current_entry_lines)
                    education = self._parse_single_education_entry(entry_text)
                    if education:
                        education_list.append(education)
                # Start new entry
                current_entry_lines = [line]
            else:
                # Add to current entry
                current_entry_lines.append(line)
        
        # Process the last entry
        if current_entry_lines:
            entry_text = '\n'.join(current_entry_lines)
            education = self._parse_single_education_entry(entry_text)
            if education:
                education_list.append(education)
        
        return education_list

    def _parse_single_education_entry(self, text: str) -> Education:
        """
        Parse a single education entry from text.
        
        Args:
            text (str): Text for a single education entry
            
        Returns:
            Education: Parsed education entry or None
        """
        education = Education()
        
        # Extract degree
        degree_matches = self.patterns.degree_pattern.findall(text)
        if degree_matches:
            education.degree = degree_matches[0].title()
        
        # Extract institution
        institution_lines = [line for line in text.split('\n') 
                           if self.patterns.institution_pattern.search(line)]
        if institution_lines:
            education.institution = institution_lines[0].strip()
        
        # Extract year
        year_matches = self.patterns.year_pattern.findall(text)
        if year_matches:
            education.graduation_year = int(max(year_matches))
        
        # Extract GPA
        gpa_matches = self.patterns.gpa_pattern.findall(text)
        if gpa_matches:
            try:
                education.gpa = float(gpa_matches[0])
            except ValueError:
                pass
        
        # Return only if we found meaningful information
        if any([education.degree, education.institution, education.graduation_year]):
            return education
        
        return None 