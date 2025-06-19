"""
skills.py

Skills data and categorization for resume parsing.
Contains predefined skill sets commonly found in resumes and internship requirements.
"""

from typing import Dict, List


class SkillsDatabase:
    """Database of technical and soft skills for resume extraction."""
    
    def __init__(self):
        """Initialize the skills database with predefined skill categories."""
        self._initialize_technical_skills()
        self._initialize_soft_skills()
    
    def _initialize_technical_skills(self):
        """Initialize technical skills categorized by type."""
        self.technical_skills = {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php',
                'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab',
                'sql', 'html', 'css', 'dart', 'perl', 'bash', 'powershell'
            ],
            'frameworks': [
                'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
                'spring', 'rails', 'laravel', 'asp.net', 'bootstrap', 'jquery',
                'react native', 'flutter', 'ionic', 'xamarin'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle',
                'sql server', 'cassandra', 'dynamodb', 'elasticsearch'
            ],
            'tools': [
                'git', 'docker', 'kubernetes', 'jenkins', 'travis', 'aws', 'azure',
                'gcp', 'terraform', 'ansible', 'vagrant', 'webpack', 'npm', 'yarn',
                'maven', 'gradle', 'jira', 'confluence', 'slack', 'trello'
            ],
            'office_applications': [
                'excel', 'microsoft excel', 'word', 'microsoft word', 'powerpoint',
                'microsoft powerpoint', 'outlook', 'microsoft outlook', 'access',
                'microsoft access', 'visio', 'microsoft visio', 'project',
                'microsoft project', 'sharepoint', 'onedrive', 'teams'
            ],
            'analytics_tools': [
                'tableau', 'power bi', 'qlik', 'looker', 'sas', 'spss', 'stata',
                'alteryx', 'knime', 'rapidminer', 'snowflake', 'databricks'
            ],
            'design_tools': [
                'photoshop', 'illustrator', 'indesign', 'figma', 'sketch',
                'adobe creative suite', 'canva', 'autocad', 'solidworks'
            ],
            'financial_tools': [
                'quickbooks', 'sap', 'oracle financials', 'netsuite', 'salesforce',
                'hubspot', 'marketo', 'mailchimp'
            ],
            'concepts': [
                'machine learning', 'ai', 'data science', 'web development',
                'mobile development', 'devops', 'agile', 'scrum', 'api',
                'microservices', 'cloud computing', 'cybersecurity', 'blockchain'
            ]
        }
    
    def _initialize_soft_skills(self):
        """Initialize soft skills commonly sought in internships."""
        self.soft_skills = [
            'leadership', 'teamwork', 'communication', 'problem solving',
            'analytical thinking', 'creativity', 'adaptability', 'time management',
            'project management', 'collaboration', 'critical thinking'
        ]
    
    def get_all_technical_skills(self) -> List[str]:
        """
        Get a flat list of all technical skills.
        
        Returns:
            List of all technical skills
        """
        all_skills = []
        for category, skills in self.technical_skills.items():
            all_skills.extend(skills)
        return all_skills
    
    def get_skills_by_category(self, category: str) -> List[str]:
        """
        Get skills for a specific technical category.
        
        Args:
            category: The skill category (e.g., 'programming_languages')
            
        Returns:
            List of skills in that category, empty list if category not found
        """
        return self.technical_skills.get(category, [])
    
    def get_technical_categories(self) -> List[str]:
        """
        Get all available technical skill categories.
        
        Returns:
            List of category names
        """
        return list(self.technical_skills.keys())
    
    def get_soft_skills(self) -> List[str]:
        """
        Get all soft skills.
        
        Returns:
            List of soft skills
        """
        return self.soft_skills.copy()
    
    def add_skill(self, category: str, skill: str) -> bool:
        """
        Add a new skill to a category.
        
        Args:
            category: Technical category or 'soft' for soft skills
            skill: The skill to add
            
        Returns:
            True if added successfully, False if category doesn't exist
        """
        if category == 'soft':
            if skill not in self.soft_skills:
                self.soft_skills.append(skill)
                return True
        elif category in self.technical_skills:
            if skill not in self.technical_skills[category]:
                self.technical_skills[category].append(skill)
                return True
        return False
    
    def remove_skill(self, category: str, skill: str) -> bool:
        """
        Remove a skill from a category.
        
        Args:
            category: Technical category or 'soft' for soft skills
            skill: The skill to remove
            
        Returns:
            True if removed successfully, False if not found
        """
        try:
            if category == 'soft':
                self.soft_skills.remove(skill)
                return True
            elif category in self.technical_skills:
                self.technical_skills[category].remove(skill)
                return True
        except ValueError:
            pass
        return False


# Singleton instance for easy import
skills_db = SkillsDatabase() 