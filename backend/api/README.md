# ShipIt API - Stage 1: Resume Tailor Interface Contracts

This document describes the Stage 1 implementation of the Resume Tailor feature, which provides **interface contracts and stubs only** - no business logic, parsing, scraping, or AI functionality has been implemented yet.

## 🎯 Stage 1 Deliverables

✅ **Public API Routes**
- `POST /v1/uploads/resume` - Resume file upload
- `POST /v1/jobs/scrape` - Job posting URL scraping
- `POST /v1/tailor/plan` - Patch plan generation
- `GET /v1/tailor/plan/{plan_id}` - Patch plan retrieval

✅ **Data Models & Schemas**
- Upload Response with file validation
- Scrape Response for job posting URLs
- Patch Plan Items with action types (KEEP, DELETE, EDIT, INSERT_AFTER)
- Plan Response with comprehensive metadata

✅ **Background Job Placeholders**
- ParseResumeJob (Celery task stub)
- ScrapeJobPostingJob (Celery task stub)
- GeneratePatchPlanJob (Celery task stub)

✅ **Operational Requirements**
- File validation (PDF/DOCX only, 5MB limit)
- JWT authentication on all endpoints
- Unified error handling with `{code, message, details}` format
- OpenAPI/Swagger documentation

✅ **Testing**
- Unit tests for file validation
- Integration tests for complete workflow
- Contract tests for OpenAPI compliance
- Authorization tests for security

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r config/requirements.txt
```

### 2. Start the API Server
```bash
python backend/api/run_server.py
```

The server will start on `http://localhost:8000` with:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 3. Get a Demo Token
When you start the server, it will print a demo JWT token for testing:
```
🔑 For testing, you can use this demo token:
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 4. Test the Endpoints

#### Upload a Resume
```bash
curl -X POST "http://localhost:8000/v1/uploads/resume" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -F "file=@path/to/resume.pdf"
```

#### Scrape a Job Posting
```bash
curl -X POST "http://localhost:8000/v1/jobs/scrape" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://careers.example.com/software-engineer"}'
```

#### Create a Patch Plan
```bash
curl -X POST "http://localhost:8000/v1/tailor/plan" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"upload_id": "your-upload-id", "job_id": "your-job-id"}'
```

## 📋 API Reference

### Upload Endpoints

#### `POST /v1/uploads/resume`
Upload a resume file for processing.

**Requirements:**
- File must be PDF or DOCX
- Maximum size: 5MB
- Authentication required

**Response:**
```json
{
  "upload_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "resume.pdf",
  "mime_type": "application/pdf",
  "status": "PENDING"
}
```

#### `GET /v1/uploads/resume/{upload_id}`
Get the status of an uploaded resume.

### Job Scraping Endpoints

#### `POST /v1/jobs/scrape`
Trigger scraping of a job posting URL.

**Requirements:**
- URL must use HTTPS
- Authentication required

**Request:**
```json
{
  "url": "https://careers.example.com/job-posting"
}
```

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174001",
  "url": "https://careers.example.com/job-posting",
  "status": "PENDING"
}
```

### Tailor Endpoints

#### `POST /v1/tailor/plan`
Create a patch plan by combining a resume and job posting.

**Requirements:**
- Resume must be in PARSED status
- Job must be in READY status
- Both resources must belong to authenticated user

**Request:**
```json
{
  "upload_id": "123e4567-e89b-12d3-a456-426614174000",
  "job_id": "123e4567-e89b-12d3-a456-426614174001"
}
```

**Response:**
```json
{
  "plan_id": "123e4567-e89b-12d3-a456-426614174002",
  "patch": [
    {
      "id": "experience_1_bullet_1",
      "action": "EDIT",
      "suggested_text": "Developed scalable web applications using Python and React",
      "rationale": "Emphasize technologies mentioned in job requirements"
    }
  ],
  "status": "READY",
  "created_at": "2024-01-15T10:30:00Z",
  "upload_id": "123e4567-e89b-12d3-a456-426614174000",
  "job_id": "123e4567-e89b-12d3-a456-426614174001"
}
```

#### `GET /v1/tailor/plan/{plan_id}`
Retrieve a previously created patch plan.

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run API Tests Only
```bash
pytest backend/api/tests/
```

### Run Specific Test Categories
```bash
# Unit tests
pytest backend/api/tests/test_uploads.py

# Integration tests  
pytest backend/api/tests/test_integration.py
```

### Test Coverage
```bash
pytest --cov=backend.api backend/api/tests/
```

## 🔧 Architecture

### File Structure
```
backend/api/
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic models and schemas
├── auth.py              # JWT authentication
├── exceptions.py        # Error handling and custom exceptions
├── jobs.py              # Background job placeholders (Celery)
├── routers/
│   ├── __init__.py
│   ├── uploads.py       # Resume upload endpoints
│   ├── jobs.py          # Job scraping endpoints
│   └── tailor.py        # Patch plan endpoints
├── tests/
│   ├── __init__.py
│   ├── test_uploads.py  # Upload endpoint tests
│   └── test_integration.py  # End-to-end workflow tests
├── run_server.py        # Development server script
└── README.md           # This file
```

### Technology Stack
- **Web Framework**: FastAPI
- **Authentication**: JWT tokens with python-jose
- **Background Jobs**: Celery with Redis broker
- **Validation**: Pydantic models
- **Testing**: pytest with FastAPI TestClient
- **Documentation**: OpenAPI/Swagger auto-generation

### Architecture Integration
The API now properly integrates with the specialized backend modules:
- **`backend/parser`**: Handles PDF/DOCX resume parsing and text extraction
- **`backend/aggregator`**: Manages job posting scraping from various job boards
- **`backend/matcher`**: Provides AI-powered resume tailoring and matching logic

This separation of concerns ensures:
- **Maintainability**: Each module has a single responsibility
- **Testability**: Business logic can be tested independently of the API
- **Reusability**: Core functionality can be used in other contexts
- **Scalability**: Modules can be optimized and scaled independently

## 🚨 Current Limitations (Stage 1)

This is a **Stage 1 implementation** with the following limitations:

✅ **Business Logic Integration**
- Resume parsing now uses `backend/parser` module for actual PDF/DOCX processing
- Job scraping now uses `backend/aggregator` module for URL processing
- Patch plan generation now uses `backend/matcher` module for AI-powered suggestions

❌ **No Persistent Storage**
- All data stored in memory (will be lost on restart)
- No database integration yet

❌ **No Real Background Processing**
- Celery jobs are stubs that return immediately
- No actual file processing or web scraping

❌ **Basic Authentication**
- Uses demo JWT tokens
- No user registration or login system

## 🛠 Development Notes

### Adding New Endpoints
1. Define Pydantic models in `models.py`
2. Create router in `routers/` directory
3. Add router to `main.py`
4. Add tests in `tests/` directory

### Error Handling
All errors follow the unified format:
```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable message",
  "details": "Additional context (optional)"
}
```

### Background Jobs
Background jobs are implemented as Celery tasks in `jobs.py`. To add a new job:
1. Define the `@celery_app.task` function
2. Create an enqueue helper function
3. Call the enqueue function from your endpoint

### Testing Strategy
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows end-to-end
- **Contract Tests**: Ensure OpenAPI documentation is accurate

## 📈 Next Steps (Future Stages)

The following features will be implemented in future stages:

🔄 **Stage 2: Business Logic Implementation**
- Real resume parsing with existing parser
- Web scraping for job postings
- AI-powered patch plan generation

🔄 **Stage 3: Data Persistence**
- Database integration (PostgreSQL)
- User management system
- Data migration scripts

🔄 **Stage 4: Production Readiness**
- Redis/Celery setup for background jobs
- Rate limiting and security hardening
- Monitoring and logging
- Deployment configuration

---

**Happy coding! 🚀**
