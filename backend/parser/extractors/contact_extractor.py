"""
contact_extractor.py

Extracts contact information from resume text including email, phone, name, and social links.
"""

import re
from typing import List, Dict, Optional

from ..schemas import ContactInfo
from ..patterns import patterns
from ..constants import ValidationConstants


class ContactExtractor:
    """
    Extracts contact information from resume text.
    """

    def __init__(self):
        """Initialize the contact extractor with patterns."""
        self.patterns = patterns

    def extract_contact_info(self, text: str) -> ContactInfo:
        """Extract contact information from resume text."""
        contact = ContactInfo()
        
        # Extract email
        email_matches = self.patterns.email_pattern.findall(text)
        if email_matches:
            contact.email = email_matches[0]
        
        # Extract phone
        phone_matches = self.patterns.phone_pattern.findall(text)
        if phone_matches:
            contact.phone = phone_matches[0]
        
        # Extract LinkedIn
        linkedin_matches = self.patterns.linkedin_pattern.findall(text)
        if linkedin_matches:
            contact.linkedin = linkedin_matches[0]
        
        # Extract GitHub
        github_matches = self.patterns.github_pattern.findall(text)
        if github_matches:
            contact.github = github_matches[0]
        
        # Extract name (heuristic: first line or text before email)
        contact.name = self._extract_name(text)
        
        return contact

    def extract_contact_info_with_layout(self, lines: List[Dict]) -> ContactInfo:
        """Extract contact information using layout data."""
        contact = ContactInfo()
        
        # Look at the top portion of the document for contact info
        top_lines = [line for line in lines if line.get('y_position', 0) < 100]  # Top 100 units
        top_text = ' '.join([line.get('text', '') for line in top_lines])
        
        # Extract standard contact info
        contact = self.extract_contact_info(top_text)
        
        # Try to get name from layout if not found
        if not contact.name:
            contact.name = self._extract_name_with_layout(top_lines)
        
        return contact

    def _extract_name(self, text: str) -> Optional[str]:
        """
        Extract name using heuristics.
        Usually the name appears at the top of the resume.
        """
        lines = text.split('\n')[:5]  # Look at first 5 lines
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and lines with email/phone/urls
            if (line and 
                not self.patterns.email_pattern.search(line) and 
                not self.patterns.phone_pattern.search(line) and
                not self.patterns.linkedin_pattern.search(line) and
                not self.patterns.github_pattern.search(line) and
                len(line.split()) <= ValidationConstants.MAX_NAME_WORDS and  # Names are usually 1-4 words
                len(line) < ValidationConstants.MAX_NAME_LENGTH):  # Names shouldn't be too long
                # Basic validation: should contain alphabetic characters
                if re.search(r'^[a-zA-Z\s]+$', line):  # Only letters and spaces
                    return line
        
        return None

    def _extract_name_with_layout(self, top_lines: List[Dict]) -> Optional[str]:
        """
        Extract name using layout information.
        Look for the largest text at the top of the document.
        """
        if not top_lines:
            return None
        
        # Find lines with larger font size (potential name)
        max_size = max([line.get('font_size', 0) for line in top_lines], default=0)
        large_text_lines = [
            line for line in top_lines 
            if line.get('font_size', 0) >= max_size * 0.8  # Within 80% of max size
        ]
        
        for line in large_text_lines:
            text = line.get('text', '').strip()
            if self._is_valid_name(text):
                return text
        
        # Fallback to regular text extraction
        top_text = '\n'.join([line.get('text', '') for line in top_lines])
        return self._extract_name(top_text)

    def _is_valid_name(self, text: str) -> bool:
        """
        Check if text appears to be a valid name.
        
        Args:
            text (str): Text to validate
            
        Returns:
            bool: True if text appears to be a name
        """
        if not text:
            return False
        
        # Skip lines with contact information
        if (self.patterns.email_pattern.search(text) or 
            self.patterns.phone_pattern.search(text) or
            self.patterns.linkedin_pattern.search(text) or
            self.patterns.github_pattern.search(text)):
            return False
        
        # Check length constraints
        words = text.split()
        if (len(words) > ValidationConstants.MAX_NAME_WORDS or 
            len(text) > ValidationConstants.MAX_NAME_LENGTH):
            return False
        
        # Should contain only letters and spaces
        if not re.search(r'^[a-zA-Z\s]+$', text):
            return False
        
        # Should not be common section headers
        common_headers = ['resume', 'cv', 'curriculum vitae', 'contact', 'profile']
        if text.lower().strip() in common_headers:
            return False
        
        return True 