"""Unit and Integration Tests for AI Job Recommendation Module

Tests job suitability evaluation across 10 tech roles, salary estimation,
service layer orchestration, and API endpoint POST /api/v1/resume/job-recommendations/{resume_id}.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import pytest

from app.ai.job_recommendation_engine import (
    evaluate_job_suitability,
    get_salary_estimate,
    recommend_jobs,
)
from app.api.auth import get_current_user
from app.database.database import get_db
from app.main import app
from app.models.user import User


@pytest.fixture
def sample_structured_resume():
    """Fixture providing a candidate resume."""
    return {
        "personal_information": {"name": "Candidate Engineer"},
        "skills": [
            "Python",
            "FastAPI",
            "PostgreSQL",
            "Docker",
            "React",
            "TypeScript",
            "Git",
        ],
        "experience": [
            {
                "company": "Tech Corp",
                "position": "Software Developer",
                "technologies": ["Python", "FastAPI", "React"],
            }
        ],
        "projects": [
            {
                "name": "Web Application",
                "technologies": ["React", "FastAPI"],
            }
        ],
    }


@pytest.fixture
def mock_user():
    """Fixture providing a mock authenticated User."""
    user = MagicMock(spec=User)
    user.id = 40
    user.email = "jobseeker@example.com"
    return user


@pytest.fixture
def mock_db():
    """Fixture providing a mock database session."""
    return MagicMock()


def test_get_salary_estimate():
    """Test salary estimation logic for different roles and experience tiers."""
    freshener_salary = get_salary_estimate("Backend Developer", "Fresher")
    assert "$60,000" in freshener_salary or "$75,000" in freshener_salary

    senior_salary = get_salary_estimate("AI Engineer", "Senior")
    assert "$160,000" in senior_salary or "$210,000" in senior_salary


def test_evaluate_job_suitability(sample_structured_resume):
    """Test evaluating job suitability for a specific role."""
    suitability = evaluate_job_suitability(
        sample_structured_resume, role="Backend Developer", experience_level="Fresher"
    )

    assert suitability["role"] == "Backend Developer"
    assert isinstance(suitability["match_percentage"], int)
    assert 0 <= suitability["match_percentage"] <= 100
    assert "salary_range" in suitability
    assert isinstance(suitability["strengths"], list)
    assert isinstance(suitability["missing_skills"], list)
    assert isinstance(suitability["recommendations"], list)


def test_recommend_jobs(sample_structured_resume):
    """Test recommend_jobs returns top 5 ranked job recommendations."""
    result = recommend_jobs(
        structured_data=sample_structured_resume,
        preferred_location="Remote",
        experience_level="Fresher",
        top_n=5,
    )

    assert "recommended_jobs" in result
    jobs = result["recommended_jobs"]
    assert len(jobs) == 5

    # Check ranking order (descending by match_percentage)
    for i in range(len(jobs) - 1):
        assert jobs[i]["match_percentage"] >= jobs[i + 1]["match_percentage"]

    # Verify standard output keys per recommended job item
    job_1 = jobs[0]
    assert "role" in job_1
    assert "match_percentage" in job_1
    assert "salary_range" in job_1
    assert "strengths" in job_1
    assert "missing_skills" in job_1
    assert "recommendations" in job_1


def test_job_recommendation_api_endpoint_success(mock_user, mock_db):
    """Test POST /api/v1/resume/job-recommendations/{resume_id} API endpoint."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)

    mock_service_result = {
        "status": "success",
        "resume_id": 99,
        "user_id": 40,
        "original_filename": "jobseeker_resume.pdf",
        "recommended_jobs": [
            {
                "role": "Backend Developer",
                "match_percentage": 85,
                "salary_range": "$60,000 - $80,000 / year",
                "strengths": [
                    "Demonstrated proficiency in Python, FastAPI, PostgreSQL"
                ],
                "missing_skills": ["Redis", "Celery"],
                "recommendations": [
                    "Prioritize learning Redis to optimize backend performance"
                ],
            }
        ],
    }

    with patch(
        "app.api.job_recommendation.analyze_resume_job_recommendations",
        return_value=mock_service_result,
    ):
        response = client.post(
            "/api/v1/resume/job-recommendations/99",
            json={"preferred_location": "Remote", "experience_level": "Fresher"},
        )
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["status"] == "success"
        assert json_data["resume_id"] == 99
        assert len(json_data["recommended_jobs"]) == 1
        assert json_data["recommended_jobs"][0]["role"] == "Backend Developer"

    app.dependency_overrides.clear()
