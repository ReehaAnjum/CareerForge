from datetime import date

from tests.conftest import csrf_token, register_and_login


def test_dashboard_has_empty_state_and_computes_student_specific_readiness(client):
    register_and_login(client, "dashboard_student")
    empty = client.get("/dashboard")
    assert empty.status_code == 200
    assert b"Add your first technical skill" in empty.data
    assert b"0</strong>" in empty.data

    token = csrf_token(client, "/skills/")
    client.post("/skills/create", data={"csrf_token": token, "name": "Python", "category": "Programming", "level": "4"})
    client.post("/skills/create", data={"csrf_token": csrf_token(client, "/skills/"), "name": "SQL", "category": "Data", "level": "3"})
    for number in range(10):
        client.post(
            "/practice/coding/add",
            data={
                "csrf_token": csrf_token(client, "/practice/"),
                "problem": f"Problem {number}",
                "topic": "Arrays",
                "practiced_at": date.today().isoformat(),
            },
        )
    for number in range(4):
        client.post(
            "/practice/interview/add",
            data={
                "csrf_token": csrf_token(client, "/practice/"),
                "topic": f"Interview topic {number}",
                "practiced_at": date.today().isoformat(),
                "completed": "on" if number < 2 else "",
            },
        )
    dashboard = client.get("/dashboard")
    assert b"58" in dashboard.data
    assert b"70%" in dashboard.data
    assert b"50%" in dashboard.data
    assert b"Python" in dashboard.data
    assert b"Problem 9" in dashboard.data


def test_dashboard_does_not_include_other_students_records(app, client):
    register_and_login(client, "student_a")
    client.post(
        "/skills/create",
        data={"csrf_token": csrf_token(client, "/skills/"), "name": "Secret skill", "category": "", "level": "5"},
    )
    other_student = app.test_client()
    register_and_login(other_student, "student_b")
    dashboard = other_student.get("/dashboard")
    assert b"Secret skill" not in dashboard.data
