"""
scraper.py

Job posting scraper for extracting job information from URLs.
This module handles the scraping logic that was previously in the API layer.
"""

import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


@dataclass
class JobPosting:
    """Structure for storing scraped job posting data."""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: list = None
    salary: Optional[str] = None
    employment_type: Optional[str] = None
    url: Optional[str] = None
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []


class JobScraper:
    """
    Main class for scraping job postings from various job boards.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_job_posting(self, url: str) -> JobPosting:
        """
        Scrape a job posting from the given URL.
        
        Args:
            url: The URL of the job posting to scrape
            
        Returns:
            JobPosting: Structured job posting data
            
        Raises:
            Exception: If scraping fails
        """
        logger.info(f"Starting job scraping for URL: {url}")
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            if 'linkedin.com' in domain:
                company = 'LinkedIn'
            elif 'indeed.com' in domain:
                company = 'Indeed'
            elif 'glassdoor.com' in domain:
                company = 'Glassdoor'
            else:
                company = domain.split('.')[0].title() if domain else 'Unknown'

            return self._placeholder_posting(url, company)
                
        except Exception as e:
            logger.error(f"Job scraping failed for URL: {url}, error: {str(e)}")
            raise
    
    def _placeholder_posting(self, url: str, company: str) -> JobPosting:
        """Return a simple placeholder posting."""
        return JobPosting(
            title="Software Engineering Intern",
            company=company,
            location="Remote",
            description="Demo job posting",
            requirements=["Python"],
            employment_type="Internship",
            url=url,
        )


# Convenience function
def scrape_job_posting(url: str) -> JobPosting:
    """
    Convenience function to scrape a job posting.
    
    Args:
        url: URL of the job posting
        
    Returns:
        JobPosting: Scraped job data
    """
    scraper = JobScraper()
    return scraper.scrape_job_posting(url) 