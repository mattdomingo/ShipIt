#!/usr/bin/env python3
"""
Fetch and display parsed resume data from the API
Usage: python get_parsed_resume.py <task_id>
"""

import json
import sys
import time
from typing import Dict, Any, Optional
import requests
from datetime import datetime


class ResumeDataFormatter:
    """Format parsed resume data for display"""
    
    @staticmethod
    def print_section_header(title: str):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f" {title.upper()}")
        print(f"{'='*60}")
    
    @staticmethod
    def print_contact_info(contact: Dict[str, Any]):
        """Print contact information"""
        if not contact:
            print("No contact information found")
            return
            
        print(f"Name: {contact.get('name', 'N/A')}")
        print(f"Email: {contact.get('email', 'N/A')}")
        print(f"Phone: {contact.get('phone', 'N/A')}")
        
        if contact.get('linkedin'):
            print(f"LinkedIn: {contact['linkedin']}")
        if contact.get('github'):
            print(f"GitHub: {contact['github']}")
        if contact.get('website'):
            print(f"Website: {contact['website']}")
        if contact.get('address'):
            print(f"Address: {contact['address']}")
    
    @staticmethod
    def print_education(education: list):
        """Print education entries"""
        if not education:
            print("No education information found")
            return
            
        for i, edu in enumerate(education, 1):
            print(f"\n{i}. {edu.get('degree', 'N/A')} - {edu.get('field_of_study', 'N/A')}")
            print(f"   Institution: {edu.get('institution', 'N/A')}")
            
            # Format dates
            start_date = edu.get('start_date')
            end_date = edu.get('end_date')
            if start_date or end_date:
                date_str = f"   Duration: "
                if start_date:
                    date_str += start_date
                if start_date and end_date:
                    date_str += " - "
                if end_date:
                    date_str += end_date
                print(date_str)
            
            if edu.get('gpa'):
                print(f"   GPA: {edu['gpa']}")
            if edu.get('activities'):
                print(f"   Activities: {', '.join(edu['activities'])}")
    
    @staticmethod
    def print_experience(experience: list):
        """Print work experience entries"""
        if not experience:
            print("No work experience found")
            return
            
        for i, exp in enumerate(experience, 1):
            print(f"\n{i}. {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
            
            # Format dates
            start_date = exp.get('start_date')
            end_date = exp.get('end_date')
            if start_date or end_date:
                date_str = f"   Duration: "
                if start_date:
                    date_str += start_date
                if start_date and end_date:
                    date_str += " - "
                if end_date:
                    date_str += end_date
                print(date_str)
            
            if exp.get('location'):
                print(f"   Location: {exp['location']}")
            
            if exp.get('responsibilities'):
                print("   Responsibilities:")
                for resp in exp['responsibilities']:
                    print(f"   • {resp}")
    
    @staticmethod
    def print_skills(skills: Dict[str, Any]):
        """Print skills information"""
        if not skills:
            print("No skills found")
            return
            
        all_skills = []
        
        # Collect skills from different categories
        for category in ['programming_languages', 'frameworks', 'tools', 
                        'databases', 'cloud_platforms', 'soft_skills', 'other']:
            if category in skills and skills[category]:
                all_skills.extend(skills[category])
        
        if all_skills:
            print(", ".join(sorted(set(all_skills))))
        else:
            print("No specific skills listed")
    
    @staticmethod
    def print_projects(projects: list):
        """Print project entries"""
        if not projects:
            return
            
        ResumeDataFormatter.print_section_header("Projects")
        for i, proj in enumerate(projects, 1):
            print(f"\n{i}. {proj.get('name', 'N/A')}")
            if proj.get('description'):
                print(f"   {proj['description']}")
            if proj.get('technologies'):
                print(f"   Technologies: {', '.join(proj['technologies'])}")
            if proj.get('url'):
                print(f"   URL: {proj['url']}")


def get_demo_token(base_url: str) -> Optional[str]:
    """Get demo authentication token"""
    try:
        response = requests.get(f"{base_url}/v1/auth/demo-token")
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"Error getting demo token: {e}")
        return None


def check_task_status(base_url: str, task_id: str, token: str) -> Dict[str, Any]:
    """Check the status of a parsing task"""
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(
            f"{base_url}/v1/uploads/status/{task_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error checking task status: {e}")
        return {}


def format_and_print_resume(parsed_data: Dict[str, Any]):
    """Format and print the parsed resume data"""
    formatter = ResumeDataFormatter()
    
    # Print metadata
    print(f"\nParsing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Contact Information
    formatter.print_section_header("Contact Information")
    formatter.print_contact_info(parsed_data.get('contact', {}))
    
    # Education
    formatter.print_section_header("Education")
    formatter.print_education(parsed_data.get('education', []))
    
    # Experience
    formatter.print_section_header("Work Experience")
    formatter.print_experience(parsed_data.get('experience', []))
    
    # Skills
    formatter.print_section_header("Skills")
    formatter.print_skills(parsed_data.get('skills', {}))
    
    # Projects (if any)
    if parsed_data.get('projects'):
        formatter.print_projects(parsed_data['projects'])
    
    # Additional sections
    if parsed_data.get('certifications'):
        formatter.print_section_header("Certifications")
        for cert in parsed_data['certifications']:
            print(f"• {cert}")
    
    if parsed_data.get('languages'):
        formatter.print_section_header("Languages")
        for lang in parsed_data['languages']:
            print(f"• {lang}")
    
    print(f"\n{'='*60}\n")


def main():
    """Main function to fetch and display parsed resume data"""
    if len(sys.argv) < 2:
        print("Usage: python get_parsed_resume.py <task_id>")
        print("Example: python get_parsed_resume.py 7ec196a1-bb66-43dc-8f60-55b2766b8e6b")
        sys.exit(1)
    
    task_id = sys.argv[1]
    base_url = "http://localhost:8000"
    
    # Get authentication token
    print("Getting authentication token...")
    token = get_demo_token(base_url)
    if not token:
        print("Failed to get authentication token")
        sys.exit(1)
    
    print(f"Checking status for task: {task_id}")
    
    # Poll for completion
    max_attempts = 30
    for attempt in range(max_attempts):
        status_data = check_task_status(base_url, task_id, token)
        
        if not status_data:
            print("Failed to get status")
            sys.exit(1)
        
        status = status_data.get('status', 'unknown')
        print(f"Status: {status}", end='')
        
        if status == 'completed':
            print(" ✓")
            if 'result' in status_data and 'parsed_data' in status_data['result']:
                format_and_print_resume(status_data['result']['parsed_data'])
            else:
                print("\nNo parsed data found in result")
                print(f"Full response: {json.dumps(status_data, indent=2)}")
            break
        elif status == 'failed':
            print(" ✗")
            print(f"Task failed: {status_data.get('error', 'Unknown error')}")
            break
        else:
            print(f" (attempt {attempt + 1}/{max_attempts})")
            time.sleep(2)
    else:
        print(f"\nTimeout: Task did not complete within {max_attempts * 2} seconds")


if __name__ == "__main__":
    main() 