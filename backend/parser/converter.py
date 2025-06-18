"""
converter.py

Converts resume files (PDF/DOCX) to plain text for parsing.
"""
import os
from typing import Optional

try:
    import pdfplumber # type: ignore
except ImportError:
    pdfplumber = None #Handles  import gracefully if pdfplumber is not installed. Prevents crash on import error.
try:
    import docx
except ImportError:
    docx = None

def convert_to_text(file_path: str) -> Optional[str]:
    """
    Detects file type and extracts text from PDF or DOCX.
    Returns extracted text as a string, or None if unsupported.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_pdf_text(file_path)
    elif ext == '.docx':
        return extract_docx_text(file_path)
    else:
        return None

def extract_pdf_text(file_path: str) -> str:
    """
    Extracts text from a PDF file using pdfplumber.
    """
    if not pdfplumber:
        raise ImportError("pdfplumber is not installed.") # Handles error if the function is used without the library available.
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_docx_text(file_path: str) -> str:
    """
    Extracts text from a DOCX file using python-docx.
    """
    if not docx:
        raise ImportError("python-docx is not installed.")
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])
