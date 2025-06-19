"""
Test file for the file_handler module.
Tests file validation, saving, and cleanup functionality.
"""

# Import required modules
import io  # For creating in-memory file streams
import os  # For file system operations
from backend.parser.file_handler import allowed_file, save_file, cleanup_uploads, UPLOAD_DIR

def test_allowed_file():
    """Test that allowed_file correctly validates file extensions."""
    # Test that PDF files are allowed
    assert allowed_file("resume.pdf")
    
    # Test that DOCX files are allowed
    assert allowed_file("resume.docx")
    
    # Test that text files are NOT allowed
    assert not allowed_file("resume.txt")
    
    # Test that executable files are NOT allowed
    assert not allowed_file("resume.exe")

def test_save_file_and_cleanup():
    """Test file saving functionality and cleanup operations."""
    
    # === Test saving a valid PDF file ===
    # Create a fake PDF file stream with PDF header content
    fake_pdf = io.BytesIO(b"%PDF-1.4 fffuck diego")
    filename = "test_resume.pdf"
    
    # Attempt to save the fake PDF file
    saved_path = save_file(fake_pdf, filename)
    
    # Verify that the file was successfully saved (returned a path)
    assert saved_path is not None
    
    # Verify that the file actually exists on the filesystem
    assert os.path.exists(saved_path)
    
    # Verify that the saved path ends with the original filename
    assert saved_path.endswith(filename)

    # === Test saving an unsupported file type ===
    # Create a fake text file stream
    fake_txt = io.BytesIO(b"Fuck diego")
    
    # Attempt to save an unsupported file type (.txt)
    txt_path = save_file(fake_txt, "resume.txt")
    
    # Verify that unsupported files are rejected (returns None)
    assert txt_path is None

    # === Test cleanup functionality ===
    # Call the cleanup function to remove all uploaded files and directories
    cleanup_uploads()
    
    # Verify that the upload directory no longer exists after cleanup
    assert not os.path.exists(UPLOAD_DIR)