"""
skills_extractor.py

Extracts technical and soft skills from resume text.
"""

import re
from typing import List, Dict

from ..skills import skills_db
from ..constants import SectionHeaders


class SkillsExtractor:
    """
    Extracts skills from resume text.
    """

    def __init__(self):
        """Initialize the skills extractor with skills database."""
        self.skills_db = skills_db

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text."""
        from .section_parser import SectionParser
        
        section_parser = SectionParser()
        skills_section = section_parser.find_section(text, SectionHeaders.SKILLS)
        
        if skills_section:
            # Extract from dedicated skills section
            skills = self._extract_skills_from_text(skills_section)
        else:
            # Extract from entire resume text
            skills = self._extract_skills_from_text(text)
        
        return list(set(skills))  # Remove duplicates

    def extract_skills_with_layout(self, sections: List[Dict], full_text: str) -> List[str]:
        """Extract skills using layout data."""
        skills = []
        
        # Find skills section in layout data
        skills_sections = []
        for section in sections:
            header = section.get('header', '').lower()
            if any(keyword in header for keyword in ['skill', 'competenc', 'technical', 'technolog']):
                skills_sections.append(section)
        
        if skills_sections:
            # Extract from dedicated skills sections
            for section in skills_sections:
                content_lines = section.get('content', [])
                section_text = '\n'.join([line.get('text', '') for line in content_lines])
                section_skills = self._extract_skills_from_text(section_text)
                skills.extend(section_skills)
        else:
            # Fallback to full text extraction
            skills = self._extract_skills_from_text(full_text)
        
        return list(set(skills))  # Remove duplicates

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extract skills from text using the skills database.
        
        Args:
            text (str): Text to extract skills from
            
        Returns:
            List[str]: List of found skills
        """
        found_skills = []
        text_lower = text.lower()
        
        # Check all technical skills in the database
        for category in self.skills_db.get_technical_categories():
            for skill in self.skills_db.get_skills_by_category(category):
                if self._skill_found_in_text(skill, text_lower):
                    found_skills.append(skill)
        
        # Check soft skills
        for skill in self.skills_db.get_soft_skills():
            if self._skill_found_in_text(skill, text_lower):
                found_skills.append(skill)
        
        return found_skills

    def _skill_found_in_text(self, skill: str, text: str) -> bool:
        """
        Check if a skill is found in the text using word boundaries.
        
        Args:
            skill (str): Skill to search for
            text (str): Text to search in (should be lowercase)
            
        Returns:
            bool: True if skill is found
        """
        skill_lower = skill.lower()
        
        # Use word boundaries for exact matches
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        return bool(re.search(pattern, text))

    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize found skills by type.
        
        Args:
            skills (List[str]): List of skills to categorize
            
        Returns:
            Dict[str, List[str]]: Skills organized by category
        """
        categorized = {}
        
        for skill in skills:
            # Find which category this skill belongs to
            found_category = None
            
            # Check technical categories
            for category in self.skills_db.get_technical_categories():
                if skill in self.skills_db.get_skills_by_category(category):
                    found_category = category
                    break
            
            # Check soft skills
            if not found_category and skill in self.skills_db.get_soft_skills():
                found_category = 'soft_skills'
            
            if found_category:
                if found_category not in categorized:
                    categorized[found_category] = []
                categorized[found_category].append(skill)
        
        return categorized

    def get_top_skills(self, skills: List[str], limit: int = 10) -> List[str]:
        """
        Get the top skills based on frequency or importance.
        
        Args:
            skills (List[str]): List of skills
            limit (int): Maximum number of skills to return
            
        Returns:
            List[str]: Top skills
        """
        # For now, just return the first 'limit' skills
        # Could be enhanced with frequency analysis or skill importance ranking
        return skills[:limit]

    def extract_skill_levels(self, text: str, skills: List[str]) -> Dict[str, str]:
        """
        Extract skill levels (beginner, intermediate, advanced, expert) for found skills.
        
        Args:
            text (str): Resume text
            skills (List[str]): List of skills to find levels for
            
        Returns:
            Dict[str, str]: Mapping of skills to their levels
        """
        skill_levels = {}
        text_lower = text.lower()
        
        level_keywords = {
            'expert': ['expert', 'expertise', 'mastery', 'advanced'],
            'advanced': ['advanced', 'proficient', 'experienced'],
            'intermediate': ['intermediate', 'familiar', 'working knowledge'],
            'beginner': ['beginner', 'basic', 'introduction', 'learning']
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            # Look for the skill and nearby level indicators
            skill_pattern = r'\b' + re.escape(skill_lower) + r'\b'
            matches = list(re.finditer(skill_pattern, text_lower))
            
            for match in matches:
                # Look in a window around the skill mention
                start = max(0, match.start() - 50)
                end = min(len(text_lower), match.end() + 50)
                context = text_lower[start:end]
                
                # Check for level keywords in context
                for level, keywords in level_keywords.items():
                    if any(keyword in context for keyword in keywords):
                        skill_levels[skill] = level
                        break
                
                if skill in skill_levels:
                    break
        
        return skill_levels 