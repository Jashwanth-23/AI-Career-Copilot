"""Unit and Integration Tests for AI Resume Analysis Module

Tests resume validation, text extraction, Gemini AI parsing orchestration,
exception handling, and API endpoint POST /api/v1/resume/analyze/{resume_id}.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import fitz
import pytest

from app.api.auth import get_current_user
from app.database.database import get_db
from app.main import app
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume_analysis import (
    PersonalInformationSchema,
    StructuredResumeSchema,
)
from app.services.resume_analysis_service import (
    ResumeAnalysisFailedError,
    ResumeFileNotFoundError,
    ResumeNotFoundError,
    analyze_resume,
    build_analysis_result,
    validate_resume,
)


@pytest.fixture
def mock_user():
    """Fixture providing a mock authenticated User object."""
    user = MagicMock(spec=User)
    user.id = 101
    user.email = "architect@example.com"
    return user


@pytest.fixture
def mock_db():
    """Fixture providing a mock SQLAlchemy Database Session."""
    return MagicMock()


@pytest.fixture
def sample_pdf_path(tmp_path):
    """Fixture creating a temporary PDF resume document."""
    pdf_file = tmp_path / "sample_resume.pdf"
    pdf_doc = fitz.open()
    page = pdf_doc.new_page()
    page.insert_text(
        (50, 50),
        "John Senior Engineer\nEmail: john@example.com\nSkills: Python, FastAPI, Docker",
    )
    pdf_doc.save(str(pdf_file))
    pdf_doc.close()
    return pdf_file


def test_validate_resume_success(mock_db, sample_pdf_path, tmp_path):
    """Test validate_resume helper returns Resume model and disk path when valid."""
    mock_resume = MagicMock(spec=Resume)
    mock_resume.id = 1
    mock_resume.user_id = 101
    mock_resume.original_filename = "sample_resume.pdf"
    mock_resume.stored_filename = sample_pdf_path.name

    mock_db.scalar.return_value = mock_resume

    with patch(
        "app.services.resume_analysis_service.UPLOAD_DIR", sample_pdf_path.parent
    ):
        res, path = validate_resume(mock_db, resume_id=1, user_id=101)
        assert res.id == 1
        assert path == sample_pdf_path


def test_validate_resume_not_found(mock_db):
    """Test validate_resume raises ResumeNotFoundError if DB record is missing."""
    mock_db.scalar.return_value = None
    with pytest.raises(ResumeNotFoundError):
        validate_resume(mock_db, resume_id=999, user_id=101)


def test_build_analysis_result():
    """Test build_analysis_result constructs standardized output structure."""
    mock_resume = MagicMock(spec=Resume)
    mock_resume.id = 5
    mock_resume.user_id = 101
    mock_resume.original_filename = "test.pdf"
    mock_resume.file_type = "application/pdf"
    mock_resume.file_size = 1024
    mock_resume.uploaded_at = None

    extracted = "Sample Text"
    structured = {"personal_information": {"name": "Alice"}, "skills": ["Python"]}

    result = build_analysis_result(mock_resume, extracted, structured)
    assert result["status"] == "success"
    assert result["resume_id"] == 5
    assert result["extracted_text"] == extracted
    assert result["structured_data"] == structured


def test_analyze_resume_service_success(mock_db, sample_pdf_path):
    """Test analyze_resume service orchestrates text extraction and AI parsing."""
    mock_resume = MagicMock(spec=Resume)
    mock_resume.id = 10
    mock_resume.user_id = 101
    mock_resume.original_filename = sample_pdf_path.name
    mock_resume.stored_filename = sample_pdf_path.name
    mock_resume.file_type = "application/pdf"
    mock_resume.file_size = sample_pdf_path.stat().st_size
    mock_resume.uploaded_at = None

    mock_db.scalar.return_value = mock_resume

    mock_structured = {
        "personal_information": {"name": "John Senior Engineer"},
        "skills": ["Python", "FastAPI", "Docker"],
    }

    with patch(
        "app.services.resume_analysis_service.UPLOAD_DIR", sample_pdf_path.parent
    ), patch(
        "app.services.resume_analysis_service.parse_resume_with_gemini",
        return_value=mock_structured,
    ):

        result = analyze_resume(mock_db, resume_id=10, user_id=101, api_key="fake-key")
        assert result["resume_id"] == 10
        assert "John Senior Engineer" in result["extracted_text"]
        assert result["structured_data"] == mock_structured


def test_analyze_resume_api_endpoint_success(mock_user, mock_db):
    """Test POST /api/v1/resume/analyze/{resume_id} API endpoint."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)

    mock_result = {
        "status": "success",
        "resume_id": 15,
        "user_id": 101,
        "original_filename": "resume.pdf",
        "file_type": "application/pdf",
        "file_size": 2048,
        "uploaded_at": "2026-08-06T12:00:00Z",
        "extracted_text": "Candidate Resume Text",
        "structured_data": {"personal_information": {"name": "Candidate"}},
        "analyzed_at": "2026-08-06T12:05:00Z",
    }

    with patch(
        "app.api.resume_analysis.analyze_resume", return_value=mock_result
    ):
        response = client.post("/api/v1/resume/analyze/15")
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["resume_id"] == 15
        assert json_data["structured_data"]["personal_information"]["name"] == "Candidate"

    app.dependency_overrides.clear()


def test_analyze_resume_api_endpoint_unauthorized_resume(mock_user, mock_db):
    """Test POST /api/v1/resume/analyze/{resume_id} returns 404 when resume not owned by user."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)

    with patch(
        "app.api.resume_analysis.analyze_resume",
        side_effect=ResumeNotFoundError("Resume not found"),
    ):
        response = client.post("/api/v1/resume/analyze/999")
        assert response.status_code == 404
        assert "was not found" in response.json()["detail"]

    app.dependency_overrides.clear()
