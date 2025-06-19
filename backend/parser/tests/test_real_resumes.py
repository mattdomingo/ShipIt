"""
Test file for real resume processing.
Tests the sample_resume and Phillips resume with the new refactored system.
"""

import os
import pytest
from backend.parser.extractor import extract_resume_data_smart, extract_resume_data
from backend.parser.schemas import ResumeData


class TestRealResumes:
    """Test suite for processing real resume files."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = os.path.dirname(__file__)
        self.sample_pdf = os.path.join(self.test_dir, "sample_resume.pdf")
        self.sample_docx = os.path.join(self.test_dir, "sample_resume.docx")
        self.philip_pdf = os.path.join(self.test_dir, "Philip_Holland_Resume_v4.pdf")

    @pytest.mark.skipif(not os.path.exists(os.path.join(os.path.dirname(__file__), "sample_resume.pdf")), 
                       reason="sample_resume.pdf not found")
    def test_sample_resume_pdf_processing(self):
        """Test processing of sample_resume.pdf with smart extraction."""
        print(f"\n📄 Testing Sample Resume PDF: {self.sample_pdf}")
        
        # Use smart extraction which will use layout-aware approach for PDFs
        resume_data = extract_resume_data_smart(self.sample_pdf)
        
        # Basic validation
        assert isinstance(resume_data, ResumeData)
        assert len(resume_data.raw_text) > 0
        
        # Print extracted data for verification
        print(f"📝 Raw text length: {len(resume_data.raw_text)} characters")
        print(f"👤 Contact: {resume_data.contact.name}, {resume_data.contact.email}")
        print(f"🎓 Education entries: {len(resume_data.education)}")
        print(f"💼 Experience entries: {len(resume_data.experience)}")
        print(f"🛠️ Skills found: {len(resume_data.skills)}")
        
        # Should extract some meaningful data
        assert (len(resume_data.skills) > 0 or 
                resume_data.contact.email is not None or 
                resume_data.contact.phone is not None or
                len(resume_data.education) > 0 or
                len(resume_data.experience) > 0), "No meaningful data extracted"

    @pytest.mark.skipif(not os.path.exists(os.path.join(os.path.dirname(__file__), "sample_resume.docx")), 
                       reason="sample_resume.docx not found")
    def test_sample_resume_docx_processing(self):
        """Test processing of sample_resume.docx with smart extraction."""
        print(f"\n📄 Testing Sample Resume DOCX: {self.sample_docx}")
        
        # Use smart extraction which will use text-based approach for DOCX
        resume_data = extract_resume_data_smart(self.sample_docx)
        
        # Basic validation
        assert isinstance(resume_data, ResumeData)
        assert len(resume_data.raw_text) > 0
        
        # Print extracted data for verification
        print(f"📝 Raw text length: {len(resume_data.raw_text)} characters")
        print(f"👤 Contact: {resume_data.contact.name}, {resume_data.contact.email}")
        print(f"🎓 Education entries: {len(resume_data.education)}")
        print(f"💼 Experience entries: {len(resume_data.experience)}")
        print(f"🛠️ Skills found: {len(resume_data.skills)}")
        
        # Should extract some meaningful data
        assert (len(resume_data.skills) > 0 or 
                resume_data.contact.email is not None or 
                resume_data.contact.phone is not None or
                len(resume_data.education) > 0 or
                len(resume_data.experience) > 0), "No meaningful data extracted"

    @pytest.mark.skipif(not os.path.exists(os.path.join(os.path.dirname(__file__), "Philip_Holland_Resume_v4.pdf")), 
                       reason="Philip_Holland_Resume_v4.pdf not found")
    def test_philip_holland_resume_processing(self):
        """Test processing of Philip Holland's resume with smart extraction."""
        print(f"\n📄 Testing Philip Holland Resume: {self.philip_pdf}")
        
        # Use smart extraction for layout-aware PDF processing
        resume_data = extract_resume_data_smart(self.philip_pdf)
        
        # Basic validation
        assert isinstance(resume_data, ResumeData)
        assert len(resume_data.raw_text) > 0
        
        # Print extracted data for verification
        print(f"📝 Raw text length: {len(resume_data.raw_text)} characters")
        print(f"👤 Contact: {resume_data.contact.name}, {resume_data.contact.email}")
        print(f"🎓 Education entries: {len(resume_data.education)}")
        print(f"💼 Experience entries: {len(resume_data.experience)}")
        print(f"🛠️ Skills found: {len(resume_data.skills)}")
        
        # Print skills for Philip's resume specifically
        if resume_data.skills:
            print(f"🔧 Skills: {', '.join(resume_data.skills[:10])}")  # First 10 skills
        
        # Should extract some meaningful data
        assert (len(resume_data.skills) > 0 or 
                resume_data.contact.email is not None or 
                resume_data.contact.phone is not None or
                len(resume_data.education) > 0 or
                len(resume_data.experience) > 0), "No meaningful data extracted"

    def test_comparison_between_resumes(self):
        """Compare extraction results between sample and Philip resumes."""
        results = {}
        
        # Test each resume if it exists
        test_files = [
            ("sample_pdf", self.sample_pdf),
            ("sample_docx", self.sample_docx),
            ("philip_pdf", self.philip_pdf)
        ]
        
        for name, file_path in test_files:
            if os.path.exists(file_path):
                try:
                    resume_data = extract_resume_data_smart(file_path)
                    results[name] = {
                        'contact_name': resume_data.contact.name,
                        'contact_email': resume_data.contact.email,
                        'education_count': len(resume_data.education),
                        'experience_count': len(resume_data.experience),
                        'skills_count': len(resume_data.skills),
                        'text_length': len(resume_data.raw_text)
                    }
                except Exception as e:
                    results[name] = {'error': str(e)}
        
        # Print comparison
        print(f"\n📊 RESUME PROCESSING COMPARISON:")
        print("=" * 60)
        for name, data in results.items():
            print(f"\n{name.upper()}:")
            if 'error' in data:
                print(f"   ❌ Error: {data['error']}")
            else:
                print(f"   👤 Name: {data['contact_name'] or 'Not found'}")
                print(f"   📧 Email: {data['contact_email'] or 'Not found'}")
                print(f"   🎓 Education: {data['education_count']} entries")
                print(f"   💼 Experience: {data['experience_count']} entries")
                print(f"   🛠️ Skills: {data['skills_count']} found")
                print(f"   📝 Text: {data['text_length']:,} characters")
        
        # At least one resume should process successfully
        successful_results = [r for r in results.values() if 'error' not in r]
        assert len(successful_results) > 0, "No resumes processed successfully"

    def test_individual_extractor_components(self):
        """Test individual extractor components with sample data."""
        from backend.parser.extractor import ResumeExtractor
        
        # Test with a simple text sample
        sample_text = """
        John Doe
        john.doe@email.com
        (555) 123-4567
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology, 2023
        
        SKILLS
        Python, JavaScript, React
        """
        
        extractor = ResumeExtractor()
        
        # Test contact extraction
        contact = extractor.contact_extractor.extract_contact_info(sample_text)
        assert contact.name == "John Doe"
        assert contact.email == "john.doe@email.com"
        assert contact.phone == "(555) 123-4567"
        
        # Test education extraction
        education_list = extractor.education_extractor.extract_education(sample_text)
        assert len(education_list) >= 1
        assert education_list[0].degree and "Bachelor" in education_list[0].degree
        
        # Test skills extraction
        skills = extractor.skills_extractor.extract_skills(sample_text)
        skill_names_lower = [skill.lower() for skill in skills]
        assert "python" in skill_names_lower
        assert "javascript" in skill_names_lower
        
        print(f"\n✅ Individual extractor components working correctly")
        print(f"   Contact: {contact.name}, {contact.email}, {contact.phone}")
        print(f"   Education: {len(education_list)} entries")
        print(f"   Skills: {skills}") 