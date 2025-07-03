"""
test_integration_refactored.py

Integration tests for the refactored API that uses actual parser, aggregator, and matcher modules.
Tests the end-to-end workflow with real business logic.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
import os

from ..main import app
from ..auth import create_demo_token
from ...parser.schemas import ResumeData, ContactInfo, Education, WorkExperience
from ...aggregator.scraper import JobPosting
from ...matcher.tailor import PatchPlan, PatchPlanItem, ActionEnum


class TestRefactoredIntegration:
    """Integration tests for the refactored API with actual business logic."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.test_token = create_demo_token("test-user", "test@example.com")
        self.headers = {"Authorization": f"Bearer {self.test_token}"}
    
    @patch('backend.parser.extractor.extract_resume_data_smart')
    def test_resume_parsing_integration(self, mock_extract):
        """Test that resume upload uses actual parser module."""
        # Mock the parser response
        mock_resume_data = ResumeData(
            contact=ContactInfo(name="John Doe", email="john@test.com"),
            education=[Education(degree="Bachelor's", field="Computer Science")],
            experience=[WorkExperience(company="Tech Co", role="Developer")],
            skills=["Python", "JavaScript"],
            additional_sections={},
            raw_text="Resume content..."
        )
        mock_extract.return_value = mock_resume_data
        
        # Create a test file
        test_file_content = b"Mock PDF content"
        test_file = io.BytesIO(test_file_content)
        
        # Upload resume
        response = self.client.post(
            "/v1/uploads/resume",
            headers=self.headers,
            files={"file": ("test_resume.pdf", test_file, "application/pdf")}
        )
        
        assert response.status_code == 201
        upload_data = response.json()
        upload_id = upload_data["upload_id"]
        
        # Verify parser was called (would be called in background job)
        # For this test, we're mocking the call but verifying integration works
        assert upload_id is not None
    
    @patch('backend.aggregator.scraper.scrape_job_posting')
    def test_job_scraping_integration(self, mock_scrape):
        """Test that job scraping uses actual aggregator module."""
        # Mock the scraper response
        mock_job_posting = JobPosting(
            title="Software Engineer",
            company="Google",
            location="Mountain View, CA",
            requirements=["Python", "Go", "Kubernetes"],
            description="Great opportunity...",
            employment_type="Full-time"
        )
        mock_scrape.return_value = mock_job_posting
        
        # Scrape job posting
        response = self.client.post(
            "/v1/jobs/scrape",
            headers=self.headers,
            json={"url": "https://careers.google.com/jobs/results/123456"}
        )
        
        assert response.status_code == 201
        job_data = response.json()
        job_id = job_data["job_id"]
        
        assert job_id is not None
        assert job_data["url"] == "https://careers.google.com/jobs/results/123456"
    
    @patch('backend.matcher.tailor.generate_patch_plan')
    def test_patch_plan_generation_integration(self, mock_generate):
        """Test that patch plan generation uses actual matcher module."""
        # Mock the matcher response
        mock_patch_items = [
            PatchPlanItem(
                id="skills_section",
                action=ActionEnum.INSERT_AFTER,
                suggested_text="Go, Kubernetes",
                rationale="Add skills mentioned in job requirements"
            ),
            PatchPlanItem(
                id="experience_1_description",
                action=ActionEnum.EDIT,
                suggested_text="Enhanced description with relevant keywords",
                rationale="Improve relevance to target position"
            )
        ]
        mock_patch_plan = PatchPlan(
            items=mock_patch_items,
            resume_id="test_resume",
            job_id="test_job",
            match_score=0.75
        )
        mock_generate.return_value = mock_patch_plan
        
        # Create patch plan
        response = self.client.post(
            "/v1/tailor/plan",
            headers=self.headers,
            json={"upload_id": "test-upload-id", "job_id": "test-job-id"}
        )
        
        assert response.status_code == 201
        plan_data = response.json()
        
        assert "plan_id" in plan_data
        assert "patch" in plan_data
        assert len(plan_data["patch"]) == 2
        assert plan_data["patch"][0]["action"] == "INSERT_AFTER"
        assert plan_data["patch"][1]["action"] == "EDIT"
    
    @patch('backend.api.jobs.extract_resume_data_smart')
    @patch('backend.api.jobs.scrape_job_posting')
    @patch('backend.api.jobs.generate_patch_plan')
    def test_full_workflow_with_real_modules(self, mock_patch_gen, mock_job_scrape, mock_resume_parse):
        """Test the complete workflow using mocked versions of the real modules."""
        # Mock parser response
        mock_resume_data = ResumeData(
            contact=ContactInfo(name="Alice Smith", email="alice@test.com"),
            education=[Education(degree="Master's", field="Data Science")],
            experience=[WorkExperience(company="Data Corp", role="Data Analyst")],
            skills=["Python", "SQL", "Machine Learning"],
            additional_sections={},
            raw_text="Data scientist resume..."
        )
        mock_resume_parse.return_value = mock_resume_data
        
        # Mock scraper response
        mock_job_posting = JobPosting(
            title="Senior Data Scientist",
            company="AI Startup",
            requirements=["Python", "TensorFlow", "AWS"],
            description="Exciting AI role...",
            url="https://aistartup.com/jobs/123"
        )
        mock_job_scrape.return_value = mock_job_posting
        
        # Mock matcher response
        mock_patch_plan = PatchPlan(
            items=[
                PatchPlanItem(
                    id="skills_tensorflow",
                    action=ActionEnum.INSERT_AFTER,
                    suggested_text="TensorFlow, AWS",
                    rationale="Add AI/cloud skills from job requirements"
                )
            ],
            resume_id="alice_resume",
            job_id="ai_startup_job",
            match_score=0.8
        )
        mock_patch_gen.return_value = mock_patch_plan
        
        # Step 1: Upload resume
        test_file = io.BytesIO(b"Mock resume content")
        upload_response = self.client.post(
            "/v1/uploads/resume",
            headers=self.headers,
            files={"file": ("resume.pdf", test_file, "application/pdf")}
        )
        
        assert upload_response.status_code == 201
        upload_id = upload_response.json()["upload_id"]
        
        # Step 2: Scrape job
        job_response = self.client.post(
            "/v1/jobs/scrape",
            headers=self.headers,
            json={"url": "https://aistartup.com/jobs/123"}
        )
        
        assert job_response.status_code == 201
        job_id = job_response.json()["job_id"]
        
        # Step 3: Generate patch plan
        plan_response = self.client.post(
            "/v1/tailor/plan",
            headers=self.headers,
            json={"upload_id": upload_id, "job_id": job_id}
        )
        
        assert plan_response.status_code == 201
        plan_data = plan_response.json()
        
        # Verify the complete workflow
        assert "plan_id" in plan_data
        assert "patch" in plan_data
        assert len(plan_data["patch"]) > 0
        assert plan_data["upload_id"] == upload_id
        assert plan_data["job_id"] == job_id
        
        # Verify the patch contains intelligent suggestions
        patch_item = plan_data["patch"][0]
        assert patch_item["action"] == "INSERT_AFTER"
        assert "tensorflow" in patch_item["suggested_text"].lower()
        assert len(patch_item["rationale"]) > 0


class TestModuleIntegration:
    """Test integration between modules without API layer."""
    
    def test_parser_to_matcher_integration(self):
        """Test that parser output works correctly with matcher input."""
        from ...parser.extractor import ResumeExtractor
        from ...matcher.tailor import ResumeTailor
        from ...aggregator.scraper import JobPosting
        
        # Create test data
        test_resume_text = """
        John Doe
        john@example.com
        (555) 123-4567
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology, 2022
        
        EXPERIENCE
        Software Developer
        Tech Company (2022-2023)
        • Developed web applications using Python and Django
        • Worked with SQL databases
        
        SKILLS
        Python, JavaScript, SQL, HTML, CSS
        """
        
        # Test parser -> matcher flow
        extractor = ResumeExtractor()
        resume_data = extractor.extract_all(test_resume_text)
        
        # Verify parser output
        assert resume_data.contact.name is not None
        assert len(resume_data.skills) > 0
        assert len(resume_data.experience) > 0
        
        # Test matcher with parser output
        job_posting = JobPosting(
            title="Full Stack Developer",
            requirements=["Python", "React", "PostgreSQL"],
            description="Full stack development position"
        )
        
        tailor = ResumeTailor()
        patch_plan = tailor.generate_patch_plan(resume_data, job_posting)
        
        # Verify matcher output
        assert isinstance(patch_plan.items, list)
        assert patch_plan.match_score > 0.0
        assert len(patch_plan.items) > 0
    
    def test_aggregator_to_matcher_integration(self):
        """Test that aggregator output works correctly with matcher input."""
        from ...aggregator.scraper import JobScraper
        from ...matcher.tailor import ResumeTailor
        from ...parser.schemas import ResumeData, ContactInfo
        
        # Test scraper output
        scraper = JobScraper()
        job_posting = scraper.scrape_job_posting("https://linkedin.com/jobs/view/123")
        
        # Verify scraper output
        assert job_posting.title is not None
        assert len(job_posting.requirements) > 0
        
        # Test matcher with scraper output
        sample_resume = ResumeData(
            contact=ContactInfo(name="Test User"),
            education=[],
            experience=[],
            skills=["Python", "JavaScript"],
            additional_sections={},
            raw_text="Sample resume content"
        )
        
        tailor = ResumeTailor()
        patch_plan = tailor.generate_patch_plan(sample_resume, job_posting)
        
        # Verify integration works
        assert isinstance(patch_plan.items, list)
        assert patch_plan.match_score >= 0.0


class TestErrorHandlingWithModules:
    """Test error handling when modules fail."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.test_token = create_demo_token("error-test-user", "error@example.com")
        self.headers = {"Authorization": f"Bearer {self.test_token}"}
    
    @patch('backend.parser.extractor.extract_resume_data_smart')
    def test_parser_error_handling(self, mock_extract):
        """Test API behavior when parser module fails."""
        # Mock parser to raise an exception
        mock_extract.side_effect = Exception("PDF parsing failed")
        
        test_file = io.BytesIO(b"Corrupted PDF content")
        response = self.client.post(
            "/v1/uploads/resume",
            headers=self.headers,
            files={"file": ("corrupted.pdf", test_file, "application/pdf")}
        )
        
        # Should still accept the upload (parsing happens in background)
        assert response.status_code == 201
        # The actual error would be caught in the background job
    
    @patch('backend.aggregator.scraper.scrape_job_posting')
    def test_scraper_error_handling(self, mock_scrape):
        """Test API behavior when scraper module fails."""
        # Mock scraper to raise an exception
        mock_scrape.side_effect = Exception("Network timeout")
        
        response = self.client.post(
            "/v1/jobs/scrape",
            headers=self.headers,
            json={"url": "https://badwebsite.com/jobs/123"}
        )
        
        # Should still accept the scraping request (processing happens in background)
        assert response.status_code == 201
        # The actual error would be caught in the background job
    
    @patch('backend.matcher.tailor.generate_patch_plan')
    def test_matcher_error_handling(self, mock_generate):
        """Test API behavior when matcher module fails."""
        # Mock matcher to raise an exception
        mock_generate.side_effect = Exception("AI service unavailable")
        
        response = self.client.post(
            "/v1/tailor/plan",
            headers=self.headers,
            json={"upload_id": "test-upload", "job_id": "test-job"}
        )
        
        # Should handle the error gracefully
        # The specific behavior depends on how the API is configured to handle matcher errors
        # In this case, it might return a 500 error or fall back to default behavior 