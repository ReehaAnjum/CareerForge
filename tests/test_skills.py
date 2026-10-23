from db import get_db
from tests.conftest import csrf_token, register_and_login


def test_student_can_create_edit_and_delete_skills(app, client):
    register_and_login(client, "student_a")
    token = csrf_token(client, "/skills/")
    created = client.post(
        "/skills/create",
        data={"csrf_token": token, "name": "Python", "category": "Programming", "level": "3"},
    )
    assert created.status_code == 302
    assert b"Python" in client.get("/skills/").data

    with app.app_context():
        skill_id = get_db().execute("SELECT id FROM skills WHERE name = ?", ("Python",)).fetchone()["id"]
    edit_path = f"/skills/{skill_id}/edit"
    invalid = client.post(
        edit_path,
        data={"csrf_token": csrf_token(client, edit_path), "name": "Python", "category": "", "level": "6"},
    )
    assert b"Choose a proficiency rating" in invalid.data
    updated = client.post(
        edit_path,
        data={"csrf_token": csrf_token(client, edit_path), "name": "Python 3", "category": "Programming", "level": "4"},
    )
    assert updated.status_code == 302
    assert b"Python 3" in client.get("/skills/").data

    assert client.post(
        f"/skills/{skill_id}/delete",
        data={"csrf_token": csrf_token(client, "/skills/")},
    ).status_code == 302
    assert b"No skills yet" in client.get("/skills/").data


def test_skills_reject_duplicate_names_and_another_students_access(app, client):
    register_and_login(client, "student_a")
    token = csrf_token(client, "/skills/")
    client.post("/skills/create", data={"csrf_token": token, "name": "Python", "category": "", "level": "2"})
    duplicate = client.post(
        "/skills/create",
        data={"csrf_token": csrf_token(client, "/skills/"), "name": "Python", "category": "", "level": "3"},
        follow_redirects=True,
    )
    assert b"already added" in duplicate.data
    with app.app_context():
        skill_id = get_db().execute("SELECT id FROM skills WHERE name = ?", ("Python",)).fetchone()["id"]

    other_student = app.test_client()
    register_and_login(other_student, "student_b")
    assert other_student.get(f"/skills/{skill_id}/edit").status_code == 404
    assert other_student.post(
        f"/skills/{skill_id}/delete",
        data={"csrf_token": csrf_token(other_student, "/skills/")},
    ).status_code == 404

    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM skills").fetchone()[0] == 1
