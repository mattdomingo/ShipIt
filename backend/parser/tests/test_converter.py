"""
Test file for the converter module.
Tests PDF and DOCX text extraction functionality.
"""

# Legacy Windows environment variable setup (commented out)
#$env:PYTHONPATH="C:\Users\mdh9632\OneDrive - TruStage\Desktop\Projects\ShipIt"
#pytest backend/parser/tests/test_converter.py

# Import required modules for file operations and testing
import os
import pytest # type: ignore  # Suppress type checking warnings for pytest

# Import the functions we want to test from the converter module
from backend.parser.converter import convert_to_text, extract_pdf_text, extract_docx_text

# Get the directory where this test file is located
TEST_DIR = os.path.dirname(__file__)

# Create full paths to the sample files used for testing
SAMPLE_PDF = os.path.join(TEST_DIR, "sample_resume.pdf")
SAMPLE_DOCX = os.path.join(TEST_DIR, "sample_resume.docx")

# Skip this test if the sample PDF file doesn't exist in the test directory
@pytest.mark.skipif(not os.path.exists(SAMPLE_PDF), reason="sample_resume.pdf not found")
def test_extract_pdf_text():
    """Test that extract_pdf_text can successfully extract text from a PDF file."""
    # Call the function to extract text from the sample PDF
    text = extract_pdf_text(SAMPLE_PDF)
    
    # Verify that the returned value is a string
    assert isinstance(text, str)
    
    # Verify that some text was actually extracted (length > 0)
    assert len(text) > 0

# Skip this test if the sample DOCX file doesn't exist in the test directory
@pytest.mark.skipif(not os.path.exists(SAMPLE_DOCX), reason="sample_resume.docx not found")
def test_extract_docx_text():
    """Test that extract_docx_text can successfully extract text from a DOCX file."""
    # Call the function to extract text from the sample DOCX
    text = extract_docx_text(SAMPLE_DOCX)
    
    # Verify that the returned value is a string
    assert isinstance(text, str)
    
    # Verify that some text was actually extracted (length > 0)
    assert len(text) > 0

# Skip this test if the sample PDF file doesn't exist in the test directory
@pytest.mark.skipif(not os.path.exists(SAMPLE_PDF), reason="sample_resume.pdf not found")
def test_convert_to_text_pdf():
    """Test that convert_to_text works correctly with PDF files."""
    # Call the generic convert_to_text function with a PDF file
    text = convert_to_text(SAMPLE_PDF)
    
    # Verify that the returned value is a string
    assert isinstance(text, str)
    
    # Verify that some text was actually extracted (length > 0)
    assert len(text) > 0

# Skip this test if the sample DOCX file doesn't exist in the test directory
@pytest.mark.skipif(not os.path.exists(SAMPLE_DOCX), reason="sample_resume.docx not found")
def test_convert_to_text_docx():
    """Test that convert_to_text works correctly with DOCX files."""
    # Call the generic convert_to_text function with a DOCX file
    text = convert_to_text(SAMPLE_DOCX)
    
    # Verify that the returned value is a string
    assert isinstance(text, str)
    
    # Verify that some text was actually extracted (length > 0)
    assert len(text) > 0

def test_convert_to_text_unsupported():
    """Test that convert_to_text returns None for unsupported file types."""
    # Create a path for a temporary text file in the test directory
    fake_file = os.path.join(TEST_DIR, "resume.txt")
    
    # Create a temporary text file with some content
    with open(fake_file, "w") as f:
        f.write("This is a plain text resume.")
    
    try:
        # Call convert_to_text with an unsupported file type (.txt)
        result = convert_to_text(fake_file)
        
        # Verify that the function returns None for unsupported files
        assert result is None
    finally:
        # Clean up: remove the temporary file we created
        os.remove(fake_file)