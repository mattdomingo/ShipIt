"""
schemas.py

Data structures for resume parsing and extraction.
Contains all dataclass definitions for structured resume data.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any


@dataclass
class ContactInfo:
    """Structure for storing contact information."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Education:
    """Structure for storing education information."""
    degree: Optional[str] = None
    field: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class WorkExperience:
    """Structure for storing work experience."""
    company: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    skills_used: List[str] = None

    def __post_init__(self):
        if self.skills_used is None:
            self.skills_used = []

    def to_dict(self):
        return asdict(self)


@dataclass
class AdditionalSection:
    """Structure for storing non-standard resume sections like interests, certifications, etc."""
    title: str
    content: str
    
    def get_items(self) -> List[str]:
        """Parse the content into individual items."""
        # Simple parsing - split by lines and clean up
        items = []
        for line in self.content.split('\n'):
            line = line.strip()
            if line and line != self.title:
                # Split by commas if present, otherwise use the whole line
                if ',' in line:
                    items.extend([item.strip() for item in line.split(',') if item.strip()])
                else:
                    items.append(line)
        return items

    def to_dict(self):
        return asdict(self)


@dataclass
class ResumeData:
    """Main structure containing all extracted resume data."""
    contact: ContactInfo
    education: List[Education]
    experience: List[WorkExperience]
    skills: List[str]
    additional_sections: Dict[str, AdditionalSection]
    raw_text: str

    def __post_init__(self):
        if self.education is None:
            self.education = []
        if self.experience is None:
            self.experience = []
        if self.skills is None:
            self.skills = []
        if self.additional_sections is None:
            self.additional_sections = {}
    
    def get_section(self, section_name: str) -> Optional[AdditionalSection]:
        """Get an additional section by name (case-insensitive)."""
        for key, section in self.additional_sections.items():
            if key.lower() == section_name.lower():
                return section
        return None
    
    def has_section(self, section_name: str) -> bool:
        """Check if a section exists (case-insensitive)."""
        return self.get_section(section_name) is not None

    def to_dict(self):
        return {
            "contact": self.contact.to_dict(),
            "education": [edu.to_dict() for edu in self.education],
            "experience": [exp.to_dict() for exp in self.experience],
            "skills": self.skills,
            "additional_sections": {
                name: section.to_dict() for name, section in self.additional_sections.items()
            }
        } 