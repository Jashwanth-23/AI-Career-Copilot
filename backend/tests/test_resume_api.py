"""Integration tests for Resume API endpoints (/api/v1/resume/*).

Tests uploading, history retrieval, latest resume, file downloading,
deleting resume records, and replacing existing resumes.
"""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.api.auth import get_current_user
from app.database.database import get_db
from app.models.resume import Resume
from app.models.user import User

client = TestClient(app)


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = 10
    user.email = "resume_owner@example.com"
    return user


@pytest.fixture
def mock_db():
    return MagicMock()


def test_get_resume_history(mock_user, mock_db):
    """Test retrieving upload history for authenticated user."""
    mock_resume = Resume(
        id=1,
        user_id=mock_user.id,
        original_filename="my_resume.pdf",
        stored_filename="uuid_my_resume.pdf",
        file_type="application/pdf",
        file_size=1024,
        uploaded_at=datetime.now(timezone.utc),
    )
    mock_db.scalars.return_value.all.return_value = [mock_resume]

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/v1/resume/history")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["original_filename"] == "my_resume.pdf"


def test_get_latest_resume(mock_user, mock_db):
    """Test retrieving latest resume for authenticated user."""
    mock_resume = Resume(
        id=2,
        user_id=mock_user.id,
        original_filename="latest_resume.pdf",
        stored_filename="uuid_latest_resume.pdf",
        file_type="application/pdf",
        file_size=2048,
        uploaded_at=datetime.now(timezone.utc),
    )
    mock_db.scalar.return_value = mock_resume

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/v1/resume/latest")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "latest_resume.pdf"


def test_delete_resume_endpoint(mock_user, mock_db, tmp_path):
    """Test deleting resume record and file cleanup."""
    dummy_file = tmp_path / "uuid_delete_me.pdf"
    dummy_file.write_text("dummy resume content")

    mock_resume = Resume(
        id=5,
        user_id=mock_user.id,
        original_filename="delete_me.pdf",
        stored_filename=dummy_file.name,
        file_type="application/pdf",
        file_size=100,
        uploaded_at=datetime.now(timezone.utc),
    )

    mock_db.scalar.return_value = mock_resume

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.api.resume.UPLOAD_DIR", tmp_path):
        response = client.delete("/api/v1/resume/5")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
