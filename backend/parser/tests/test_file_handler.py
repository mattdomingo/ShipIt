import io
import os
from backend.parser.file_handler import allowed_file, save_file, cleanup_uploads, UPLOAD_DIR

def test_allowed_file():
    assert allowed_file("resume.pdf")
    assert allowed_file("resume.docx")
    assert not allowed_file("resume.txt")
    assert not allowed_file("resume.exe")

def test_save_file_and_cleanup():
    # Create a fake PDF file stream
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake pdf content")
    filename = "test_resume.pdf"
    saved_path = save_file(fake_pdf, filename)
    assert saved_path is not None
    assert os.path.exists(saved_path)
    assert saved_path.endswith(filename)

    # Create a fake unsupported file stream
    fake_txt = io.BytesIO(b"plain text content")
    txt_path = save_file(fake_txt, "resume.txt")
    assert txt_path is None

    # Cleanup uploads and check directory is removed
    cleanup_uploads()
    assert not os.path.exists(UPLOAD_DIR)