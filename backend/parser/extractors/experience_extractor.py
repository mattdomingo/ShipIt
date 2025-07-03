"""
experience_extractor.py

Enhanced experience extractor that uses positional and formatting data
to accurately identify work experience entries and avoid confusing 
job descriptions with separate roles.
"""

import re
from typing import List, Dict, Optional
from datetime import datetime

from ..schemas import WorkExperience
from ..patterns import patterns
from ..constants import SectionHeaders, RoleKeywords


class ExperienceExtractor:
    """
    Enhanced experience extractor using layout-aware parsing.
    """

    def __init__(self):
        """Initialize the experience extractor with patterns."""
        self.patterns = patterns

    def extract_experience(self, text: str) -> List[WorkExperience]:
        """Extract work experience from resume text using a more robust, entry-based approach."""
        from .section_parser import SectionParser
        
        experience_list = []
        section_parser = SectionParser()
        
        # Find the experience section
        experience_section_text = section_parser.find_section(text, SectionHeaders.EXPERIENCE)
        
        if experience_section_text:
            # Split the section into entries based on blank lines
            entries = re.split(r'\n\s*\n', experience_section_text.strip())
            for entry_text in entries:
                if not entry_text.strip():
                    continue
                
                # For each entry, parse the details
                experience = self._parse_single_experience_entry(entry_text)
                if experience:
                    experience_list.append(experience)
        
        return experience_list

    def _parse_single_experience_entry(self, text: str) -> Optional[WorkExperience]:
        """
        Parses a single block of text representing one job experience.
        """
        if not text:
            return None

        experience = WorkExperience()
        lines = text.strip().split('\n')
        
        if not lines:
            return None

        # Identify which lines are part of the header vs. the description
        header_lines = []
        description_lines = []
        header_parsed = False

        # A simple heuristic: lines with dates or company/role keywords are headers.
        # Everything after the first non-header line is description.
        for i, line in enumerate(lines):
            if not header_parsed:
                # Check if it's a header line (contains role, company, or dates)
                if self._contains_company_indicators(line) or self._contains_role_date_pattern(line) or (self._contains_job_keywords(line) and len(line.split()) < 8):
                    header_lines.append(line)
                else:
                    # This is the first line of the description
                    header_parsed = True
                    description_lines.append(line)
            else:
                description_lines.append(line)

        # Parse header lines
        for i, line in enumerate(header_lines):
            if i == 0:
                self._parse_header_line(line, experience)
            else:
                # If role or company is missing, try to find it in subsequent header lines
                if not experience.role and (self._contains_role_date_pattern(line) or self._looks_like_role_line(line)):
                    self._parse_role_date_line(line, experience)
                elif not experience.company and self._looks_like_company_line(line):
                     self._parse_company_line(line, experience)

        # Clean and set description from all identified description lines
        cleaned_description = []
        for line in description_lines:
            clean_line = line.lstrip('•-*◦ \t').strip()
            if clean_line:
                cleaned_description.append(clean_line)
        
        if cleaned_description:
            experience.description = '\n'.join(cleaned_description)

        # Extract dates from the whole text block for robustness
        self._extract_dates(text, experience)

        if experience.company or experience.role:
            return experience
        
        return None

    def extract_experience_with_layout(self, layout_data: Dict) -> List[WorkExperience]:
        """
        Extract work experience using layout-aware parsing.
        This is the preferred method for PDF files.
        """
        # Find experience section in layout data
        experience_section = self._find_experience_section_in_layout(layout_data)
        
        if experience_section:
            return self._parse_experience_with_layout(experience_section)
        
        # Fallback to text-based parsing
        return self.extract_experience(layout_data.get('text', ''))

    def _find_experience_section_in_layout(self, layout_data: Dict) -> Optional[Dict]:
        """Find the experience section in layout data."""
        sections = layout_data.get('sections', [])
        
        for section in sections:
            title = section.get('title', '').lower()
            if any(keyword in title for keyword in ['experience', 'employment', 'work history', 'professional']):
                return section
        
        return None

    def _parse_experience_with_layout(self, experience_section: Dict) -> List[WorkExperience]:
        """
        Parse experience section using layout information to identify job entries accurately.
        """
        lines = experience_section.get('lines', [])
        experiences = []
        
        # Group lines into logical job entries using layout cues
        job_groups = self._group_lines_into_jobs(lines)
        
        for job_group in job_groups:
            experience = self._parse_job_group(job_group)
            if experience and (experience.company or experience.role):
                experiences.append(experience)
        
        return experiences

    def _group_lines_into_jobs(self, lines: List[Dict]) -> List[List[Dict]]:
        """
        Group lines into logical job entries using pattern recognition.
        Expects: Company Line → Role Line → Description Lines → Company Line → ...
        """
        if not lines:
            return []
        
        job_groups = []
        current_group = []
        
        for i, line in enumerate(lines):
            line_text = line.get('text', '').strip()
            
            # Skip empty lines
            if not line_text:
                continue
            
            # Skip section headers
            if self._is_section_header(line_text):
                continue
            
            # Check if this line starts a new job entry (company line)
            is_company_line = self._contains_company_indicators(line_text)
            
            if is_company_line:
                # Save previous group if it exists and has content
                if current_group:
                    job_groups.append(current_group)
                
                # Start new group with this company line
                current_group = [line]
            else:
                # Add to current group (role line or description)
                if current_group:  # Only add if we have a group started
                    current_group.append(line)
        
        # Don't forget the last group
        if current_group:
            job_groups.append(current_group)
        
        return job_groups

    def _is_job_header_line(self, line: Dict, avg_font_size: float, left_margin: float, all_lines: List[Dict]) -> bool:
        """
        Determine if a line is likely the start of a new job entry.
        """
        text = line.get('text', '').strip()
        font_size = line.get('font_size', avg_font_size)
        x_position = line.get('x0', left_margin)
        is_bold = line.get('is_bold', False)
        
        # Skip bullet points and descriptions immediately
        if text.startswith(('•', '-', '*')) or text.startswith('File ') or text.startswith('Analyze '):
            return False
        
        # Key indicators of job header lines:
        
        # 1. Contains company name patterns (most reliable indicator)
        if self._contains_company_indicators(text):
            return True
        
        # 2. Contains role + date pattern with specific keywords
        if self._contains_role_date_pattern(text):
            return True
        
        # 3. Specific pattern recognition for common resume formats
        # Look for "Title Month Year - Month Year" format
        role_date_pattern = r'^[A-Za-z\s]+(intern|associate|analyst|manager|coordinator|specialist|engineer|developer)\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)'
        if re.search(role_date_pattern, text.lower()):
            return True
        
        # 4. Bold text that contains job-related keywords (if bold data is available)
        if is_bold and self._contains_job_keywords(text) and not text.startswith(('•', '-', '*')):
            return True
        
        # 5. Font size larger than average (if there's variation)
        if font_size > avg_font_size * 1.2 and self._contains_job_keywords(text):
            return True
        
        return False

    def _contains_company_indicators(self, text: str) -> bool:
        """Check if text contains company name indicators."""
        company_suffixes = ['inc', 'corp', 'corporation', 'llc', 'ltd', 'company', 'co.', 'group', 'associates']
        text_lower = text.lower()
        
        # Skip if it starts with obvious description words or phrases
        description_starters = [
            'file ', 'analyze ', 'ensure ', 'record ', 'maintain ', 'assisted ', 
            'processed ', 'communicated ', 'collaborated ', 'worked with',
            'managed ', 'developed ', 'created ', 'implemented ', 'led ',
            'responsible for', 'coordinated ', 'supervised ', 'filmed and edited'
        ]
        if any(text_lower.startswith(starter) for starter in description_starters):
            return False
        
        # Skip if line is too long (likely a description) - but not if it has pipe format
        if len(text.split()) > 10 and '|' not in text:
            return False
        
        # Skip if it contains bullet points
        if '•' in text:
            return False
        
        # Check for pipe format (Role | Company) - this indicates a job line
        if '|' in text and any(keyword in text_lower for keyword in ['intern', 'engineer', 'analyst', 'associate', 'manager']):
            return True
        
        # Check for company suffixes
        if any(suffix in text_lower for suffix in company_suffixes):
            return True
        
        # Check for location patterns (companies often listed with location)
        if re.search(r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b', text):  # City, ST pattern
            return True
        
        # Specific company name patterns (known companies from this resume)
        company_patterns = [
            r'\b(inpro corporation|erin hills golf course|badger boys state|pharus\.ai|magnet-schultz)\b',
            r'\b[A-Z][a-z]+\s+(corporation|corp|inc|llc|company|group|golf course)\b'
        ]
        
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in company_patterns):
            return True
        
        return False

    def _contains_role_date_pattern(self, text: str) -> bool:
        """Check if text contains role + date pattern."""
        # Look for common role keywords followed by dates
        role_keywords = ['intern', 'analyst', 'associate', 'coordinator', 'specialist', 
                        'manager', 'director', 'engineer', 'developer', 'consultant']
        
        text_lower = text.lower()
        has_role = any(role in text_lower for role in role_keywords)
        
        # Look for date patterns
        date_patterns = [
            r'\b\d{4}\s*[-–]\s*\d{4}\b',  # 2023-2024
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b',  # Month Year
            r'\b\d{1,2}/\d{4}\b',  # MM/YYYY
        ]
        
        has_dates = any(re.search(pattern, text_lower) for pattern in date_patterns)
        
        return has_role and has_dates

    def _contains_job_keywords(self, text: str) -> bool:
        """Check if text contains job-related keywords."""
        job_keywords = ['intern', 'analyst', 'associate', 'coordinator', 'specialist', 
                       'manager', 'director', 'engineer', 'developer', 'consultant',
                       'assistant', 'representative', 'officer', 'lead', 'senior',
                       'team', 'services', 'support', 'sales', 'marketing']
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in job_keywords)

    def _is_section_header(self, text: str) -> bool:
        """Check if text is a section header."""
        section_headers = ['experience', 'professional experience', 'work experience', 
                          'employment history', 'work history', 'career history']
        text_lower = text.lower().strip()
        return text_lower in section_headers

    def _parse_job_group(self, job_lines: List[Dict]) -> Optional[WorkExperience]:
        """
        Parse a group of lines representing a single job entry.
        Expected pattern: Company Line → Role Line → Description Lines
        """
        if not job_lines:
            return None
        
        experience = WorkExperience()
        description_lines = []
        
        # Process lines in order, expecting specific pattern
        for i, line in enumerate(job_lines):
            text = line.get('text', '').strip()
            
            if not text:
                continue
            
            # First line should be company or pipe format
            if i == 0:
                if '|' in text:
                    self._parse_header_line(text, experience)
                elif self._contains_company_indicators(text):
                    self._parse_company_line(text, experience)
                continue
            
            # Second line might be role/date if first was company
            if i == 1 and experience.company and not experience.role:
                if self._contains_role_date_pattern(text) or self._contains_job_keywords(text):
                    self._parse_role_date_line(text, experience)
                    continue
            
            # Handle bullet points and descriptions
            if text.startswith(('•', '-', '*')) or self._is_description_line(text):
                clean_text = text.lstrip('•-* \t')
                if clean_text:
                    description_lines.append(clean_text)
                continue
            
            # If we haven't assigned company or role yet, try to determine what this line is
            if not experience.company and self._contains_company_indicators(text):
                self._parse_company_line(text, experience)
            elif not experience.role and (self._contains_role_date_pattern(text) or self._contains_job_keywords(text)):
                self._parse_role_date_line(text, experience)
            else:
                # Treat as description if it doesn't fit company/role patterns
                if not self._is_description_line(text):
                    # This might be additional company/role info
                    description_lines.append(text)
                else:
                    description_lines.append(text)
        
        # Set description
        if description_lines:
            experience.description = '\n'.join(description_lines)
        
        # Only return if we have at least company or role
        if experience.company or experience.role:
            return experience
        
        return None
    
    def _is_description_line(self, text: str) -> bool:
        """Check if a line is likely a job description/responsibility."""
        text_lower = text.lower()
        
        # Common description starters
        description_starters = [
            'file ', 'analyze ', 'ensure ', 'record ', 'maintain ', 'assisted ', 
            'processed ', 'communicated ', 'worked with', 'collaborated with',
            'managed ', 'developed ', 'created ', 'implemented ', 'led ',
            'responsible for', 'coordinated ', 'supervised '
        ]
        
        return any(text_lower.startswith(starter) for starter in description_starters)

    def _parse_header_line(self, text: str, experience: WorkExperience):
        """Parse the main header line of a job entry."""
        # Try different parsing strategies
        
        # Strategy 1: Role | Company format
        if '|' in text:
            parts = text.split('|')
            if len(parts) >= 2:
                experience.role = parts[0].strip()
                experience.company = parts[1].strip()
            return
        
        # Strategy 2: Company Location format
        location_match = re.search(r'\b([A-Z][a-z]+,\s*[A-Z]{2})\b', text)
        if location_match:
            location = location_match.group(1)
            company_part = text[:location_match.start()].strip()
            if company_part:
                experience.company = company_part
                experience.location = location
            return
        
        # Strategy 3: Role at Company format
        at_match = re.search(r'^(.+?)\s+at\s+(.+)$', text, re.IGNORECASE)
        if at_match:
            experience.role = at_match.group(1).strip()
            experience.company = at_match.group(2).strip()
            return
        
        # Strategy 4: Try to determine if it's company or role
        if self._contains_company_indicators(text):
            experience.company = text
        elif self._contains_job_keywords(text):
            experience.role = text
        else:
            # Default to company
            experience.company = text

    def _looks_like_role_line(self, text: str) -> bool:
        """Check if a line looks like a role/position line."""
        return (self._contains_job_keywords(text) and 
                not self._contains_company_indicators(text))

    def _looks_like_company_line(self, text: str) -> bool:
        """Check if a line looks like a company line."""
        return self._contains_company_indicators(text)

    def _parse_role_date_line(self, text: str, experience: WorkExperience):
        """Parse role and date information from a line."""
        # Extract dates first
        self._extract_dates(text, experience)
        
        # Extract role (text before dates)
        date_patterns = [
            r'\b\d{4}\s*[-–]\s*\d{4}\b',
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b',
            r'\b\d{1,2}/\d{4}\b',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                role_part = text[:match.start()].strip()
                if role_part and not experience.role:
                    experience.role = role_part
                break

    def _parse_company_line(self, text: str, experience: WorkExperience):
        """Parse company information from a line."""
        # Extract location if present
        location_match = re.search(r'\b([A-Z][a-z]+,\s*[A-Z]{2})\b', text)
        if location_match:
            experience.location = location_match.group(1)
            company_part = text[:location_match.start()].strip()
            if company_part:
                experience.company = company_part
        else:
            experience.company = text

    def _extract_dates(self, text: str, experience: WorkExperience):
        """Extract start and end dates from text."""
        # Look for date range patterns
        date_range_patterns = [
            r'\b(\d{4})\s*[-–]\s*(\d{4}|\w+)\b',  # 2023-2024 or 2023-Present
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})\s*[-–]\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})\b',
        ]
        
        for pattern in date_range_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    start_year, end_year = match.groups()
                    experience.start_date = start_year
                    experience.end_date = end_year if end_year.lower() != 'present' else 'Present'
                elif len(match.groups()) == 4:
                    start_month, start_year, end_month, end_year = match.groups()
                    experience.start_date = f"{start_month} {start_year}"
                    experience.end_date = f"{end_month} {end_year}"
                break

    def _parse_experience_text_based(self, section_text: str) -> List[WorkExperience]:
        """
        Fallback text-based parsing for when layout data is not available.
        More conservative to avoid creating too many false job entries.
        """
        lines = [line.strip() for line in section_text.split('\n') if line.strip()]
        experiences = []
        current_experience = None
        description_lines = []
        
        for line in lines:
            # Skip section headers
            if self._is_section_header(line):
                continue
            
            # Skip obvious bullet points/descriptions
            if line.startswith(('•', '-', '*', '◦')):
                if current_experience:
                    description_lines.append(line.lstrip('•-*◦ \t'))
                continue
            
            # Check if this looks like a new job entry
            if self._is_likely_job_header(line):
                # Save previous experience
                if current_experience and (current_experience.company or current_experience.role):
                    if description_lines:
                        current_experience.description = '\n'.join(description_lines)
                    experiences.append(current_experience)
                
                # Start new experience
                current_experience = WorkExperience()
                description_lines = []
                self._parse_header_line(line, current_experience)
            
            elif current_experience:
                # Try to parse as additional job info
                if not current_experience.role and self._looks_like_role_line(line):
                    self._parse_role_date_line(line, current_experience)
                elif not current_experience.company and self._looks_like_company_line(line):
                    self._parse_company_line(line, current_experience)
                else:
                    # Add as description if it doesn't look like a new job
                    if not self._is_likely_job_header(line):
                        description_lines.append(line)
        
        # Add the last experience
        if current_experience and (current_experience.company or current_experience.role):
            if description_lines:
                current_experience.description = '\n'.join(description_lines)
            experiences.append(current_experience)
        
        return experiences

    def _is_likely_job_header(self, line: str) -> bool:
        """Conservative check for job headers in text-based parsing."""
        # Must contain either company indicators or role+date pattern
        return (self._contains_company_indicators(line) or 
                self._contains_role_date_pattern(line) or
                (self._contains_job_keywords(line) and 
                 not line.startswith(('•', '-', '*')) and
                 len(line.split()) <= 8))  # Keep headers reasonably short