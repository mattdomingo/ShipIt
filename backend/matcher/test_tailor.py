"""
test_tailor.py

Tests for the resume tailor functionality in the matcher module.
"""

import pytest
from .tailor import (
    ResumeTailor, PatchPlanItem, PatchPlan, ActionEnum, 
    generate_patch_plan
)
from .analyzer import ResumeJobAnalyzer
from ..parser.schemas import ResumeData, ContactInfo, Education, WorkExperience
from ..aggregator.scraper import JobPosting


class TestActionEnum:
    """Test the ActionEnum."""
    
    def test_enum_values(self):
        """Test that ActionEnum has correct values."""
        assert ActionEnum.KEEP == "KEEP"
        assert ActionEnum.DELETE == "DELETE"
        assert ActionEnum.EDIT == "EDIT"
        assert ActionEnum.INSERT_AFTER == "INSERT_AFTER"


class TestPatchPlanItem:
    """Test the PatchPlanItem dataclass."""
    
    def test_patch_plan_item_creation(self):
        """Test creating a PatchPlanItem."""
        item = PatchPlanItem(
            id="test_id",
            action=ActionEnum.EDIT,
            suggested_text="Test text",
            rationale="Test rationale"
        )
        
        assert item.id == "test_id"
        assert item.action == ActionEnum.EDIT
        assert item.suggested_text == "Test text"
        assert item.rationale == "Test rationale"
    
    def test_patch_plan_item_to_dict(self):
        """Test converting PatchPlanItem to dictionary."""
        item = PatchPlanItem(
            id="test_id",
            action=ActionEnum.EDIT,
            suggested_text="Test text",
            rationale="Test rationale"
        )
        
        result = item.to_dict()
        expected = {
            "id": "test_id",
            "action": "EDIT",
            "suggested_text": "Test text",
            "rationale": "Test rationale"
        }
        
        assert result == expected


class TestPatchPlan:
    """Test the PatchPlan dataclass."""
    
    def test_patch_plan_creation(self):
        """Test creating a PatchPlan."""
        items = [
            PatchPlanItem("id1", ActionEnum.EDIT, "text1", "rationale1"),
            PatchPlanItem("id2", ActionEnum.DELETE, None, "rationale2")
        ]
        
        plan = PatchPlan(
            items=items,
            resume_id="resume_123",
            job_id="job_456",
            match_score=0.75
        )
        
        assert len(plan.items) == 2
        assert plan.resume_id == "resume_123"
        assert plan.job_id == "job_456"
        assert plan.match_score == 0.75
    
    def test_patch_plan_to_dict(self):
        """Test converting PatchPlan to dictionary."""
        items = [PatchPlanItem("id1", ActionEnum.EDIT, "text1", "rationale1")]
        plan = PatchPlan(items, "resume_123", "job_456", 0.8)
        
        result = plan.to_dict()
        
        assert "items" in result
        assert "resume_id" in result
        assert "job_id" in result
        assert "match_score" in result
        assert len(result["items"]) == 1
        assert result["resume_id"] == "resume_123"
        assert result["job_id"] == "job_456"
        assert result["match_score"] == 0.8


class TestResumeTailor:
    """Test the ResumeTailor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tailor = ResumeTailor()
        
        # Create sample resume data
        self.sample_resume = ResumeData(
            contact=ContactInfo(name="John Doe", email="john@example.com"),
            education=[Education(degree="Bachelor's", field="Computer Science", institution="University")],
            experience=[
                WorkExperience(
                    company="Tech Co",
                    role="Developer",
                    description="Built web applications using JavaScript",
                    skills_used=["JavaScript", "HTML"]
                )
            ],
            skills=["Python", "JavaScript", "HTML"],
            additional_sections={},
            raw_text="John Doe resume content with Python and JavaScript experience..."
        )
        
        # Create sample job posting
        self.sample_job = JobPosting(
            title="Software Engineer Intern",
            company="Target Corp",
            requirements=["Python", "React", "SQL"],
            description="Looking for a software engineer intern with Python and React experience..."
        )
    
    def test_tailor_initialization(self):
        """Test that tailor initializes correctly."""
        assert self.tailor.skill_keywords is not None
        assert isinstance(self.tailor.skill_keywords, dict)
        assert "programming" in self.tailor.skill_keywords
        assert "web" in self.tailor.skill_keywords
    
    def test_generate_patch_plan(self):
        """Test generating a complete patch plan."""
        plan = self.tailor.generate_patch_plan(self.sample_resume, self.sample_job)
        
        assert isinstance(plan, PatchPlan)
        assert isinstance(plan.items, list)
        assert plan.match_score >= 0.0
        assert plan.match_score <= 1.0
    
    def test_skills_gap_analysis(self):
        """Test skills gap analysis."""
        patches = self.tailor._analyze_skills_gap(self.sample_resume, self.sample_job)
        
        # Should suggest adding missing skills (React, SQL)
        assert len(patches) > 0
        skill_patch = patches[0]
        assert skill_patch.action == ActionEnum.INSERT_AFTER
        assert "react" in skill_patch.suggested_text.lower() or "sql" in skill_patch.suggested_text.lower()
    
    def test_experience_relevance_analysis(self):
        """Test experience relevance analysis."""
        patches = self.tailor._analyze_experience_relevance(self.sample_resume, self.sample_job)
        
        # May suggest enhancing experience descriptions
        assert isinstance(patches, list)
        for patch in patches:
            assert patch.action in [ActionEnum.EDIT, ActionEnum.INSERT_AFTER]
            assert len(patch.rationale) > 0
    
    def test_keyword_alignment_analysis(self):
        """Test keyword alignment analysis."""
        patches = self.tailor._analyze_keyword_alignment(self.sample_resume, self.sample_job)
        
        assert isinstance(patches, list)
        # Test will depend on specific keywords missing
    
    def test_match_score_calculation(self):
        """Test match score calculation."""
        score = self.tailor._calculate_match_score(self.sample_resume, self.sample_job)
        
        # Should be between 0 and 1
        assert 0.0 <= score <= 1.0
        
        # With Python matching, should be > 0
        assert score > 0.0
    
    def test_match_score_with_no_requirements(self):
        """Test match score when job has no requirements."""
        job_no_reqs = JobPosting(title="Job", company="Company", requirements=[])
        score = self.tailor._calculate_match_score(self.sample_resume, job_no_reqs)
        
        assert score == 0.5  # Default score
    
    def test_keyword_extraction_from_job(self):
        """Test extracting keywords from job posting."""
        keywords = self.tailor._extract_keywords_from_job(self.sample_job)
        
        assert isinstance(keywords, list)
        assert "python" in keywords
        assert "react" in keywords
        assert "sql" in keywords
        assert len(keywords) <= 10  # Should limit to top 10


class TestConvenienceFunction:
    """Test the convenience function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_resume = ResumeData(
            contact=ContactInfo(name="Test User"),
            education=[],
            experience=[],
            skills=["Python"],
            additional_sections={},
            raw_text="Test resume"
        )
        
        self.sample_job = JobPosting(
            title="Test Job",
            requirements=["Python", "SQL"]
        )
    
    def test_generate_patch_plan_function(self):
        """Test the generate_patch_plan convenience function."""
        plan = generate_patch_plan(self.sample_resume, self.sample_job)
        
        assert isinstance(plan, PatchPlan)
        assert isinstance(plan.items, list)
        assert plan.match_score >= 0.0


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tailor = ResumeTailor()
    
    def test_empty_resume(self):
        """Test handling empty resume data."""
        empty_resume = ResumeData(
            contact=ContactInfo(),
            education=[],
            experience=[],
            skills=[],
            additional_sections={},
            raw_text=""
        )
        
        job = JobPosting(title="Job", requirements=["Python"])
        
        plan = self.tailor.generate_patch_plan(empty_resume, job)
        assert isinstance(plan, PatchPlan)
        assert plan.match_score == 0.0
    
    def test_empty_job_posting(self):
        """Test handling empty job posting."""
        resume = ResumeData(
            contact=ContactInfo(name="User"),
            education=[],
            experience=[],
            skills=["Python"],
            additional_sections={},
            raw_text="Resume content"
        )
        
        empty_job = JobPosting()
        
        plan = self.tailor.generate_patch_plan(resume, empty_job)
        assert isinstance(plan, PatchPlan)
    
    def test_perfect_match_resume(self):
        """Test resume that perfectly matches job requirements."""
        perfect_resume = ResumeData(
            contact=ContactInfo(name="Perfect Candidate"),
            education=[Education(degree="Master's", field="Computer Science")],
            experience=[
                WorkExperience(
                    company="Tech Co",
                    role="Developer",
                    description="Extensive experience with Python, React, and SQL databases"
                )
            ],
            skills=["Python", "React", "SQL", "JavaScript"],
            additional_sections={},
            raw_text="Perfect resume with Python, React, SQL experience"
        )
        
        job = JobPosting(
            title="Developer",
            requirements=["Python", "React", "SQL"]
        )
        
        plan = self.tailor.generate_patch_plan(perfect_resume, job)
        assert plan.match_score == 1.0  # Perfect match


class TestResumeJobAnalyzer:
    """Test the ResumeJobAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ResumeJobAnalyzer()
        
        self.sample_resume = ResumeData(
            contact=ContactInfo(name="Analyst Test"),
            education=[],
            experience=[
                WorkExperience(
                    company="Dev Co",
                    role="Junior Developer",
                    description="Worked with Python and web technologies"
                )
            ],
            skills=["Python", "HTML", "CSS"],
            additional_sections={},
            raw_text="Resume with Python experience"
        )
        
        self.sample_job = JobPosting(
            title="Python Developer",
            requirements=["Python", "Django", "PostgreSQL"],
            description="Python developer position"
        )
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        assert isinstance(self.analyzer, ResumeJobAnalyzer)
    
    def test_analyze_compatibility(self):
        """Test complete compatibility analysis."""
        result = self.analyzer.analyze_compatibility(self.sample_resume, self.sample_job)
        
        assert "compatibility_score" in result
        assert "skill_analysis" in result
        assert "experience_analysis" in result
        assert "recommendations" in result
        
        assert 0.0 <= result["compatibility_score"] <= 1.0
        assert isinstance(result["recommendations"], list)
    
    def test_skills_match_analysis(self):
        """Test skills matching analysis."""
        analysis = self.analyzer._analyze_skills_match(self.sample_resume, self.sample_job)
        
        assert "match_percentage" in analysis
        assert "matched_skills" in analysis
        assert "missing_skills" in analysis
        assert "total_requirements" in analysis
        
        assert "python" in analysis["matched_skills"]
        assert "django" in analysis["missing_skills"]
        assert "postgresql" in analysis["missing_skills"]
    
    def test_experience_relevance_analysis(self):
        """Test experience relevance analysis."""
        analysis = self.analyzer._analyze_experience_relevance(self.sample_resume, self.sample_job)
        
        assert "relevance_score" in analysis
        assert "relevant_experiences" in analysis
        assert "total_experiences" in analysis
        
        assert analysis["total_experiences"] == 1 