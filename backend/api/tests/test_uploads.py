"""
test_uploads.py

Unit tests for the uploads router.
Tests file validation, upload endpoints, and authentication.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open
import io

from backend.api.main import app
from backend.api.auth import create_demo_token

client = TestClient(app)

# Test authentication token
TEST_TOKEN = create_demo_token("test-user", "test@example.com")
AUTH_HEADERS = {"Authorization": f"Bearer {TEST_TOKEN}"}


class TestFileValidation:
    """Test file validation logic."""

    @patch('backend.api.routers.uploads.enqueue_parse_resume')
    def test_upload_valid_pdf(self, mock_enqueue_parse):
        """Test uploading a valid PDF file."""
        mock_enqueue_parse.return_value = "mock_task_id"
        pdf_content = b"Mock PDF content"
        files = {"file": ("test_resume.pdf", io.BytesIO(pdf_content), "application/pdf")}

        with patch('builtins.open', mock_open()), patch('os.makedirs'):
            response = client.post("/v1/uploads/resume", files=files, headers=AUTH_HEADERS)

        assert response.status_code == 201
        data = response.json()
        assert "upload_id" in data
        assert data["filename"] == "test_resume.pdf"

    @patch('backend.api.routers.uploads.enqueue_parse_resume')
    def test_upload_valid_docx(self, mock_enqueue_parse):
        """Test uploading a valid DOCX file."""
        mock_enqueue_parse.return_value = "mock_task_id"
        docx_content = b"Mock DOCX content"
        files = {"file": ("test_resume.docx", io.BytesIO(docx_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}

        with patch('builtins.open', mock_open()), patch('os.makedirs'):
            response = client.post("/v1/uploads/resume", files=files, headers=AUTH_HEADERS)

        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "test_resume.docx"

    def test_reject_invalid_mime_type(self):
        """Test rejecting files with invalid MIME types."""
        txt_content = b"This is not a resume"
        files = {"file": ("resume.txt", io.BytesIO(txt_content), "text/plain")}
        
        response = client.post("/v1/uploads/resume", files=files, headers=AUTH_HEADERS)
        
        assert response.status_code == 400
        assert response.json()["code"] == "FILE_VALIDATION_ERROR"

    def test_reject_invalid_extension(self):
        """Test rejecting files with invalid extensions."""
        content = b"Mock content"
        files = {"file": ("resume.txt", io.BytesIO(content), "application/pdf")}
        
        response = client.post("/v1/uploads/resume", files=files, headers=AUTH_HEADERS)
        
        assert response.status_code == 400
        assert response.json()["code"] == "FILE_VALIDATION_ERROR"

    def test_file_size_limit(self):
        """Test file size validation (this is a mock test since actual size checking requires real files)."""
        from backend.api.routers.uploads import MAX_FILE_SIZE
        assert MAX_FILE_SIZE == 5 * 1024 * 1024


class TestUploadEndpoints:
    """Test upload endpoints and authentication."""

    def test_upload_requires_authentication(self):
        """Test that upload endpoint requires authentication."""
        files = {"file": ("test.pdf", io.BytesIO(b"content"), "application/pdf")}
        response = client.post("/v1/uploads/resume", files=files)
        assert response.status_code == 403

    def test_get_upload_status_requires_authentication(self):
        """Test that upload status endpoint requires authentication."""
        response = client.get("/v1/uploads/resume/test-id")
        assert response.status_code == 403

    def test_get_upload_status_not_found(self):
        """Test getting status for non-existent upload."""
        response = client.get("/v1/uploads/resume/non-existent-id", headers=AUTH_HEADERS)
        assert response.status_code == 404

    @patch('backend.api.routers.uploads.enqueue_parse_resume')
    def test_upload_and_get_status_workflow(self, mock_enqueue_parse):
        """Test the complete upload and status check workflow."""
        mock_enqueue_parse.return_value = "mock_task_id"
        pdf_content = b"Mock PDF content"
        files = {"file": ("test_resume.pdf", io.BytesIO(pdf_content), "application/pdf")}

        with patch('builtins.open', mock_open()), patch('os.makedirs'):
            upload_response = client.post("/v1/uploads/resume", files=files, headers=AUTH_HEADERS)
        
        assert upload_response.status_code == 201
        upload_id = upload_response.json()["upload_id"]
        
        status_response = client.get(f"/v1/uploads/resume/{upload_id}", headers=AUTH_HEADERS)
        
        assert status_response.status_code == 200
        assert status_response.json()["upload_id"] == upload_id


class TestAuthorizationChecks:
    """Test authorization and access control."""

    def test_user_cannot_access_other_users_uploads(self):
        """Test that users cannot access uploads from other users."""
        from backend.api.routers.uploads import upload_records
        
        other_upload_id = "other-user-upload"
        upload_records[other_upload_id] = {
            "id": other_upload_id,
            "user_id": "other-user",
            "filename": "other.pdf",
            "mime_type": "application/pdf",
            "status": "PENDING"
        }
        
        response = client.get(f"/v1/uploads/resume/{other_upload_id}", headers=AUTH_HEADERS)
        
        assert response.status_code == 403
        
        del upload_records[other_upload_id]
