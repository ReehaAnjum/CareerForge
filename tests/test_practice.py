from datetime import date, timedelta

from db import get_db
from tests.conftest import csrf_token, register_and_login


def test_coding_practice_records_dates_and_rejects_future(app, client):
    register_and_login(client, "student_a")
    token = csrf_token(client, "/practice/")
    invalid = client.post(
        "/practice/coding/add",
        data={"csrf_token": token, "problem": "Future problem", "topic": "Arrays", "practiced_at": "2999-01-01"},
        follow_redirects=True,
    )
    assert b"not in the future" in invalid.data

    expected_date = (date.today() - timedelta(days=3)).isoformat()
    added = client.post(
        "/practice/coding/add",
        data={"csrf_token": csrf_token(client, "/practice/"), "problem": "Two Sum", "topic": "Arrays", "practiced_at": expected_date},
        follow_redirects=True,
    )
    assert b"Two Sum" in added.data
    assert expected_date.encode() in added.data
    with app.app_context():
        row = get_db().execute(
            "SELECT problem, topic, practiced_at FROM practice_logs WHERE user_id = ?",
            (1,),
        ).fetchone()
    assert tuple(row) == ("Two Sum", "Arrays", expected_date)


def test_interview_topics_can_be_completed_and_removed(app, client):
    register_and_login(client, "student_a")
    added = client.post(
        "/practice/interview/add",
        data={"csrf_token": csrf_token(client, "/practice/"), "topic": "Behavioral questions", "practiced_at": date.today().isoformat()},
        follow_redirects=True,
    )
    assert b"In progress" in added.data
    with app.app_context():
        topic_id = get_db().execute("SELECT id FROM interview_topics").fetchone()["id"]
    completed = client.post(
        f"/practice/interview/{topic_id}/toggle",
        data={"csrf_token": csrf_token(client, "/practice/")},
        follow_redirects=True,
    )
    assert b"Prepared" in completed.data
    assert client.post(
        f"/practice/interview/{topic_id}/delete",
        data={"csrf_token": csrf_token(client, "/practice/")},
    ).status_code == 302


def test_practice_records_are_private_to_their_student(app, client):
    register_and_login(client, "student_a")
    client.post(
        "/practice/coding/add",
        data={"csrf_token": csrf_token(client, "/practice/"), "problem": "Private problem", "topic": "Arrays", "practiced_at": date.today().isoformat()},
    )
    with app.app_context():
        record_id = get_db().execute("SELECT id FROM practice_logs").fetchone()["id"]
    other_student = app.test_client()
    register_and_login(other_student, "student_b")
    response = other_student.post(
        f"/practice/coding/{record_id}/delete",
        data={"csrf_token": csrf_token(other_student, "/practice/")},
    )
    assert response.status_code == 404
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM practice_logs").fetchone()[0] == 1


def test_interview_topics_are_private_to_their_student(app, client):
    register_and_login(client, "student_a")
    client.post(
        "/practice/interview/add",
        data={"csrf_token": csrf_token(client, "/practice/"), "topic": "Private interview topic", "practiced_at": date.today().isoformat()},
    )
    with app.app_context():
        topic_id = get_db().execute("SELECT id FROM interview_topics").fetchone()["id"]
    other_student = app.test_client()
    register_and_login(other_student, "student_b")
    response = other_student.post(
        f"/practice/interview/{topic_id}/toggle",
        data={"csrf_token": csrf_token(other_student, "/practice/")},
    )
    assert response.status_code == 404
    with app.app_context():
        completed = get_db().execute("SELECT completed FROM interview_topics").fetchone()["completed"]
    assert completed == 0
