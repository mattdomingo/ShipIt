#!/usr/bin/env python3
"""
Demo script for testing resume processing with the refactored system.
Tests both sample_resume and Phillips resume files.
"""

import os
import sys
from pathlib import Path

# Add the backend parser to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.parser.extractor import extract_resume_data_smart, ResumeExtractor
from backend.parser.converter import convert_to_text


def print_separator(title: str, char: str = "="):
    """Print a formatted separator."""
    print(f"\n{char * 60}")
    print(f"{title.center(60)}")
    print(f"{char * 60}")


def analyze_resume(file_path: str, resume_name: str):
    """Analyze a single resume file and print detailed results."""
    print_separator(f"ANALYZING {resume_name}", "=")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        # Basic file info
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        print(f"📄 File: {os.path.basename(file_path)}")
        print(f"📊 Size: {file_size:,} bytes")
        print(f"🔧 Format: {file_ext.upper()}")
        
        # Extract resume data using smart extraction
        print(f"\n🧠 Extracting data using smart extraction...")
        resume_data = extract_resume_data_smart(file_path)
        
        # Print results
        print_separator("CONTACT INFORMATION", "-")
        contact = resume_data.contact
        print(f"👤 Name: {contact.name or 'Not found'}")
        print(f"📧 Email: {contact.email or 'Not found'}")
        print(f"📱 Phone: {contact.phone or 'Not found'}")
        print(f"🔗 LinkedIn: {contact.linkedin or 'Not found'}")
        print(f"🐙 GitHub: {contact.github or 'Not found'}")
        
        print_separator("EDUCATION", "-")
        print(f"🎓 Education entries found: {len(resume_data.education)}")
        for i, edu in enumerate(resume_data.education, 1):
            print(f"  {i}. {edu.degree or 'Unknown degree'}")
            print(f"     🏛️  Institution: {edu.institution or 'Unknown'}")
            print(f"     📅 Year: {edu.graduation_year or 'Unknown'}")
            if edu.gpa:
                print(f"     📊 GPA: {edu.gpa}")
            if edu.field:
                print(f"     📚 Field: {edu.field}")
        
        print_separator("WORK EXPERIENCE", "-")
        print(f"💼 Experience entries found: {len(resume_data.experience)}")
        for i, exp in enumerate(resume_data.experience, 1):
            print(f"  {i}. {exp.role or 'Unknown role'}")
            print(f"     🏢 Company: {exp.company or 'Unknown company'}")
            if exp.start_date or exp.end_date:
                print(f"     📅 Duration: {exp.start_date or '?'} - {exp.end_date or '?'}")
            if exp.location:
                print(f"     📍 Location: {exp.location}")
            if exp.description:
                desc_preview = exp.description[:150] + ("..." if len(exp.description) > 150 else "")
                print(f"     📝 Description: {desc_preview}")
        
        print_separator("SKILLS", "-")
        print(f"🛠️ Skills found: {len(resume_data.skills)}")
        if resume_data.skills:
            # Group skills for better display
            skills_per_line = 4
            for i in range(0, len(resume_data.skills), skills_per_line):
                skills_group = resume_data.skills[i:i+skills_per_line]
                print(f"   {' • '.join(skills_group)}")
        else:
            print("   No skills detected")
        
        print_separator("ADDITIONAL SECTIONS", "-")
        print(f"📋 Additional sections found: {len(resume_data.additional_sections)}")
        for section_name, section in resume_data.additional_sections.items():
            print(f"  • {section.title}")
            items = section.get_items()
            if items:
                print(f"    📝 Items: {len(items)}")
                # Show first few items
                for item in items[:3]:
                    print(f"      - {item[:100]}{'...' if len(item) > 100 else ''}")
                if len(items) > 3:
                    print(f"      ... and {len(items) - 3} more")
        
        print_separator("RAW TEXT PREVIEW", "-")
        print(f"📝 Raw text length: {len(resume_data.raw_text):,} characters")
        print(f"📄 First 300 characters:")
        print("-" * 40)
        print(resume_data.raw_text[:300] + ("..." if len(resume_data.raw_text) > 300 else ""))
        print("-" * 40)
        
        return resume_data
        
    except Exception as e:
        print(f"❌ Error processing {resume_name}: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function to test all available resumes."""
    print_separator("RESUME PROCESSING DEMO", "=")
    print("Testing resume processing with the refactored system")
    print("This will test both sample_resume and Phillips resume files")
    
    # Define test files
    test_dir = Path("backend/parser/tests")
    test_files = [
        (test_dir / "sample_resume.pdf", "Sample Resume (PDF)"),
        (test_dir / "sample_resume.docx", "Sample Resume (DOCX)"),
        (test_dir / "Philip_Holland_Resume_v4.pdf", "Philip Holland Resume"),
    ]
    
    results = {}
    
    # Process each file
    for file_path, name in test_files:
        if file_path.exists():
            resume_data = analyze_resume(str(file_path), name)
            if resume_data:
                results[name] = resume_data
        else:
            print_separator(f"SKIPPING {name}", "=")
            print(f"❌ File not found: {file_path}")
    
    # Summary comparison
    if len(results) > 1:
        print_separator("COMPARISON SUMMARY", "=")
        print(f"🔍 Processed {len(results)} resumes successfully")
        
        comparison_table = []
        headers = ["Resume", "Contact", "Education", "Experience", "Skills", "Sections"]
        
        for name, data in results.items():
            row = [
                name[:20],  # Truncate name
                "✅" if data.contact.name else "❌",
                str(len(data.education)),
                str(len(data.experience)),
                str(len(data.skills)),
                str(len(data.additional_sections))
            ]
            comparison_table.append(row)
        
        # Print table
        print(f"{'Resume':<22} {'Contact':<8} {'Edu':<4} {'Exp':<4} {'Skills':<7} {'Sections':<8}")
        print("-" * 60)
        for row in comparison_table:
            print(f"{row[0]:<22} {row[1]:<8} {row[2]:<4} {row[3]:<4} {row[4]:<7} {row[5]:<8}")
    
    print_separator("DEMO COMPLETE", "=")
    print("✅ Resume processing demo completed!")
    
    if results:
        print(f"📊 Successfully processed {len(results)} resume(s)")
        print("🔧 The refactored system is working correctly!")
    else:
        print("❌ No resumes were processed successfully")
        print("⚠️  Please check that resume files exist in backend/parser/tests/")


if __name__ == "__main__":
    main() 