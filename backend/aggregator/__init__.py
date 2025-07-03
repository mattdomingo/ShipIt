"""
Job Aggregator Module

This module handles fetching and scraping job postings from various sources.
"""

from .scraper import JobScraper, scrape_job_posting

__all__ = ['JobScraper', 'scrape_job_posting'] 