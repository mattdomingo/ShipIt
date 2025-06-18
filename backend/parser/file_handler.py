"""
file_handler.py

Handles saving and validating uploaded resume files.
"""

import os
import shutil
from typing import Optional

ALLOWED_EXTENSIONS = {'.pdf', '.docx'}
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')

def allowed_file(filename: str) -> bool:
    """
    Checks if the file has an allowed extension.
    """
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file_stream, filename: str) -> Optional[str]:
    """
    Saves the uploaded file stream to the uploads directory.
    Returns the saved file path, or None if not allowed.
    """
    if not allowed_file(filename):
        return None

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, 'wb') as f:
        shutil.copyfileobj(file_stream, f)

    return file_path

def cleanup_uploads():
    """
    Deletes all files in the uploads directory (for test cleanup).
    """
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)