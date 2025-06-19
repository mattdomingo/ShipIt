"""
extractor.py

Main orchestrator for resume data extraction.
Core functionality for the resume-powered internship finder MVP.

Coordinates specialized extractors for:
- Contact information (email, phone, name)
- Education (degree, institution, graduation year, GPA)
- Skills (technical and soft skills)
- Work experience (company, role, duration, responsibilities)
"""

from typing import Dict

from .schemas import ResumeData
from .extractors import (
    ContactExtractor,
    EducationExtractor,
    ExperienceExtractor,
    SkillsExtractor,
    SectionParser,
    LayoutParser
)


class ResumeExtractor:
    """
    Main orchestrator for extracting structured data from resume text.
    """

    def __init__(self):
        """Initialize the extractor with specialized extractors."""
        self.contact_extractor = ContactExtractor()
        self.education_extractor = EducationExtractor()
        self.experience_extractor = ExperienceExtractor()
        self.skills_extractor = SkillsExtractor()
        self.section_parser = SectionParser()
        self.layout_parser = LayoutParser()

    def extract_all(self, text: str) -> ResumeData:
        """
        Extract all structured data from resume text.
        
        Args:
            text (str): The raw resume text from PDF/DOCX parsing
            
        Returns:
            ResumeData: Structured resume data object
        """
        # Clean the text
        cleaned_text = self.section_parser.clean_text(text)
        
        # Extract each component using specialized extractors
        contact = self.contact_extractor.extract_contact_info(cleaned_text)
        education = self.education_extractor.extract_education(cleaned_text)
        experience = self.experience_extractor.extract_experience(cleaned_text)
        skills = self.skills_extractor.extract_skills(cleaned_text)
        
        # Extract additional sections
        additional_sections = self._extract_additional_sections(cleaned_text)
        
        return ResumeData(
            contact=contact,
            education=education,
            experience=experience,
            skills=skills,
            additional_sections=additional_sections,
            raw_text=text
        )

    def extract_all_with_layout(self, layout_data: Dict) -> ResumeData:
        """
        Extract all structured data using layout information.
        
        Args:
            layout_data (Dict): Layout data from PDF parsing
            
        Returns:
            ResumeData: Structured resume data object
        """
        return self.layout_parser.extract_all_with_layout(layout_data)

    def find_all_sections(self, text: str) -> Dict[str, str]:
        """
        Find all major sections in the resume.
        
        Args:
            text (str): The resume text to parse
            
        Returns:
            Dict[str, str]: Dictionary mapping section names to their content
        """
        return self.section_parser.find_all_sections(text)

    def _extract_additional_sections(self, text: str) -> Dict[str, any]:
        """
        Extract additional sections like projects, certifications, etc.
        
        Args:
            text (str): Resume text
            
        Returns:
            Dict[str, any]: Additional sections content
        """
        from .schemas import AdditionalSection
        from .constants import SectionHeaders
        
        additional_sections = {}
        
        # Define additional section types to look for
        additional_section_types = {
            'projects': SectionHeaders.PROJECTS,
            'certifications': SectionHeaders.CERTIFICATIONS,
            'awards': ['awards', 'honors', 'achievements'],
            'publications': ['publications', 'papers', 'articles'],
            'volunteer': ['volunteer', 'community service', 'volunteering'],
            'languages': ['languages', 'language skills'],
            'interests': ['interests', 'hobbies', 'activities']
        }
        
        for section_name, keywords in additional_section_types.items():
            section_content = self.section_parser.find_section(text, keywords)
            if section_content:
                additional_sections[section_name] = AdditionalSection(
                    title=section_name.title(),
                    content=section_content.strip()
                )
        
        return additional_sections


# Convenience functions for backward compatibility
def extract_resume_data(text: str) -> ResumeData:
    """
    Extract resume data from text (convenience function).
    
    Args:
        text (str): Resume text
        
    Returns:
        ResumeData: Extracted resume data
    """
    extractor = ResumeExtractor()
    return extractor.extract_all(text)


def extract_resume_data_smart(file_path: str) -> ResumeData:
    """
    Extract resume data with automatic format detection (convenience function).
    
    Args:
        file_path (str): Path to resume file
        
    Returns:
        ResumeData: Extracted resume data
    """
    from .converter import convert_to_text, extract_pdf_with_layout
    import os
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Use layout-aware extraction for PDFs
    if file_ext == '.pdf':
        try:
            layout_data = extract_pdf_with_layout(file_path)
            extractor = ResumeExtractor()
            return extractor.extract_all_with_layout(layout_data)
        except Exception as e:
            # Fallback to text-based extraction if layout parsing fails
            print(f"Layout extraction failed, falling back to text: {e}")
            text = convert_to_text(file_path)
            return extract_resume_data(text)
    else:
        # Use text-based extraction for other formats (DOCX, etc.)
        text = convert_to_text(file_path)
        return extract_resume_data(text)
