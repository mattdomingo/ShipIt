"""
test_scraper.py

Tests for the job scraper functionality in the aggregator module.
"""

import pytest
from unittest.mock import Mock, patch
from .scraper import JobScraper, JobPosting, scrape_job_posting


class TestJobPosting:
    """Test the JobPosting dataclass."""
    
    def test_job_posting_creation(self):
        """Test creating a JobPosting with all fields."""
        job = JobPosting(
            title="Software Engineer",
            company="Test Corp",
            location="San Francisco, CA",
            description="Great job opportunity",
            requirements=["Python", "React"],
            salary="$80,000",
            employment_type="Full-time",
            url="https://example.com/job"
        )
        
        assert job.title == "Software Engineer"
        assert job.company == "Test Corp"
        assert job.location == "San Francisco, CA"
        assert job.description == "Great job opportunity"
        assert job.requirements == ["Python", "React"]
        assert job.salary == "$80,000"
        assert job.employment_type == "Full-time"
        assert job.url == "https://example.com/job"
    
    def test_job_posting_defaults(self):
        """Test JobPosting with default values."""
        job = JobPosting()
        
        assert job.title is None
        assert job.company is None
        assert job.location is None
        assert job.description is None
        assert job.requirements == []  # Should default to empty list
        assert job.salary is None
        assert job.employment_type is None
        assert job.url is None


class TestJobScraper:
    """Test the JobScraper class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = JobScraper()
    
    def test_scraper_initialization(self):
        """Test that scraper initializes correctly."""
        assert self.scraper.session is not None
        assert 'Mozilla' in self.scraper.session.headers['User-Agent']
    
    def test_linkedin_scraping(self):
        """Test LinkedIn job scraping."""
        url = "https://www.linkedin.com/jobs/view/123456"
        result = self.scraper.scrape_job_posting(url)
        
        assert isinstance(result, JobPosting)
        assert result.title is not None
        assert result.company == "LinkedIn"
        assert result.employment_type == "Internship"
        assert result.url == url
        assert len(result.requirements) > 0
    
    def test_indeed_scraping(self):
        """Test Indeed job scraping."""
        url = "https://www.indeed.com/viewjob?jk=123456"
        result = self.scraper.scrape_job_posting(url)
        
        assert isinstance(result, JobPosting)
        assert result.title is not None
        assert result.company == "Indeed"
        assert result.employment_type == "Internship"
        assert result.url == url
        assert len(result.requirements) > 0
    
    def test_glassdoor_scraping(self):
        """Test Glassdoor job scraping."""
        url = "https://www.glassdoor.com/job-listing/123456"
        result = self.scraper.scrape_job_posting(url)
        
        assert isinstance(result, JobPosting)
        assert result.title is not None
        assert result.company == "Glassdoor"
        assert result.employment_type == "Internship"
        assert result.url == url
        assert len(result.requirements) > 0
    
    def test_generic_scraping(self):
        """Test generic job board scraping."""
        url = "https://careers.techcorp.com/job/123456"
        result = self.scraper.scrape_job_posting(url)
        
        assert isinstance(result, JobPosting)
        assert result.title is not None
        assert result.company == "Careers"  # Should extract from domain
        assert result.employment_type == "Internship"
        assert result.url == url
        assert len(result.requirements) > 0
    
    def test_scraping_error_handling(self):
        """Test error handling in scraping."""
        # Mock a method to raise an exception
        with patch.object(self.scraper, '_scrape_generic', side_effect=Exception("Network error")):
            with pytest.raises(Exception) as exc_info:
                self.scraper.scrape_job_posting("https://example.com/job")
            
            assert "Network error" in str(exc_info.value)


class TestConvenienceFunction:
    """Test the convenience function."""
    
    def test_scrape_job_posting_function(self):
        """Test the scrape_job_posting convenience function."""
        url = "https://www.linkedin.com/jobs/view/123456"
        result = scrape_job_posting(url)
        
        assert isinstance(result, JobPosting)
        assert result.url == url
        assert result.company == "LinkedIn"
    
    def test_function_creates_new_scraper_instance(self):
        """Test that the function creates a new scraper instance."""
        url = "https://example.com/job"
        
        with patch('backend.aggregator.scraper.JobScraper') as mock_scraper_class:
            mock_scraper = Mock()
            mock_job_posting = JobPosting(title="Test Job")
            mock_scraper.scrape_job_posting.return_value = mock_job_posting
            mock_scraper_class.return_value = mock_scraper
            
            result = scrape_job_posting(url)
            
            mock_scraper_class.assert_called_once()
            mock_scraper.scrape_job_posting.assert_called_once_with(url)
            assert result == mock_job_posting


class TestDomainDetection:
    """Test domain-specific scraping logic."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = JobScraper()
    
    def test_linkedin_domain_detection(self):
        """Test that LinkedIn URLs are properly detected."""
        urls = [
            "https://www.linkedin.com/jobs/view/123456",
            "https://linkedin.com/jobs/view/123456",
            "https://ca.linkedin.com/jobs/view/123456"
        ]
        
        for url in urls:
            result = self.scraper.scrape_job_posting(url)
            assert result.company == "LinkedIn"
    
    def test_indeed_domain_detection(self):
        """Test that Indeed URLs are properly detected."""
        urls = [
            "https://www.indeed.com/viewjob?jk=123456",
            "https://indeed.com/viewjob?jk=123456",
            "https://ca.indeed.com/viewjob?jk=123456"
        ]
        
        for url in urls:
            result = self.scraper.scrape_job_posting(url)
            assert result.company == "Indeed"
    
    def test_glassdoor_domain_detection(self):
        """Test that Glassdoor URLs are properly detected."""
        urls = [
            "https://www.glassdoor.com/job-listing/123456",
            "https://glassdoor.com/job-listing/123456",
            "https://ca.glassdoor.com/job-listing/123456"
        ]
        
        for url in urls:
            result = self.scraper.scrape_job_posting(url)
            assert result.company == "Glassdoor"


class TestIntegration:
    """Integration tests for the scraper module."""
    
    def test_end_to_end_scraping_workflow(self):
        """Test complete scraping workflow."""
        # Test with a realistic URL
        url = "https://careers.google.com/jobs/results/123456"
        
        scraper = JobScraper()
        result = scraper.scrape_job_posting(url)
        
        # Verify we get a complete JobPosting object
        assert isinstance(result, JobPosting)
        assert result.url == url
        assert result.title is not None
        assert result.company is not None
        assert result.employment_type is not None
        assert isinstance(result.requirements, list)
        assert len(result.requirements) > 0
    
    def test_different_url_formats(self):
        """Test scraping with various URL formats."""
        urls = [
            "https://jobs.netflix.com/jobs/123456",
            "https://careers.spotify.com/job/123456",
            "https://jobs.apple.com/en-us/details/123456",
            "https://amazon.jobs/en/jobs/123456"
        ]
        
        scraper = JobScraper()
        
        for url in urls:
            result = scraper.scrape_job_posting(url)
            assert isinstance(result, JobPosting)
            assert result.url == url
            assert result.company is not None 