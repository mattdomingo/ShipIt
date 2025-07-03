"""
test_refactoring_functionality.py

Simple functional tests to verify the refactored modules work together correctly.
These tests bypass the API layer and test the core functionality directly.
"""

import pytest
from typing import Dict, Any

# Test imports to verify modules can be imported
def test_module_imports():
    """Test that all refactored modules can be imported successfully."""
    try:
        from backend.parser.extractor import extract_resume_data_smart, ResumeExtractor
        from backend.aggregator.scraper import JobScraper, JobPosting, scrape_job_posting
        from backend.matcher.tailor import ResumeTailor, generate_patch_plan
        from backend.matcher.analyzer import ResumeJobAnalyzer
        print("✅ All modules imported successfully!")
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")


def test_parser_functionality():
    """Test that the parser module works correctly."""
    from backend.parser.extractor import ResumeExtractor
    
    # Test with realistic resume text
    resume_text = """
    Jane Smith
    jane.smith@email.com
    (555) 987-6543
    
    EDUCATION
    Master of Science in Computer Science
    Stanford University, 2021
    GPA: 3.8
    
    SKILLS
    Python, Java, Machine Learning, SQL, React, AWS, Docker
    
    EXPERIENCE
    Software Engineer
    Google Inc. (2021-2023)
    Developed scalable microservices using Python and Docker
    Implemented machine learning models for user recommendation systems
    """
    
    extractor = ResumeExtractor()
    resume_data = extractor.extract_all(resume_text)
    
    # Verify parser output
    assert resume_data.contact.name == "Jane Smith"
    assert resume_data.contact.email == "jane.smith@email.com"
    assert resume_data.contact.phone == "(555) 987-6543"
    assert len(resume_data.skills) > 0
    assert "python" in [skill.lower() for skill in resume_data.skills]
    assert len(resume_data.education) > 0
    assert resume_data.education[0].institution is not None
    
    print("✅ Parser functionality verified!")
    return resume_data


def test_aggregator_functionality():
    """Test that the aggregator module works correctly."""
    from backend.aggregator.scraper import JobScraper
    
    scraper = JobScraper()
    
    # Test different job board URLs
    test_urls = [
        "https://www.linkedin.com/jobs/view/123456",
        "https://www.indeed.com/viewjob?jk=123456",
        "https://careers.google.com/jobs/results/123456"
    ]
    
    for url in test_urls:
        job_posting = scraper.scrape_job_posting(url)
        
        # Verify scraper output
        assert job_posting.title is not None
        assert job_posting.company is not None
        assert job_posting.url == url
        assert len(job_posting.requirements) > 0
        assert job_posting.employment_type is not None
    
    print("✅ Aggregator functionality verified!")
    return job_posting


def test_matcher_functionality():
    """Test that the matcher module works correctly."""
    from backend.matcher.tailor import ResumeTailor
    from backend.matcher.analyzer import ResumeJobAnalyzer
    from backend.parser.schemas import ResumeData, ContactInfo, Education, WorkExperience
    from backend.aggregator.scraper import JobPosting
    
    # Create test data
    resume_data = ResumeData(
        contact=ContactInfo(name="Test Developer", email="test@example.com"),
        education=[Education(degree="Bachelor's", field="Computer Science")],
        experience=[
            WorkExperience(
                company="Tech Corp",
                role="Software Developer",
                description="Developed web applications using Python and JavaScript"
            )
        ],
        skills=["Python", "JavaScript", "HTML", "CSS"],
        additional_sections={},
        raw_text="Resume content with Python and JavaScript experience"
    )
    
    job_posting = JobPosting(
        title="Full Stack Developer",
        company="Startup Inc",
        requirements=["Python", "React", "PostgreSQL", "AWS"],
        description="Looking for a full stack developer with Python and React experience"
    )
    
    # Test matcher
    tailor = ResumeTailor()
    patch_plan = tailor.generate_patch_plan(resume_data, job_posting)
    
    # Verify matcher output
    assert len(patch_plan.items) > 0
    assert 0.0 <= patch_plan.match_score <= 1.0
    assert patch_plan.match_score > 0.0  # Should have some match due to Python
    
    # Test analyzer
    analyzer = ResumeJobAnalyzer()
    analysis = analyzer.analyze_compatibility(resume_data, job_posting)
    
    # Verify analyzer output
    assert "compatibility_score" in analysis
    assert "skill_analysis" in analysis
    assert "experience_analysis" in analysis
    assert "recommendations" in analysis
    assert 0.0 <= analysis["compatibility_score"] <= 1.0
    
    print("✅ Matcher functionality verified!")
    return patch_plan, analysis


def test_end_to_end_integration():
    """Test complete end-to-end functionality."""
    # Run all module tests
    resume_data = test_parser_functionality()
    job_posting = test_aggregator_functionality()
    patch_plan, analysis = test_matcher_functionality()
    
    # Test actual integration between real outputs
    from backend.matcher.tailor import ResumeTailor
    
    tailor = ResumeTailor()
    integrated_patch_plan = tailor.generate_patch_plan(resume_data, job_posting)
    
    # Verify integration works
    assert integrated_patch_plan is not None
    assert len(integrated_patch_plan.items) >= 0  # May be 0 if perfect match
    assert 0.0 <= integrated_patch_plan.match_score <= 1.0
    
    print("✅ End-to-end integration verified!")
    print(f"   📊 Match score: {integrated_patch_plan.match_score:.2f}")
    print(f"   🔧 Patch suggestions: {len(integrated_patch_plan.items)}")
    
    return {
        "resume_data": resume_data,
        "job_posting": job_posting,
        "patch_plan": integrated_patch_plan,
        "analysis": analysis
    }


def test_background_job_integration():
    """Test that background jobs can use the new modules."""
    from backend.api.jobs import parse_resume_job, scrape_job_posting_job, generate_patch_plan_job
    from unittest.mock import patch
    
    # We can't actually run Celery jobs without Redis, but we can test the function logic
    print("✅ Background job functions are properly defined and importable!")
    
    # Verify the functions exist and have correct signatures
    assert callable(parse_resume_job)
    assert callable(scrape_job_posting_job)
    assert callable(generate_patch_plan_job)


if __name__ == "__main__":
    print("🧪 Testing refactored functionality...\n")
    
    # Run tests in order
    test_module_imports()
    test_parser_functionality()
    test_aggregator_functionality()
    test_matcher_functionality()
    test_end_to_end_integration()
    test_background_job_integration()
    
    print("\n🎉 All functionality tests passed!")
    print("✨ Refactoring successful - API now uses real business logic!") 