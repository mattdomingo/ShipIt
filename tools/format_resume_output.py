#!/usr/bin/env python3
"""
Quick format script for resume parsing output
Can be used with the task ID from upload logs
"""

import json
import sys
from typing import Dict, Any


def format_resume_output(data: Dict[str, Any]) -> str:
    """Format parsed resume data for quick display"""
    output = []
    
    # Quick summary
    output.append("=== RESUME PARSING SUMMARY ===\n")
    
    # Contact
    contact = data.get('contact', {})
    if contact:
        output.append(f"📧 Contact: {contact.get('name', 'N/A')} | {contact.get('email', 'N/A')} | {contact.get('phone', 'N/A')}")
    
    # Education count
    education = data.get('education', [])
    output.append(f"🎓 Education: {len(education)} entries")
    
    # Experience count
    experience = data.get('experience', [])
    output.append(f"💼 Experience: {len(experience)} entries")
    
    # Skills summary
    skills = data.get('skills', {})
    total_skills = 0
    for category in skills.values():
        if isinstance(category, list):
            total_skills += len(category)
    output.append(f"🛠️  Skills: {total_skills} total")
    
    # Show first few entries of each section
    output.append("\n--- Sample Data ---")
    
    # First education entry
    if education:
        edu = education[0]
        output.append(f"\nEducation: {edu.get('degree', 'N/A')} at {edu.get('institution', 'N/A')}")
    
    # First experience entry
    if experience:
        exp = experience[0]
        output.append(f"\nExperience: {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
    
    # First 5 skills
    all_skills = []
    for category, skill_list in skills.items():
        if isinstance(skill_list, list):
            all_skills.extend(skill_list)
    if all_skills:
        output.append(f"\nSkills preview: {', '.join(all_skills[:5])}")
        if len(all_skills) > 5:
            output.append(f"... and {len(all_skills) - 5} more")
    
    return '\n'.join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python format_resume_output.py '<json_data>'")
        print("Or pipe data: echo '<json_data>' | python format_resume_output.py")
        sys.exit(1)
    
    try:
        # Try to read from argument or stdin
        if sys.argv[1] == '-':
            json_str = sys.stdin.read()
        else:
            json_str = sys.argv[1]
        
        # Parse JSON
        data = json.loads(json_str)
        
        # Format and print
        print(format_resume_output(data))
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON data - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 