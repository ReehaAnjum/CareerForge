from flask import Blueprint, current_app, g, render_template

from auth import login_required
from db import get_db
from readiness import calculate_readiness

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
@login_required
def index():
    database = get_db()
    student_skills = database.execute(
        "SELECT id, name, category, level FROM skills WHERE user_id = ? ORDER BY level, name COLLATE NOCASE",
        (g.user["id"],),
    ).fetchall()
    coding_logs = database.execute(
        "SELECT problem, topic, practiced_at FROM practice_logs WHERE user_id = ? ORDER BY practiced_at DESC, id DESC",
        (g.user["id"],),
    ).fetchall()
    interview_topics = database.execute(
        "SELECT topic, completed, practiced_at FROM interview_topics WHERE user_id = ? ORDER BY practiced_at DESC, id DESC",
        (g.user["id"],),
    ).fetchall()

    weights = dict(current_app.config["READINESS_WEIGHTS"])
    target = current_app.config["CODING_TARGET"]
    readiness = calculate_readiness(
        [skill["level"] for skill in student_skills],
        len(coding_logs),
        len(interview_topics),
        sum(topic["completed"] for topic in interview_topics),
        weights,
        target,
    )
    suggestions = []
    if not student_skills:
        suggestions.append(("Add your first technical skill.", "skills.index"))
    elif readiness["skills"] < 70:
        suggestions.append(("Strengthen your foundations in your lowest-rated skills.", "skills.index"))
    if readiness["coding"] < 70:
        suggestions.append(("Solve and record coding problems consistently.", "practice.index"))
    if readiness["interview"] < 70:
        suggestions.append(("Practise interview topics and mark them prepared when ready.", "practice.index"))
    if not suggestions:
        suggestions.append(("Great momentum—keep your preparation consistent.", "practice.index"))

    return render_template(
        "dashboard.html",
        readiness=readiness,
        weights=weights,
        coding_target=target,
        skills=student_skills,
        coding_logs=coding_logs[:5],
        interview_topics=interview_topics[:5],
        solved_count=len(coding_logs),
        interview_completed=sum(topic["completed"] for topic in interview_topics),
        suggestions=suggestions,
    )
