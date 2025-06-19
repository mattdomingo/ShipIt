"""
layout_parser.py

Handles layout-aware parsing utilities for resume data extraction.
Provides methods for working with structured layout data from PDF parsing.
"""

from typing import Dict, List, Optional

from ..schemas import ResumeData, AdditionalSection


class LayoutParser:
    """
    Handles layout-aware parsing utilities.
    """

    def __init__(self):
        """Initialize the layout parser."""
        pass

    def extract_all_with_layout(self, layout_data: Dict) -> ResumeData:
        """
        Extract all resume data using layout information.
        
        Args:
            layout_data (Dict): Layout data from PDF parsing
            
        Returns:
            ResumeData: Structured resume data
        """
        from .contact_extractor import ContactExtractor
        from .education_extractor import EducationExtractor
        from .experience_extractor import ExperienceExtractor
        from .skills_extractor import SkillsExtractor
        
        # Extract lines and convert to text for fallback
        lines = layout_data.get('lines', [])
        full_text = '\n'.join([line.get('text', '') for line in lines])
        
        # Find sections
        sections = self._identify_sections_from_layout(lines)
        
        # Initialize extractors
        contact_extractor = ContactExtractor()
        education_extractor = EducationExtractor()
        experience_extractor = ExperienceExtractor()
        skills_extractor = SkillsExtractor()
        
        # Extract data
        contact = contact_extractor.extract_contact_info_with_layout(lines)
        education = education_extractor.extract_education_with_layout(sections, full_text)
        experience = experience_extractor.extract_experience_with_layout(sections, full_text)
        skills = skills_extractor.extract_skills_with_layout(sections, full_text)
        additional_sections = self._extract_additional_sections_with_layout(sections)
        
        return ResumeData(
            contact=contact,
            education=education,
            experience=experience,
            skills=skills,
            additional_sections=additional_sections,
            raw_text=full_text
        )

    def _identify_sections_from_layout(self, lines: List[Dict]) -> List[Dict]:
        """
        Identify sections from layout data.
        
        Args:
            lines (List[Dict]): Lines with layout information
            
        Returns:
            List[Dict]: Identified sections with headers and content
        """
        sections = []
        current_section = None
        
        for i, line in enumerate(lines):
            text = line.get('text', '').strip()
            if not text:
                continue
            
            # Check if this line is a section header
            if self._is_section_header_layout(line, lines):
                # Save previous section if exists
                if current_section:
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'header': text,
                    'start_line': i,
                    'content': []
                }
            elif current_section:
                # Add to current section content
                current_section['content'].append(line)
        
        # Add the last section
        if current_section:
            sections.append(current_section)
        
        return sections

    def _is_section_header_layout(self, line: Dict, all_lines: List[Dict]) -> bool:
        """
        Check if a line is a section header using layout information.
        
        Args:
            line (Dict): Line to check
            all_lines (List[Dict]): All lines for context
            
        Returns:
            bool: True if likely a section header
        """
        text = line.get('text', '').strip().lower()
        
        # Common section headers
        section_keywords = [
            'education', 'experience', 'work experience', 'employment',
            'skills', 'technical skills', 'core competencies',
            'projects', 'personal projects', 'key projects',
            'certifications', 'certificates', 'awards',
            'summary', 'objective', 'profile',
            'activities', 'volunteer', 'leadership'
        ]
        
        # Check if text matches section keywords
        text_match = any(keyword in text for keyword in section_keywords)
        if not text_match:
            return False
        
        # Use layout cues to confirm
        is_bold = line.get('bold', False) or line.get('font_weight', 0) > 400
        is_larger = line.get('font_size', 0) > self._get_average_font_size(all_lines)
        is_short = len(text.split()) <= 4
        
        # Section headers are usually bold, larger, or short
        return text_match and (is_bold or is_larger or is_short)

    def _get_average_font_size(self, lines: List[Dict]) -> float:
        """Get average font size from lines."""
        font_sizes = [line.get('font_size', 12) for line in lines if line.get('font_size')]
        return sum(font_sizes) / len(font_sizes) if font_sizes else 12

    def _extract_additional_sections_with_layout(self, sections: List[Dict]) -> Dict[str, AdditionalSection]:
        """
        Extract additional sections using layout data.
        
        Args:
            sections (List[Dict]): Identified sections
            
        Returns:
            Dict[str, AdditionalSection]: Additional sections
        """
        additional_sections = {}
        
        # Define which sections to treat as additional
        main_sections = ['education', 'experience', 'work experience', 'skills', 'employment']
        
        for section in sections:
            header = section.get('header', '').lower()
            
            # Skip main sections
            if any(main_keyword in header for main_keyword in main_sections):
                continue
            
            # Process as additional section
            content_lines = section.get('content', [])
            content_text = '\n'.join([line.get('text', '') for line in content_lines])
            
            # Create additional section
            if content_text.strip():
                section_name = section.get('header', 'Additional')
                additional_sections[section_name] = AdditionalSection(
                    title=section_name,
                    content=content_text.strip()
                )
        
        return additional_sections

    def group_lines_by_proximity(self, lines: List[Dict], threshold: float = 20.0) -> List[List[Dict]]:
        """
        Group lines by their vertical proximity.
        
        Args:
            lines (List[Dict]): Lines with position information
            threshold (float): Maximum distance to consider lines as grouped
            
        Returns:
            List[List[Dict]]: Groups of lines
        """
        if not lines:
            return []
        
        # Sort lines by y position
        sorted_lines = sorted(lines, key=lambda x: x.get('y_position', 0))
        
        groups = []
        current_group = [sorted_lines[0]]
        
        for i in range(1, len(sorted_lines)):
            current_line = sorted_lines[i]
            previous_line = sorted_lines[i-1]
            
            # Calculate distance
            current_y = current_line.get('y_position', 0)
            previous_y = previous_line.get('y_position', 0)
            distance = abs(current_y - previous_y)
            
            if distance <= threshold:
                # Add to current group
                current_group.append(current_line)
            else:
                # Start new group
                groups.append(current_group)
                current_group = [current_line]
        
        # Add the last group
        if current_group:
            groups.append(current_group)
        
        return groups

    def extract_text_styles(self, lines: List[Dict]) -> Dict[str, any]:
        """
        Extract style information from lines.
        
        Args:
            lines (List[Dict]): Lines with style information
            
        Returns:
            Dict[str, any]: Style statistics
        """
        font_sizes = []
        font_weights = []
        bold_count = 0
        
        for line in lines:
            if 'font_size' in line:
                font_sizes.append(line['font_size'])
            if 'font_weight' in line:
                font_weights.append(line['font_weight'])
            if line.get('bold', False):
                bold_count += 1
        
        return {
            'average_font_size': sum(font_sizes) / len(font_sizes) if font_sizes else 12,
            'max_font_size': max(font_sizes) if font_sizes else 12,
            'min_font_size': min(font_sizes) if font_sizes else 12,
            'average_font_weight': sum(font_weights) / len(font_weights) if font_weights else 400,
            'bold_line_count': bold_count,
            'total_lines': len(lines)
        } 