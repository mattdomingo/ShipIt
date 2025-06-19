#!/usr/bin/env python3
"""
Demo script for resume data extraction.
Shows both traditional text-only and enhanced layout-aware extraction.
"""

import os
import sys
from pathlib import Path

# Add the backend parser to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.parser.converter import convert_to_text, extract_pdf_with_layout
from backend.parser.extractor import extract_resume_data, extract_resume_data_smart, ResumeExtractor


def demo_traditional_extraction(file_path: str):
    """Demo the traditional text-only extraction approach."""
    print("=" * 60)
    print("TRADITIONAL TEXT-ONLY EXTRACTION")
    print("=" * 60)
    
    # Use smart extraction (will automatically choose best method)
    resume_data = extract_resume_data_smart(file_path)
    
    print(f"Extracted text length: {len(resume_data.raw_text)} characters")
    print("\nFirst 200 characters:")
    text = resume_data.raw_text
    print(text[:200] + "..." if len(text) > 200 else text)
    
    print("\n" + "-" * 40)
    print("EXTRACTED DATA:")
    print("-" * 40)
    
    print(f"Name: {resume_data.contact.name}")
    print(f"Email: {resume_data.contact.email}")
    print(f"Phone: {resume_data.contact.phone}")
    print(f"LinkedIn: {resume_data.contact.linkedin}")
    print(f"GitHub: {resume_data.contact.github}")
    
    print(f"\nEducation entries: {len(resume_data.education)}")
    for edu in resume_data.education:
        print(f"  - {edu.degree} from {edu.institution} ({edu.graduation_year})")
        if edu.gpa:
            print(f"    GPA: {edu.gpa}")
    
    print(f"\nWork experience entries: {len(resume_data.experience)}")
    for exp in resume_data.experience:
        print(f"  - {exp.role} at {exp.company}")
        if exp.start_date or exp.end_date:
            print(f"    Duration: {exp.start_date} - {exp.end_date}")
    
    print(f"\nSkills found: {len(resume_data.skills)}")
    print(f"  {', '.join(resume_data.skills[:10])}" + ("..." if len(resume_data.skills) > 10 else ""))
    
    print(f"\nAdditional sections: {len(resume_data.additional_sections)}")
    for section_name in resume_data.additional_sections.keys():
        print(f"  - {section_name}")


def demo_layout_aware_extraction(file_path: str):
    """Demo the enhanced layout-aware extraction approach."""
    print("\n" + "=" * 60)
    print("ENHANCED LAYOUT-AWARE EXTRACTION")
    print("=" * 60)
    
    # Check if file is PDF (layout extraction only works for PDFs currently)
    if not file_path.lower().endswith('.pdf'):
        print("Layout-aware extraction only works with PDF files.")
        return
    
    try:
        # Extract with layout data
        layout_data = extract_pdf_with_layout(file_path)
        
        print(f"Extracted text length: {len(layout_data['text'])} characters")
        print(f"Detected lines: {len(layout_data['lines'])}")
        print(f"Detected sections: {len(layout_data['sections'])}")
        
        print("\nDetected sections with layout analysis:")
        for i, section in enumerate(layout_data['sections']):
            print(f"  {i+1}. {section['title']} (lines: {len(section['lines'])})")
        
        # Extract structured data using layout-aware method
        extractor = ResumeExtractor()
        resume_data = extractor.extract_all_with_layout(layout_data)
        
        print("\n" + "-" * 40)
        print("EXTRACTED DATA (LAYOUT-AWARE):")
        print("-" * 40)
        
        print(f"Name: {resume_data.contact.name}")
        print(f"Email: {resume_data.contact.email}")
        print(f"Phone: {resume_data.contact.phone}")
        print(f"LinkedIn: {resume_data.contact.linkedin}")
        print(f"GitHub: {resume_data.contact.github}")
        
        print(f"\nEducation entries: {len(resume_data.education)}")
        for edu in resume_data.education:
            print(f"  - {edu.degree} from {edu.institution} ({edu.graduation_year})")
            if edu.gpa:
                print(f"    GPA: {edu.gpa}")
        
        print(f"\nWork experience entries: {len(resume_data.experience)}")
        for exp in resume_data.experience:
            print(f"  - {exp.role} at {exp.company}")
            if exp.start_date or exp.end_date:
                print(f"    Duration: {exp.start_date} - {exp.end_date}")
        
        print(f"\nSkills found: {len(resume_data.skills)}")
        print(f"  {', '.join(resume_data.skills[:10])}" + ("..." if len(resume_data.skills) > 10 else ""))
        
        print(f"\nAdditional sections: {len(resume_data.additional_sections)}")
        for section_name in resume_data.additional_sections.keys():
            print(f"  - {section_name}")
            
        # Show layout analysis details
        print("\n" + "-" * 40)
        print("LAYOUT ANALYSIS DETAILS:")
        print("-" * 40)
        
        # Show font size analysis
        font_sizes = [line['font_size'] for line in layout_data['lines'] if line.get('font_size')]
        if font_sizes:
            avg_font = sum(font_sizes) / len(font_sizes)
            max_font = max(font_sizes)
            min_font = min(font_sizes)
            print(f"Font sizes - Avg: {avg_font:.1f}pt, Range: {min_font:.1f}-{max_font:.1f}pt")
        
        # Show potential headers detected
        potential_headers = [line for line in layout_data['lines'] if line.get('is_potential_header')]
        print(f"Potential headers detected: {len(potential_headers)}")
        for header in potential_headers[:5]:  # Show first 5
            print(f"  - '{header['text']}' (font: {header['font_size']:.1f}pt)")
            
    except Exception as e:
        print(f"Error in layout-aware extraction: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main demo function."""
    # Look for sample resume files
    sample_files = [
        "backend/parser/tests/sample_resume.pdf",
        "backend/parser/tests/sample_resume.docx"
    ]
    
    # Find the first available sample file
    sample_file = None
    for file_path in sample_files:
        if os.path.exists(file_path):
            sample_file = file_path
            break
    
    if not sample_file:
        print("No sample resume files found. Please ensure sample files exist in:")
        for file_path in sample_files:
            print(f"  - {file_path}")
        return
    
    print(f"Using sample file: {sample_file}")
    
    # Demo both approaches
    demo_traditional_extraction(sample_file)
    demo_layout_aware_extraction(sample_file)
    
    print("\n" + "=" * 60)
    print("🎯 SMART EXTRACTION DEMO")
    print("=" * 60)
    print("The new extract_resume_data_smart() function automatically chooses")
    print("the best extraction method based on file type:")
    print(f"  - PDF files: Uses layout-aware extraction")
    print(f"  - DOCX files: Uses traditional extraction")
    print(f"  - Automatic fallback if layout extraction fails")
    
    print("\nSimple usage:")
    print("  from backend.parser.extractor import extract_resume_data_smart")
    print("  resume_data = extract_resume_data_smart('resume.pdf')")
    
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    print("Traditional approach:")
    print("  + Works with any text format (PDF, DOCX)")
    print("  + Simple and fast")
    print("  - Relies on text patterns and keywords")
    print("  - Can miss sections with non-standard formatting")
    print("  - May incorrectly identify headers/sections")
    
    print("\nLayout-aware approach:")
    print("  + Uses visual formatting cues (font size, bold, positioning)")
    print("  + More accurate section detection")
    print("  + Better handling of complex layouts")
    print("  + Can identify names by font size")
    print("  - Currently PDF-only")
    print("  - Slightly more complex")
    
    print("\n✨ Smart approach (RECOMMENDED):")
    print("  + Automatically chooses the best method")
    print("  + Layout-aware for PDFs, traditional for DOCX")
    print("  + Robust fallback handling")
    print("  + Simple API - just pass the file path")


if __name__ == "__main__":
    main() 