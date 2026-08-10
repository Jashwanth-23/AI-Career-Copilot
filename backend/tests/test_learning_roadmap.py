"""Unit and Integration Tests for AI Learning Roadmap Module

Tests weekly curriculum generation, duration calculation, service orchestration,
and API endpoint POST /api/v1/resume/learning-roadmap/{resume_id}.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import pytest

from app.ai.learning_roadmap_engine import (
    generate_learning_roadmap,
    generate_skill_curriculum,
)
from app.api.auth import get_current_user
from app.database.database import get_db
from app.main import app
from app.models.user import User


@pytest.fixture
def mock_user():
    """Fixture providing a mock authenticated User."""
    user = MagicMock(spec=User)
    user.id = 30
    user.email = "learner@example.com"
    return user


@pytest.fixture
def mock_db():
    """Fixture providing a mock database session."""
    return MagicMock()


def test_generate_skill_curriculum():
    """Test generating weekly curriculum for a known skill."""
    curr = generate_skill_curriculum("Python", week_num=1)
    assert curr["week"] == 1
    assert curr["focus"] == "Python"
    assert isinstance(curr["topics"], list)
    assert len(curr["topics"]) > 0
    assert isinstance(curr["resources"], list)
    assert "mini_project" in curr
    assert "milestone" in curr


def test_generate_learning_roadmap():
    """Test generate_learning_roadmap builds valid roadmap payload."""
    structured = {"skills": ["Python", "FastAPI"]}
    ats_score = {"overall_score": 75}
    skill_gap = {
        "target_role": "Backend Developer",
        "match_percentage": 65,
        "priority_learning_order": ["Redis", "Celery", "Docker"],
        "missing_skills": ["Redis", "Celery"],
        "recommended_skills": ["Docker", "Kubernetes"],
    }

    result = generate_learning_roadmap(
        structured_data=structured,
        ats_score=ats_score,
        skill_gap=skill_gap,
        target_role="Backend Developer",
    )

    assert result["target_role"] == "Backend Developer"
    assert result["estimated_duration"] == "8 Weeks"
    assert result["overall_progress"] == 65
    assert isinstance(result["roadmap"], list)
    assert len(result["roadmap"]) == 8

    week_1 = result["roadmap"][0]
    assert week_1["week"] == 1
    assert "focus" in week_1
    assert "topics" in week_1
    assert "resources" in week_1
    assert "mini_project" in week_1
    assert "milestone" in week_1


def test_learning_roadmap_api_endpoint_success(mock_user, mock_db):
    """Test POST /api/v1/resume/learning-roadmap/{resume_id} API endpoint."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)

    mock_service_result = {
        "status": "success",
        "resume_id": 88,
        "user_id": 30,
        "original_filename": "learner_resume.pdf",
        "learning_roadmap": {
            "target_role": "Backend Developer",
            "estimated_duration": "8 Weeks",
            "overall_progress": 65,
            "roadmap": [
                {
                    "week": 1,
                    "focus": "Redis",
                    "topics": [
                        "In-Memory Data Structures",
                        "Caching Strategies",
                    ],
                    "resources": ["Redis University"],
                    "mini_project": "Build a Redis Rate Limiter Middleware",
                    "milestone": "Master Distributed In-Memory Caching",
                }
            ],
        },
    }

    with patch(
        "app.api.learning_roadmap.analyze_resume_learning_roadmap",
        return_value=mock_service_result,
    ):
        response = client.post(
            "/api/v1/resume/learning-roadmap/88",
            json={"target_role": "Backend Developer"},
        )
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["status"] == "success"
        assert json_data["resume_id"] == 88
        assert (
            json_data["learning_roadmap"]["target_role"] == "Backend Developer"
        )
        assert json_data["learning_roadmap"]["estimated_duration"] == "8 Weeks"
        assert len(json_data["learning_roadmap"]["roadmap"]) == 1

    app.dependency_overrides.clear()
