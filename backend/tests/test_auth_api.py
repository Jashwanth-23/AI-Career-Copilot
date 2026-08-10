"""Integration tests for Authentication API endpoints (/api/v1/auth/*).

Tests user registration, login, JWT token issuance, profile retrieval,
duplicate user rejection, and invalid credential handling.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.database.database import get_db
from app.models.user import User
from app.auth.password import hash_password

client = TestClient(app)


@pytest.fixture
def mock_db_session():
    db = MagicMock()
    return db


def test_register_user_success(mock_db_session):
    """Test successful user registration flow."""
    mock_db_session.scalar.return_value = None

    def mock_create_user(db, user_in):
        user = User(
            id=1,
            name=user_in.name,
            email=user_in.email,
            password=hash_password(user_in.password),
            created_at=datetime.now(timezone.utc),
        )
        return user

    app.dependency_overrides[get_db] = lambda: mock_db_session

    with patch("app.api.auth.create_user", side_effect=mock_create_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "name": "Jane Test",
                "email": "jane@example.com",
                "password": "Password123!",
            },
        )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "jane@example.com"
    assert data["name"] == "Jane Test"


def test_register_duplicate_email(mock_db_session):
    """Test registering with an email that already exists."""
    existing_user = User(id=1, name="Existing", email="jane@example.com", password="hash", created_at=datetime.now(timezone.utc))
    mock_db_session.scalar.return_value = existing_user

    app.dependency_overrides[get_db] = lambda: mock_db_session

    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Jane Duplicate",
            "email": "jane@example.com",
            "password": "Password123!",
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(mock_db_session):
    """Test user login with valid credentials."""
    hashed = hash_password("Secret123")
    user = User(id=2, name="Alice", email="alice@example.com", password=hashed, created_at=datetime.now(timezone.utc))
    mock_db_session.scalar.return_value = user

    app.dependency_overrides[get_db] = lambda: mock_db_session

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "Secret123"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(mock_db_session):
    """Test login with incorrect password."""
    hashed = hash_password("Secret123")
    user = User(id=2, name="Alice", email="alice@example.com", password=hashed, created_at=datetime.now(timezone.utc))
    mock_db_session.scalar.return_value = user

    app.dependency_overrides[get_db] = lambda: mock_db_session

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "WrongPassword"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]
