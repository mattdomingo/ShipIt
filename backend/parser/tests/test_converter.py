#$env:PYTHONPATH="C:\Users\mdh9632\OneDrive - TruStage\Desktop\Projects\ShipIt"
#pytest backend/parser/tests/test_converter.py

import os
import pytest # type: ignore
from backend.parser.converter import convert_to_text, extract_pdf_text, extract_docx_text

TEST_DIR = os.path.dirname(__file__)
SAMPLE_PDF = os.path.join(TEST_DIR, "sample_resume.pdf")
SAMPLE_DOCX = os.path.join(TEST_DIR, "sample_resume.docx")

@pytest.mark.skipif(not os.path.exists(SAMPLE_PDF), reason="sample_resume.pdf not found")
def test_extract_pdf_text():
    text = extract_pdf_text(SAMPLE_PDF)
    assert isinstance(text, str)
    assert len(text) > 0

@pytest.mark.skipif(not os.path.exists(SAMPLE_DOCX), reason="sample_resume.docx not found")
def test_extract_docx_text():
    text = extract_docx_text(SAMPLE_DOCX)
    assert isinstance(text, str)
    assert len(text) > 0

@pytest.mark.skipif(not os.path.exists(SAMPLE_PDF), reason="sample_resume.pdf not found")
def test_convert_to_text_pdf():
    text = convert_to_text(SAMPLE_PDF)
    assert isinstance(text, str)
    assert len(text) > 0

@pytest.mark.skipif(not os.path.exists(SAMPLE_DOCX), reason="sample_resume.docx not found")
def test_convert_to_text_docx():
    text = convert_to_text(SAMPLE_DOCX)
    assert isinstance(text, str)
    assert len(text) > 0

def test_convert_to_text_unsupported():
    fake_file = os.path.join(TEST_DIR, "resume.txt")
    with open(fake_file, "w") as f:
        f.write("This is a plain text resume.")
    try:
        result = convert_to_text(fake_file)
        assert result is None
    finally:
        os.remove(fake_file)