import re

import pytest

from app import create_app
from db import init_db


@pytest.fixture
def app(tmp_path):
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "pytest-only-secret",
            "DATABASE": str(tmp_path / "careerforge-test.sqlite"),
            "READINESS_WEIGHTS": {"skills": 0.40, "coding": 0.35, "interview": 0.25},
            "CODING_TARGET": 20,
        }
    )
    with application.app_context():
        init_db()
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


def csrf_token(client, path):
    response = client.get(path)
    match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
    assert match is not None, f"Expected a CSRF token in {path}"
    return match.group(1).decode()


def register_and_login(client, username):
    token = csrf_token(client, "/auth/register")
    response = client.post(
        "/auth/register",
        data={
            "csrf_token": token,
            "username": username,
            "password": "student-password-123",
            "confirm_password": "student-password-123",
        },
    )
    assert response.status_code == 302
    token = csrf_token(client, "/auth/login")
    response = client.post(
        "/auth/login",
        data={
            "csrf_token": token,
            "username": username,
            "password": "student-password-123",
        },
    )
    assert response.status_code == 302
    return client
