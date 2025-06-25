"""
Matcher Module

This module handles matching parsed resume data to job postings and generating
tailored resume suggestions using keyword analysis and AI techniques.
"""

from .tailor import ResumeTailor, generate_patch_plan
from .analyzer import ResumeJobAnalyzer

__all__ = ['ResumeTailor', 'generate_patch_plan', 'ResumeJobAnalyzer'] 