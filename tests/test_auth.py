from werkzeug.security import check_password_hash

from db import get_db
from tests.conftest import csrf_token


def test_registration_validates_fields_and_hashes_password(app, client):
    token = csrf_token(client, "/auth/register")
    invalid = client.post(
        "/auth/register",
        data={
            "csrf_token": token,
            "username": "ab",
            "password": "short",
            "confirm_password": "different",
        },
    )
    assert b"Username must be" in invalid.data

    valid = client.post(
        "/auth/register",
        data={
            "csrf_token": token,
            "username": "ready_student",
            "password": "student-password-123",
            "confirm_password": "student-password-123",
        },
    )
    assert valid.status_code == 302
    with app.app_context():
        user = get_db().execute(
            "SELECT username, password_hash FROM users WHERE username = ?",
            ("ready_student",),
        ).fetchone()
    assert user["username"] == "ready_student"
    assert user["password_hash"] != "student-password-123"
    assert check_password_hash(user["password_hash"], "student-password-123")


def test_registration_rejects_duplicate_username_case_insensitively(client):
    token = csrf_token(client, "/auth/register")
    data = {
        "csrf_token": token,
        "username": "student",
        "password": "student-password-123",
        "confirm_password": "student-password-123",
    }
    assert client.post("/auth/register", data=data).status_code == 302
    data["username"] = "STUDENT"
    response = client.post("/auth/register", data=data, follow_redirects=True)
    assert b"already registered" in response.data


def test_login_logout_and_csrf_protection(client):
    token = csrf_token(client, "/auth/register")
    client.post(
        "/auth/register",
        data={
            "csrf_token": token,
            "username": "student",
            "password": "student-password-123",
            "confirm_password": "student-password-123",
        },
    )
    token = csrf_token(client, "/auth/login")
    invalid = client.post(
        "/auth/login",
        data={"csrf_token": token, "username": "student", "password": "incorrect"},
    )
    assert b"Invalid username or password" in invalid.data
    assert client.post("/auth/login", data={"username": "student", "password": "student-password-123"}).status_code == 400
    assert client.post(
        "/auth/login",
        data={"csrf_token": token, "username": "student", "password": "student-password-123"},
    ).location == "/dashboard"

    with client.session_transaction() as session:
        assert "user_id" in session
    token = csrf_token(client, "/auth/login")
    assert client.post("/auth/logout", data={"csrf_token": token}).status_code == 302
    with client.session_transaction() as session:
        assert "user_id" not in session


def test_dashboard_redirects_anonymous_visitors(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert response.location.endswith("/auth/login")
