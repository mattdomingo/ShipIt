"""
experience_extractor.py

Extracts work experience information from resume text including company names, roles, dates, and responsibilities.
Handles both text-based and layout-aware parsing for different resume formats.
"""

import re
from typing import List, Dict, Optional

from ..schemas import WorkExperience
from ..patterns import patterns
from ..constants import SectionHeaders, RoleKeywords


class ExperienceExtractor:
    """
    Extracts work experience information from resume text.
    """

    def __init__(self):
        """Initialize the experience extractor with patterns."""
        self.patterns = patterns

    def extract_experience(self, text: str) -> List[WorkExperience]:
        """Extract work experience from resume text."""
        from .section_parser import SectionParser
        
        experience_list = []
        section_parser = SectionParser()
        
        # Look for experience section
        experience_section = section_parser.find_section(text, SectionHeaders.EXPERIENCE)
        
        if experience_section:
            experience_list = self._parse_experience_section(experience_section)
        
        return experience_list

    def _parse_experience_section(self, section_text: str) -> List[WorkExperience]:
        """
        Parse the experience section handling different resume formats.
        
        Args:
            section_text (str): The experience section text
            
        Returns:
            List[WorkExperience]: Parsed work experiences
        """
        lines = [line.strip() for line in section_text.split('\n') if line.strip()]
        experiences = []
        current_experience = None
        description_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip section headers
            if any(header.lower() in line.lower() for header in ['experience', 'professional experience', 'work experience', 'employment']):
                i += 1
                continue
            
            # Skip bullet points - these are descriptions, not new jobs
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                if current_experience:
                    description_lines.append(line)
                i += 1
                continue
            
            # Check if this line looks like a company/location line
            if self._is_company_location_line(line):
                # Save previous experience if exists
                if current_experience and (current_experience.company or current_experience.role):
                    if description_lines:
                        current_experience.description = '\n'.join(description_lines)
                    experiences.append(current_experience)
                
                # Start new experience
                current_experience = WorkExperience()
                description_lines = []
                self._parse_company_location(line, current_experience)
                
                # Check if next line is role/date
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if self._is_role_date_line(next_line) and not next_line.startswith('•'):
                        self._parse_role_dates(next_line, current_experience)
                        i += 2  # Skip both company and role lines
                        continue
                
                i += 1
                
            # Check if this line looks like a role/date line (for pipe format or standalone)
            elif self._is_role_date_line(line):
                # Only treat as new job if we don't have a current experience or this looks like a standalone job
                if not current_experience or '|' in line:
                    # Save previous experience if switching to new one
                    if current_experience and (current_experience.company or current_experience.role):
                        if description_lines:
                            current_experience.description = '\n'.join(description_lines)
                        experiences.append(current_experience)
                    
                    current_experience = WorkExperience()
                    description_lines = []
                
                self._parse_role_dates(line, current_experience)
                
                # If this line has company info (pipe format), parse it
                if '|' in line:
                    self._parse_company_location(line, current_experience)
                
                i += 1
                
            # Other content lines - be more careful about treating these as new jobs
            else:
                # If we have an active experience, this might be description
                if current_experience:
                    # Only treat as new job if it really looks like one and we have substantial content already
                    if (self._might_be_new_job_entry(line, lines, i) and 
                        (current_experience.company or current_experience.role) and
                        len(description_lines) > 0):
                        
                        # Save current experience
                        if description_lines:
                            current_experience.description = '\n'.join(description_lines)
                        experiences.append(current_experience)
                        
                        # Start new experience
                        current_experience = WorkExperience()
                        description_lines = []
                        
                        # Try to parse this line
                        if self._is_company_location_line(line):
                            self._parse_company_location(line, current_experience)
                        else:
                            # Treat as a general line, might have mixed info
                            self._parse_mixed_line(line, current_experience)
                    else:
                        # Add to description unless it's clearly a different job
                        if not self._is_clearly_different_job(line, current_experience):
                            description_lines.append(line)
                        else:
                            # This looks like a different job
                            if description_lines:
                                current_experience.description = '\n'.join(description_lines)
                            experiences.append(current_experience)
                            
                            current_experience = WorkExperience()
                            description_lines = []
                            self._parse_mixed_line(line, current_experience)
                else:
                    # No current experience, try to start one
                    current_experience = WorkExperience()
                    description_lines = []
                    self._parse_mixed_line(line, current_experience)
                
                i += 1
        
        # Add the last experience
        if current_experience and (current_experience.company or current_experience.role):
            if description_lines:
                current_experience.description = '\n'.join(description_lines)
            experiences.append(current_experience)
        
        return experiences

    def _is_company_location_line(self, line: str) -> bool:
        """
        Check if a line looks like a company + location line.
        
        Examples:
        - "Inpro Corporation Muskego, WI"
        - "Google Inc. Mountain View, CA"
        - "Microsoft Seattle, WA"
        """
        # Look for location pattern (City, State)
        location_match = self.patterns.location_pattern.search(line)
        if location_match:
            # Check if the part before location looks like a company name
            company_part = line[:location_match.start()].strip()
            if company_part and not any(keyword.lower() in company_part.lower() for keyword in RoleKeywords.COMMON_ROLES):
                return True
        
        # Check for company indicators without location
        company_indicators = ['corporation', 'corp', 'inc', 'llc', 'ltd', 'company', 'group', 'associates']
        if any(indicator in line.lower() for indicator in company_indicators):
            # Make sure it's not a role description
            if not any(keyword.lower() in line.lower() for keyword in RoleKeywords.COMMON_ROLES):
                return True
        
        return False

    def _is_role_date_line(self, line: str) -> bool:
        """
        Check if a line looks like a role + date line.
        
        Examples:
        - "Finance Intern May 2025 – August 2025"
        - "Software Engineer | Google Inc. 2023-2024"
        - "Data Scientist June 2022 - Present"
        """
        # Check for role keywords
        has_role = any(keyword.lower() in line.lower() for keyword in RoleKeywords.COMMON_ROLES)
        
        # Check for date patterns
        has_dates = bool(self.patterns.year_pattern.search(line))
        
        # Check for pipe format
        has_pipe = '|' in line
        
        return has_role or has_dates or has_pipe

    def _might_be_new_job_entry(self, line: str, all_lines: List[str], current_index: int) -> bool:
        """
        Heuristic to determine if a line might start a new job entry.
        """
        # If it looks like a company line
        if self._is_company_location_line(line):
            return True
        
        # If it has role keywords and we're not in a bullet point
        if any(keyword.lower() in line.lower() for keyword in RoleKeywords.COMMON_ROLES):
            if not line.startswith('•') and not line.startswith('-'):
                return True
        
        # If the previous line was a bullet point and this doesn't start with a bullet
        if current_index > 0:
            prev_line = all_lines[current_index - 1]
            if (prev_line.startswith('•') or prev_line.startswith('-')) and not line.startswith('•') and not line.startswith('-'):
                # And this line looks substantial
                if len(line.split()) >= 3:
                    return True
        
        return False

    def _parse_company_location(self, text: str, experience: WorkExperience):
        """Parse company name and location from a line of text."""
        # Method 1: Pipe-separated format (Role | Company Location)
        if '|' in text:
            parts = text.split('|')
            if len(parts) >= 2:
                # In pipe format, company might be in second part
                company_location_part = parts[1].strip()
                location_match = self.patterns.location_pattern.search(company_location_part)
                if location_match:
                    experience.company = company_location_part[:location_match.start()].strip()
                    experience.location = f"{location_match.group(1)}, {location_match.group(2)}"
                else:
                    experience.company = company_location_part
                return
        
        # Method 2: Company + Location format
        location_match = self.patterns.location_pattern.search(text)
        if location_match:
            # The pattern might be too greedy and include company name in the city part
            # Try to extract a more reasonable city name
            full_city_part = location_match.group(1)
            state_part = location_match.group(2)
            
            # Split the city part and take the last few words as the actual city
            city_words = full_city_part.split()
            if len(city_words) > 2:
                # Likely format: "Company Name City", so take last 1-2 words as city
                actual_city = ' '.join(city_words[-2:]) if len(city_words) > 3 else city_words[-1]
                company_part = ' '.join(city_words[:-2]) if len(city_words) > 3 else ' '.join(city_words[:-1])
            else:
                # Short city name, probably correct
                actual_city = full_city_part
                company_part = text[:location_match.start()].strip()
            
            experience.company = company_part.strip() if company_part else None
            experience.location = f"{actual_city}, {state_part}"
            return
        
        # Method 3: Just company name (no clear location)
        # Remove common role words first
        clean_text = text
        for role_word in RoleKeywords.COMMON_ROLES:
            clean_text = re.sub(rf'\b{re.escape(role_word)}\b', '', clean_text, flags=re.IGNORECASE)
        
        clean_text = clean_text.strip()
        if clean_text and not experience.company:
            experience.company = clean_text

    def _parse_role_dates(self, text: str, experience: WorkExperience):
        """Parse role and dates from a line of text."""
        # Extract dates first
        date_matches = self.patterns.year_pattern.findall(text)
        if date_matches:
            if len(date_matches) >= 2:
                experience.start_date = date_matches[0]
                experience.end_date = date_matches[-1]
            elif len(date_matches) == 1:
                experience.start_date = date_matches[0]
                # Check for "Present" or similar
                if any(word in text.lower() for word in ['present', 'current', 'now']):
                    experience.end_date = 'Present'
        
        # Extract role (remove dates and clean up)
        role_text = text
        for date in date_matches:
            role_text = role_text.replace(date, '')
        
        # Remove common date separators and words
        role_text = re.sub(r'[–—-]+', '', role_text)  # Remove dashes
        role_text = re.sub(r'\b(present|current|now|to)\b', '', role_text, flags=re.IGNORECASE)
        role_text = re.sub(r'[|].*$', '', role_text)  # Remove everything after pipe
        role_text = re.sub(r'\s+', ' ', role_text).strip()  # Clean up whitespace
        
        if role_text and not experience.role:
            experience.role = role_text

    def _parse_mixed_line(self, text: str, experience: WorkExperience):
        """Parse a line that might contain mixed company/role information."""
        # Try to parse as company location first
        if not experience.company:
            self._parse_company_location(text, experience)
        
        # Try to parse as role if it contains role keywords
        if not experience.role and any(keyword.lower() in text.lower() for keyword in RoleKeywords.COMMON_ROLES):
            self._parse_role_dates(text, experience)

    def extract_experience_with_layout(self, sections: List[Dict], full_text: str) -> List[WorkExperience]:
        """Extract work experience using layout data."""
        experience_list = []
        
        # Find experience section in layout data
        experience_sections = []
        for section in sections:
            header = section.get('header', '').lower()
            if any(keyword in header for keyword in ['experience', 'employment', 'work', 'career', 'professional']):
                experience_sections.append(section)
        
        if not experience_sections:
            # Fallback to text-based extraction
            return self.extract_experience(full_text)
        
        for section in experience_sections:
            experience_entries = self._parse_experience_with_layout_enhanced(section)
            experience_list.extend(experience_entries)
        
        return experience_list

    def _parse_experience_with_layout_enhanced(self, experience_section: Dict) -> List[WorkExperience]:
        """Enhanced parsing using layout information to handle different resume formats."""
        content_lines = experience_section.get('content', [])
        
        # Convert layout data to text and use improved text parser
        text_lines = [line.get('text', '') for line in content_lines]
        text = '\n'.join(text_lines)
        return self._parse_experience_section(text)

    def _is_likely_company_name(self, text: str) -> bool:
        """Heuristic to determine if text looks like a company name."""
        if not text or len(text) < 2:
            return False
        
        # Skip if it looks like a role title
        role_indicators = ['engineer', 'developer', 'manager', 'analyst', 'intern', 'specialist']
        if any(indicator in text.lower() for indicator in role_indicators):
            return False
        
        # Skip if it's a date
        if re.search(r'\d{4}', text):
            return False
        
        # Company names usually have capital letters
        if not any(c.isupper() for c in text):
            return False
        
        return True

    def _is_clearly_different_job(self, line: str, current_experience: WorkExperience) -> bool:
        """
        Check if a line clearly represents a different job than the current one.
        """
        # If the line contains a different company name
        if current_experience.company:
            current_company_words = set(current_experience.company.lower().split())
            line_words = set(line.lower().split())
            
            # If the line contains company-like words that are completely different
            company_indicators = ['corporation', 'corp', 'inc', 'llc', 'ltd', 'company', 'group', 'associates']
            if any(indicator in line.lower() for indicator in company_indicators):
                # Check if any company words overlap
                if not current_company_words.intersection(line_words):
                    return True
        
        # If the line looks like a completely different role context
        if current_experience.role:
            # Check for very different role contexts
            current_role_context = current_experience.role.lower()
            if ('intern' in current_role_context and 'manager' in line.lower()) or \
               ('manager' in current_role_context and 'intern' in line.lower()):
                return True
        
        return False 