"""Unit and Integration Tests for Skill Gap Analysis Module

Tests skill gap evaluation algorithms, role taxonomy resolutions,
service layer orchestration, and API endpoint POST /api/v1/resume/skill-gap/{resume_id}.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import pytest

from app.ai.skill_gap_engine import (
    InvalidTargetRoleError,
    evaluate_skill_gap,
    resolve_target_role,
)
from app.api.auth import get_current_user
from app.database.database import get_db
from app.main import app
from app.models.user import User


@pytest.fixture
def sample_structured_resume():
    """Fixture providing a candidate resume with backend skills."""
    return {
        "personal_information": {"name": "Candidate Developer"},
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
        "experience": [
            {
                "company": "Tech Corp",
                "position": "Backend Developer",
                "technologies": ["Python", "FastAPI", "REST API"],
            }
        ],
        "projects": [
            {
                "name": "API Service",
                "technologies": ["PostgreSQL", "Docker"],
            }
        ],
    }


@pytest.fixture
def mock_user():
    """Fixture providing a mock authenticated User."""
    user = MagicMock(spec=User)
    user.id = 20
    user.email = "candidate@example.com"
    return user


@pytest.fixture
def mock_db():
    """Fixture providing a mock database session."""
    return MagicMock()


def test_resolve_target_role():
    """Test target role resolution and case-insensitive alias matching."""
    assert resolve_target_role("Backend Developer") == "Backend Developer"
    assert resolve_target_role("backend engineer") == "Backend Developer"
    assert resolve_target_role("AI Engineer") == "AI Engineer"
    assert resolve_target_role("ml engineer") == "AI Engineer"

    with pytest.raises(InvalidTargetRoleError):
        resolve_target_role("Quantum Rocket Scientist")


def test_evaluate_skill_gap(sample_structured_resume):
    """Test evaluate_skill_gap outputs exact required JSON keys and structure."""
    result = evaluate_skill_gap(sample_structured_resume, "Backend Developer")

    assert result["target_role"] == "Backend Developer"
    assert isinstance(result["matched_skills"], list)
    assert isinstance(result["missing_skills"], list)
    assert isinstance(result["recommended_skills"], list)
    assert isinstance(result["priority_learning_order"], list)
    assert isinstance(result["match_percentage"], int)
    assert 0 <= result["match_percentage"] <= 100

    # Verify python, fastapi, postgresql are matched
    matched_lower = [s.lower() for s in result["matched_skills"]]
    assert "python" in matched_lower
    assert "fastapi" in matched_lower


def test_skill_gap_api_endpoint_success(mock_user, mock_db, sample_structured_resume):
    """Test POST /api/v1/resume/skill-gap/{resume_id} API endpoint returning complete skill gap response."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)

    mock_service_result = {
        "status": "success",
        "resume_id": 50,
        "user_id": 20,
        "original_filename": "candidate_resume.pdf",
        "skill_gap": {
            "target_role": "Backend Developer",
            "matched_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "missing_skills": ["Redis", "Celery", "gRPC"],
            "recommended_skills": ["Kafka", "Kubernetes"],
            "match_percentage": 65,
            "priority_learning_order": ["Redis", "Celery", "gRPC"],
        },
    }

    with patch(
        "app.api.skill_gap.analyze_resume_skill_gap", return_value=mock_service_result
    ):
        response = client.post(
            "/api/v1/resume/skill-gap/50", json={"target_role": "Backend Developer"}
        )
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["status"] == "success"
        assert json_data["resume_id"] == 50
        assert json_data["skill_gap"]["target_role"] == "Backend Developer"
        assert json_data["skill_gap"]["match_percentage"] == 65

    app.dependency_overrides.clear()


def test_skill_gap_api_endpoint_invalid_role(mock_user, mock_db):
    """Test POST /api/v1/resume/skill-gap/{resume_id} returns 400 for unsupported target role."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)

    with patch(
        "app.api.skill_gap.analyze_resume_skill_gap",
        side_effect=InvalidTargetRoleError("Target role 'Unknown' is not supported."),
    ):
        response = client.post(
            "/api/v1/resume/skill-gap/50", json={"target_role": "Unknown Role"}
        )
        assert response.status_code == 400
        assert "not supported" in response.json()["detail"]

    app.dependency_overrides.clear()
