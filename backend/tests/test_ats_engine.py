"""Unit and Integration Tests for ATS Score Engine Module

Tests ATS sub-score calculations, feedback generation, service integration,
and API endpoint POST /api/v1/resume/ats/{resume_id}.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import pytest

from app.ai.ats_engine import (
    ATSAnalysisFailedError,
    calculate_completeness_score,
    calculate_education_score,
    calculate_experience_score,
    calculate_projects_score,
    calculate_skills_score,
    evaluate_ats_score,
)
from app.api.auth import get_current_user
from app.database.database import get_db
from app.main import app
from app.models.user import User


@pytest.fixture
def sample_structured_resume():
    """Fixture providing a realistic structured resume dictionary."""
    return {
        "personal_information": {
            "name": "Jane Architect",
            "email": "jane@example.com",
            "phone": "+1-555-0199",
            "location": "San Francisco, CA",
            "linkedin": "https://linkedin.com/in/janearchitect",
            "github": "https://github.com/janearchitect",
            "website": "https://janearchitect.dev",
        },
        "summary": "Senior AI Software Architect with 8+ years experience designing cloud systems.",
        "skills": [
            "Python",
            "FastAPI",
            "PostgreSQL",
            "Docker",
            "Kubernetes",
            "AWS",
            "React",
            "TypeScript",
            "GraphQL",
            "PyTorch",
            "Redis",
            "CI/CD",
        ],
        "experience": [
            {
                "company": "Tech Corp",
                "position": "Lead Engineer",
                "location": "San Francisco, CA",
                "start_date": "2021-01",
                "end_date": "Present",
                "description": [
                    "Architected microservices improving API latency by 45%.",
                    "Led a team of 10 engineers scaling system to 1M daily users.",
                ],
                "technologies": ["Python", "FastAPI", "Docker"],
            }
        ],
        "education": [
            {
                "institution": "Stanford University",
                "degree": "B.S.",
                "field_of_study": "Computer Science",
                "start_date": "2013",
                "end_date": "2017",
                "gpa": "3.9",
            }
        ],
        "projects": [
            {
                "name": "AI Career Copilot",
                "description": "SaaS AI tool for career advancement",
                "technologies": ["FastAPI", "React", "Gemini AI"],
                "link": "https://github.com/janearchitect/ai-copilot",
            }
        ],
        "certifications": ["AWS Certified Solutions Architect"],
        "languages": ["English"],
    }


@pytest.fixture
def mock_user():
    """Fixture providing a mock authenticated User."""
    user = MagicMock(spec=User)
    user.id = 10
    user.email = "jane@example.com"
    return user


@pytest.fixture
def mock_db():
    """Fixture providing a mock database session."""
    return MagicMock()


def test_sub_score_evaluators(sample_structured_resume):
    """Test individual sub-score calculation logic."""
    c_score, c_str, c_weak = calculate_completeness_score(
        sample_structured_resume
    )
    assert c_score >= 85
    assert len(c_str) > 0

    s_score, s_str, s_weak = calculate_skills_score(
        sample_structured_resume["skills"]
    )
    assert s_score >= 90

    exp_score, exp_str, exp_weak = calculate_experience_score(
        sample_structured_resume["experience"]
    )
    assert exp_score >= 80

    edu_score, edu_str, edu_weak = calculate_education_score(
        sample_structured_resume["education"]
    )
    assert edu_score >= 80

    proj_score, proj_str, proj_weak = calculate_projects_score(
        sample_structured_resume["projects"]
    )
    assert proj_score >= 80


def test_evaluate_ats_score(sample_structured_resume):
    """Test main evaluate_ats_score function produces valid score breakdown."""
    ats_result = evaluate_ats_score(sample_structured_resume)

    assert "overall_score" in ats_result
    assert 0 <= ats_result["overall_score"] <= 100
    assert ats_result["skills_score"] > 0
    assert ats_result["experience_score"] > 0
    assert ats_result["education_score"] > 0
    assert ats_result["projects_score"] > 0
    assert ats_result["completeness_score"] > 0
    assert isinstance(ats_result["strengths"], list)
    assert isinstance(ats_result["weaknesses"], list)
    assert isinstance(ats_result["improvement_suggestions"], list)


def test_evaluate_ats_score_invalid_input():
    """Test evaluate_ats_score raises ATSAnalysisFailedError on non-dict input."""
    with pytest.raises(ATSAnalysisFailedError):
        evaluate_ats_score("invalid text string")


def test_ats_api_endpoint_success(mock_user, mock_db, sample_structured_resume):
    """Test POST /api/v1/resume/ats/{resume_id} API endpoint returning complete ATS analysis."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)

    mock_service_result = {
        "status": "success",
        "resume_id": 42,
        "user_id": 10,
        "original_filename": "jane_resume.pdf",
        "ats_score": {
            "overall_score": 88,
            "skills_score": 95,
            "experience_score": 85,
            "education_score": 90,
            "projects_score": 85,
            "completeness_score": 92,
            "strengths": ["Strong technical skills section."],
            "weaknesses": [],
            "improvement_suggestions": [
                "Your resume meets high ATS standards!"
            ],
        },
        "structured_data": sample_structured_resume,
    }

    with patch(
        "app.api.ats.analyze_resume_ats", return_value=mock_service_result
    ):
        response = client.post("/api/v1/resume/ats/42")
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["status"] == "success"
        assert json_data["resume_id"] == 42
        assert json_data["ats_score"]["overall_score"] == 88
        assert json_data["ats_score"]["skills_score"] == 95

    app.dependency_overrides.clear()
