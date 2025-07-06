#!/usr/bin/env python3
"""
Real Resume Testing Script

Test the resume parser functionality with your own resume files.
Provides detailed analysis and debugging information.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional

# Add the backend parser to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.parser.extractor import extract_resume_data_smart, extract_resume_data, ResumeExtractor
from backend.parser.converter import convert_to_text, extract_pdf_with_layout


def print_separator(title: str, char: str = "="):
    """Print a formatted separator."""
    print(f"\n{char * 60}")
    print(f"{title}")
    print(f"{char * 60}")


def test_file_basic_info(file_path: str):
    """Test basic file information and text extraction."""
    print_separator("📄 FILE INFORMATION")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    file_size = os.path.getsize(file_path)
    file_ext = os.path.splitext(file_path)[1].lower()
    
    print(f"File: {file_path}")
    print(f"Size: {file_size:,} bytes")
    print(f"Extension: {file_ext}")
    print(f"Supported: {'✅' if file_ext in ['.pdf', '.docx'] else '❌'}")
    
    return file_ext in ['.pdf', '.docx']


def test_text_extraction(file_path: str):
    """Test basic text extraction."""
    print_separator("📝 TEXT EXTRACTION TEST")
    
    try:
        text = convert_to_text(file_path)
        if text:
            print(f"✅ Text extraction successful")
            print(f"   Length: {len(text):,} characters")
            print(f"   Lines: {len(text.splitlines())}")
            
            # Show preview
            print(f"\n📖 First 300 characters:")
            print("-" * 40)
            print(text[:300] + ("..." if len(text) > 300 else ""))
            print("-" * 40)
            
            return text
        else:
            print(f"❌ Text extraction failed - no text returned")
            return None
    except Exception as e:
        print(f"❌ Text extraction failed: {e}")
        return None


def test_smart_extraction(file_path: str):
    """Test the smart extraction function."""
    print_separator("🧠 SMART EXTRACTION TEST")
    
    try:
        resume_data = extract_resume_data_smart(file_path)
        print(f"✅ Smart extraction successful")
        
        # Contact Information
        print(f"\n👤 CONTACT INFORMATION:")
        contact = resume_data.contact
        print(f"   Name: {contact.name or 'Not found'}")
        print(f"   Email: {contact.email or 'Not found'}")
        print(f"   Phone: {contact.phone or 'Not found'}")
        print(f"   LinkedIn: {contact.linkedin or 'Not found'}")
        print(f"   GitHub: {contact.github or 'Not found'}")
        
        # Education
        print(f"\n🎓 EDUCATION ({len(resume_data.education)} entries):")
        for i, edu in enumerate(resume_data.education, 1):
            print(f"   {i}. {edu.degree or 'Unknown degree'}")
            print(f"      Institution: {edu.institution or 'Unknown'}")
            print(f"      Year: {edu.graduation_year or 'Unknown'}")
            if edu.gpa:
                print(f"      GPA: {edu.gpa}")
        
        # Experience
        print(f"\n💼 WORK EXPERIENCE ({len(resume_data.experience)} entries):")
        for i, exp in enumerate(resume_data.experience, 1):
            print(f"   {i}. {exp.role or 'Unknown role'}")
            print(f"      Company: {exp.company or 'Unknown company'}")
            if exp.start_date or exp.end_date:
                print(f"      Duration: {exp.start_date or '?'} - {exp.end_date or '?'}")
            if exp.description:
                print(f"      Description: {exp.description[:100]}...")
        
        # Skills
        print(f"\n🛠️ SKILLS ({len(resume_data.skills)} found):")
        if resume_data.skills:
            # Group skills for better display
            for i in range(0, len(resume_data.skills), 5):
                skills_group = resume_data.skills[i:i+5]
                print(f"   {' • '.join(skills_group)}")
        else:
            print("   No skills detected")
        
        # Additional Sections
        print(f"\n📋 ADDITIONAL SECTIONS ({len(resume_data.additional_sections)}):")
        for section_name, section in resume_data.additional_sections.items():
            print(f"   • {section.title}")
        
        return resume_data
        
    except Exception as e:
        print(f"❌ Smart extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_layout_analysis(file_path: str):
    """Test layout analysis for PDF files."""
    if not file_path.lower().endswith('.pdf'):
        print_separator("⚠️ LAYOUT ANALYSIS SKIPPED", "-")
        print("Layout analysis only works with PDF files.")
        return
    
    print_separator("🔍 LAYOUT ANALYSIS TEST")
    
    try:
        layout_data = extract_pdf_with_layout(file_path)
        
        print(f"✅ Layout analysis successful")
        print(f"   Total lines detected: {len(layout_data['lines'])}")
        print(f"   Sections detected: {len(layout_data['sections'])}")
        
        # Font analysis
        font_sizes = [line.get('font_size', 12) for line in layout_data['lines']]
        if font_sizes:
            print(f"   Font size range: {min(font_sizes):.1f} - {max(font_sizes):.1f}pt")
            print(f"   Average font size: {sum(font_sizes)/len(font_sizes):.1f}pt")
        
        # Show detected sections
        print(f"\n📑 DETECTED SECTIONS:")
        for i, section in enumerate(layout_data['sections'], 1):
            line_count = len(section.get('lines', []))
            print(f"   {i}. {section['title']} ({line_count} lines)")
        
        # Show potential headers
        headers = [line for line in layout_data['lines'] if line.get('is_potential_header')]
        print(f"\n🏷️ POTENTIAL HEADERS ({len(headers)}):")
        for header in headers[:10]:  # Show first 10
            font_info = f"({header.get('font_size', 12):.1f}pt"
            if header.get('is_bold'): font_info += ", bold"
            if header.get('is_all_caps'): font_info += ", caps"
            font_info += ")"
            print(f"   • '{header['text']}' {font_info}")
        
        return layout_data
        
    except Exception as e:
        print(f"❌ Layout analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main testing function."""
    print("🧪 REAL RESUME PARSER TESTING TOOL")
    print("=" * 60)
    
    # Get file path from user
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        print("Usage: python test_real_resume.py <path_to_resume_file>")
        print("\nExample:")
        print("  python test_real_resume.py ~/Documents/my_resume.pdf")
        print("  python test_real_resume.py '/path/to/resume.docx'")
        
        # Allow interactive input
        file_path = input("\nOr enter the path to your resume file: ").strip()
        if not file_path:
            print("No file path provided. Exiting.")
            return
    
    # Remove quotes if present
    file_path = file_path.strip('\'"')
    
    # Test sequence
    print(f"\n🎯 Testing resume: {file_path}")
    
    # 1. Basic file info
    if not test_file_basic_info(file_path):
        return
    
    # 2. Text extraction
    text = test_text_extraction(file_path)
    if not text:
        return
    
    # 3. Smart extraction
    resume_data = test_smart_extraction(file_path)
    if not resume_data:
        return
    
    # 4. Layout analysis (PDF only)
    layout_data = test_layout_analysis(file_path)
    
    print_separator("🎉 TESTING COMPLETE")
    print("If results aren't as expected, consider:")
    print("  • Trying a different file format (PDF vs DOCX)")
    print("  • Checking that section headers are clear")
    print("  • Ensuring contact info is at the top")
    print("  • Using standard resume formatting")


if __name__ == "__main__":
    main()