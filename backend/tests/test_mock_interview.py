"""Integration and unit tests for Mock Interview endpoints (/api/v1/interview/*).

Tests session creation, authorization, user data isolation, answer submission,
empty answer validation, report retrieval, history retrieval, deletion, and HTTP 429 quota handling.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest

from app.api.auth import get_current_user
from app.core.gemini_client import GeminiQuotaExhaustedError
from app.database.database import get_db
from app.main import app
from app.models.interview import InterviewQuestion, InterviewSession
from app.models.user import User

client = TestClient(app)


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = 42
    user.email = "interview_user@example.com"
    return user


@pytest.fixture
def mock_db():
    return MagicMock()


def test_start_interview_unauthorized():
    """Test start interview requires JWT authentication header."""
    response = client.post(
        "/api/v1/interview/start",
        json={
            "resume_id": 1,
            "target_role": "Backend Engineer",
            "interview_type": "technical",
            "difficulty": "medium",
            "total_questions": 3,
        },
    )
    assert response.status_code == 403 or response.status_code == 401


def test_start_interview_success(mock_user, mock_db):
    """Test starting a new interview session successfully."""
    mock_session = InterviewSession(
        id=101,
        user_id=mock_user.id,
        resume_id=1,
        target_role="Backend Engineer",
        interview_type="technical",
        difficulty="medium",
        total_questions=3,
        current_question_number=1,
        status="active",
        started_at=datetime.now(timezone.utc),
    )
    mock_q1 = InterviewQuestion(
        id=501,
        session_id=101,
        question_number=1,
        question_type="technical",
        difficulty="medium",
        topic="FastAPI",
        question_text="How do dependency injection systems work in FastAPI?",
    )

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.api.mock_interview.start_interview", return_value=(mock_session, mock_q1)):
        response = client.post(
            "/api/v1/interview/start",
            json={
                "resume_id": 1,
                "target_role": "Backend Engineer",
                "interview_type": "technical",
                "difficulty": "medium",
                "total_questions": 3,
            },
        )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    data = response.json()
    assert data["session_id"] == 101
    assert data["target_role"] == "Backend Engineer"
    assert data["current_question"]["question_text"] == "How do dependency injection systems work in FastAPI?"


def test_submit_answer_empty_validation(mock_user, mock_db):
    """Test submit answer rejects empty text input."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/api/v1/interview/session/101/answer",
        json={"answer": "   "},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 422


def test_submit_answer_success(mock_user, mock_db):
    """Test submitting answer evaluates answer and returns evaluation feedback."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    mock_eval = {
        "overall_score": 85,
        "technical_accuracy": 90,
        "relevance": 90,
        "completeness": 80,
        "clarity": 85,
        "communication": 85,
        "problem_solving": 80,
        "strengths": ["Good explanation of FastAPI Depends"],
        "weaknesses": [],
        "missing_points": [],
        "improvement": "Great job.",
        "ideal_answer": "Depends injects request-scoped services.",
        "follow_up_needed": False,
    }

    mock_service_return = {
        "evaluation": mock_eval,
        "next_question": {
            "id": 502,
            "question_number": 2,
            "question_type": "technical",
            "difficulty": "medium",
            "topic": "PostgreSQL",
            "question_text": "Explain database indexing.",
        },
        "question_number": 2,
        "total_questions": 3,
        "completed": False,
    }

    with patch("app.api.mock_interview.submit_answer", return_value=mock_service_return):
        response = client.post(
            "/api/v1/interview/session/101/answer",
            json={"answer": "FastAPI uses Depends() to manage request dependencies cleanly."},
        )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["evaluation"]["overall_score"] == 85
    assert data["completed"] is False
    assert data["next_question"]["question_text"] == "Explain database indexing."


def test_get_session_user_isolation(mock_user, mock_db):
    """Test user cannot access another user's session."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    from app.services.mock_interview_service import SessionNotFoundError

    with patch("app.api.mock_interview.get_session", side_effect=SessionNotFoundError("Session not found or access is denied.")):
        response = client.get("/api/v1/interview/session/999")

    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert "access is denied" in response.json()["detail"]


def test_get_report_success(mock_user, mock_db):
    """Test retrieving final performance report."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    mock_report = {
        "session_id": 101,
        "target_role": "Backend Engineer",
        "interview_type": "technical",
        "difficulty": "medium",
        "total_questions": 3,
        "overall_score": 88,
        "performance_rating": "Strong",
        "completed_at": "2026-08-13T00:00:00Z",
        "report": {
            "overall_score": 88,
            "technical_score": 90,
            "problem_solving_score": 85,
            "communication_score": 88,
            "role_readiness_score": 88,
            "performance_rating": "Strong",
            "strengths": ["Clear technical articulation"],
            "weaknesses": ["Deep dive into async locks"],
            "recommended_topics": ["Asyncio concurrency"],
            "final_feedback": "Excellent performance overall.",
            "action_plan": ["Review asyncio primitives"],
        },
    }

    with patch("app.api.mock_interview.get_report", return_value=mock_report):
        response = client.get("/api/v1/interview/session/101/report")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 88
    assert data["performance_rating"] == "Strong"


def test_get_history_success(mock_user, mock_db):
    """Test fetching user's interview history."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    mock_history_item = InterviewSession(
        id=101,
        resume_id=1,
        target_role="Backend Engineer",
        interview_type="technical",
        difficulty="medium",
        total_questions=3,
        status="completed",
        overall_score=88,
        performance_rating="Strong",
        started_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )

    with patch("app.api.mock_interview.get_user_history", return_value=[mock_history_item]):
        response = client.get("/api/v1/interview/history")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["target_role"] == "Backend Engineer"


def test_delete_interview_success(mock_user, mock_db):
    """Test deleting an interview session."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.api.mock_interview.delete_interview", return_value=True):
        response = client.delete("/api/v1/interview/session/101")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_gemini_429_quota_handling(mock_user, mock_db):
    """Test HTTP 429 quota error handling gracefully returns friendly message."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.api.mock_interview.start_interview", side_effect=GeminiQuotaExhaustedError("Quota exhausted")):
        response = client.post(
            "/api/v1/interview/start",
            json={
                "resume_id": 1,
                "target_role": "Backend Engineer",
                "interview_type": "technical",
                "difficulty": "medium",
                "total_questions": 3,
            },
        )

    app.dependency_overrides.clear()
    assert response.status_code == 429
    assert "temporarily unavailable due to quota limits" in response.json()["detail"]
