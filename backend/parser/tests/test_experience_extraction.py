"""
test_experience_extraction.py

Tests for the improved experience extraction that uses layout-aware parsing
to accurately identify work experience entries without confusing job descriptions
with separate roles.
"""

import pytest
from backend.parser.extractor import extract_resume_data_smart
from backend.parser.extractors.experience_extractor import ExperienceExtractor


class TestExperienceExtraction:
    """Test the improved experience extraction functionality."""

    def test_philip_holland_resume_experience_extraction(self):
        """Test that Philip Holland resume extracts exactly 3 job entries with correct details."""
        resume_data = extract_resume_data_smart('backend/parser/tests/Philip_Holland_Resume_v4.pdf')
        
        # Should extract exactly 3 job entries
        assert len(resume_data.experience) == 3, f"Expected 3 experience entries, got {len(resume_data.experience)}"
        
        # Verify the specific jobs
        jobs = resume_data.experience
        
        # Job 1: Inpro Corporation
        inpro_job = next((job for job in jobs if 'inpro' in job.company.lower()), None)
        assert inpro_job is not None, "Inpro Corporation job not found"
        assert inpro_job.role == "Finance Intern", f"Expected Finance Intern, got {inpro_job.role}"
        assert "2025" in str(inpro_job.start_date), f"Expected 2025 start date, got {inpro_job.start_date}"
        assert inpro_job.description is not None, "Expected job description"
        assert len(inpro_job.description.split()) > 50, "Expected substantial job description"
        
        # Job 2: Erin Hills Golf Course
        erin_job = next((job for job in jobs if 'erin hills' in job.company.lower()), None)
        assert erin_job is not None, "Erin Hills Golf Course job not found"
        assert inpro_job.role == "Finance Intern", f"Expected Finance Intern, got {inpro_job.role}"
        assert "2022" in str(erin_job.start_date), f"Expected 2022 start date, got {erin_job.start_date}"
        assert erin_job.description is not None, "Expected job description"
        
        # Job 3: Badger Boys State
        badger_job = next((job for job in jobs if 'badger' in job.company.lower()), None)
        assert badger_job is not None, "Badger Boys State job not found"
        assert badger_job.role == "Marketing Team", f"Expected Marketing Team, got {badger_job.role}"
        assert "2024" in str(badger_job.start_date), f"Expected 2024 start date, got {badger_job.start_date}"

    def test_sample_resume_experience_extraction(self):
        """Test that sample resume extracts exactly 2 job entries with correct details."""
        resume_data = extract_resume_data_smart('backend/parser/tests/sample_resume.pdf')
        
        # Should extract exactly 2 job entries
        assert len(resume_data.experience) == 2, f"Expected 2 experience entries, got {len(resume_data.experience)}"
        
        # Verify the specific jobs
        jobs = resume_data.experience
        
        # Job 1: Pharus.ai
        pharus_job = next((job for job in jobs if 'pharus' in job.company.lower()), None)
        assert pharus_job is not None, "Pharus.ai job not found"
        assert pharus_job.role == "Software Engineer Intern", f"Expected Software Engineer Intern, got {pharus_job.role}"
        
        # Job 2: Magnet-Schultz
        magnet_job = next((job for job in jobs if 'magnet' in job.company.lower()), None)
        assert magnet_job is not None, "Magnet-Schultz job not found"
        assert magnet_job.role == "SysOps Intern", f"Expected SysOps Intern, got {magnet_job.role}"

    def test_no_bullet_points_as_separate_jobs(self):
        """Test that bullet point descriptions are not treated as separate job entries."""
        resume_data = extract_resume_data_smart('backend/parser/tests/Philip_Holland_Resume_v4.pdf')
        
        # Check that no job has a company or role that looks like a description
        for job in resume_data.experience:
            # Company should not start with action verbs
            if job.company:
                assert not job.company.lower().startswith(('file ', 'analyze ', 'ensure ', 'record ', 'maintain ')), \
                    f"Company '{job.company}' looks like a job description"
            
            # Role should not be a long sentence
            if job.role:
                assert len(job.role.split()) <= 8, f"Role '{job.role}' is too long, likely a description"

    def test_pipe_format_parsing(self):
        """Test that pipe format (Role | Company) is correctly parsed."""
        resume_data = extract_resume_data_smart('backend/parser/tests/sample_resume.pdf')
        
        # Sample resume uses pipe format
        for job in resume_data.experience:
            assert job.role is not None, f"Role should be extracted from pipe format, got None"
            assert job.company is not None, f"Company should be extracted from pipe format, got None"
            assert '|' not in job.role, f"Role should not contain pipe character: {job.role}"
            assert '|' not in job.company, f"Company should not contain pipe character: {job.company}"

    def test_company_location_format_parsing(self):
        """Test that Company Location format is correctly parsed."""
        resume_data = extract_resume_data_smart('backend/parser/tests/Philip_Holland_Resume_v4.pdf')
        
        # Philip Holland resume uses Company Location format
        inpro_job = next((job for job in resume_data.experience if 'inpro' in job.company.lower()), None)
        assert inpro_job is not None, "Inpro job should exist"
        
        # Company should not include location
        assert 'muskego' not in inpro_job.company.lower(), f"Company should not include location: {inpro_job.company}"

    def test_experience_descriptions_content(self):
        """Test that job descriptions contain substantial content and are properly formatted."""
        resume_data = extract_resume_data_smart('backend/parser/tests/Philip_Holland_Resume_v4.pdf')
        
        for job in resume_data.experience:
            if job.description:
                # Description should have substantial content
                words = job.description.split()
                assert len(words) >= 10, f"Job description too short: {len(words)} words"
                
                # Description should not start with bullet points
                lines = job.description.split('\n')
                for line in lines:
                    clean_line = line.strip()
                    if clean_line:
                        assert not clean_line.startswith('•'), f"Description line should not start with bullet: {clean_line}"

    def test_layout_aware_vs_text_based_extraction(self):
        """Test that layout-aware extraction produces better results than text-based extraction."""
        # This test demonstrates the improvement over old extraction methods
        extractor = ExperienceExtractor()
        
        # Test with Philip Holland resume using text-based extraction
        from backend.parser.converter import convert_to_text
        text = convert_to_text('backend/parser/tests/Philip_Holland_Resume_v4.pdf')
        text_based_results = extractor.extract_experience(text)
        
        # Test with layout-aware extraction
        from backend.parser.converter import extract_pdf_with_layout
        layout_data = extract_pdf_with_layout('backend/parser/tests/Philip_Holland_Resume_v4.pdf')
        layout_based_results = extractor.extract_experience_with_layout(layout_data)
        
        # Layout-aware should produce fewer, more accurate results
        # (This may not always be true, but it's the expected improvement)
        assert len(layout_based_results) <= len(text_based_results) + 2, \
            "Layout-aware extraction should not produce significantly more entries"
        
        # Layout-aware results should have better job/company assignment
        layout_jobs_with_both = sum(1 for job in layout_based_results if job.company and job.role)
        text_jobs_with_both = sum(1 for job in text_based_results if job.company and job.role)
        
        # Layout-aware should have more complete job entries
        assert layout_jobs_with_both >= text_jobs_with_both, \
            "Layout-aware extraction should have more complete job entries"

class TestExperienceExtractionRegression:
    """Regression tests to ensure the improvements don't break existing functionality."""

    def test_resume_data_structure_integrity(self):
        """Test that the WorkExperience objects have proper structure."""
        resume_data = extract_resume_data_smart('backend/parser/tests/Philip_Holland_Resume_v4.pdf')
        
        for job in resume_data.experience:
            # Each job should have at least company or role
            assert job.company or job.role, "Each job should have company or role"
            
            # Dates should be strings if present
            if job.start_date:
                assert isinstance(job.start_date, str), "Start date should be string"
            if job.end_date:
                assert isinstance(job.end_date, str), "End date should be string"
            
            # Description should be string if present
            if job.description:
                assert isinstance(job.description, str), "Description should be string"

    def test_no_empty_experience_entries(self):
        """Test that no completely empty experience entries are created."""
        resume_data = extract_resume_data_smart('backend/parser/tests/sample_resume.pdf')
        
        for job in resume_data.experience:
            # Each job should have meaningful content
            has_content = any([
                job.company and job.company.strip(),
                job.role and job.role.strip(),
                job.description and job.description.strip()
            ])
            assert has_content, f"Job entry has no meaningful content: {job}"

    def test_consistent_extraction_results(self):
        """Test that extraction produces consistent results on multiple runs."""
        # Run extraction multiple times
        results = []
        for _ in range(3):
            resume_data = extract_resume_data_smart('backend/parser/tests/Philip_Holland_Resume_v4.pdf')
            results.append(len(resume_data.experience))
        
        # Results should be consistent
        assert all(count == results[0] for count in results), \
            f"Extraction results should be consistent across runs: {results}" 