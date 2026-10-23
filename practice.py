from datetime import date

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from auth import login_required
from db import get_db

practice = Blueprint("practice", __name__, url_prefix="/practice")


def parse_practice_date(value):
    try:
        practiced_at = date.fromisoformat(value) if value else date.today()
    except ValueError:
        return None
    if practiced_at > date.today():
        return None
    return practiced_at.isoformat()


def owned_record(table, record_id):
    if table not in {"practice_logs", "interview_topics"}:
        raise ValueError("Unsupported practice record table")
    record = get_db().execute(
        f"SELECT id FROM {table} WHERE id = ? AND user_id = ?",
        (record_id, g.user["id"]),
    ).fetchone()
    if record is None:
        abort(404)


@practice.route("/")
@login_required
def index():
    database = get_db()
    coding_logs = database.execute(
        "SELECT id, problem, topic, practiced_at FROM practice_logs WHERE user_id = ? ORDER BY practiced_at DESC, id DESC",
        (g.user["id"],),
    ).fetchall()
    interview_topics = database.execute(
        "SELECT id, topic, completed, practiced_at FROM interview_topics WHERE user_id = ? ORDER BY practiced_at DESC, id DESC",
        (g.user["id"],),
    ).fetchall()
    return render_template(
        "practice/index.html",
        coding_logs=coding_logs,
        interview_topics=interview_topics,
        today=date.today().isoformat(),
    )


@practice.route("/coding/add", methods=("POST",))
@login_required
def add_coding_log():
    problem = request.form.get("problem", "").strip()
    topic = request.form.get("topic", "").strip()
    practiced_at = parse_practice_date(request.form.get("practiced_at", ""))

    if not problem or len(problem) > 120:
        flash("Problem name is required and must be 120 characters or fewer.", "error")
    elif not topic or len(topic) > 80:
        flash("Topic is required and must be 80 characters or fewer.", "error")
    elif practiced_at is None:
        flash("Enter a valid practice date that is not in the future.", "error")
    else:
        database = get_db()
        database.execute(
            "INSERT INTO practice_logs (user_id, problem, topic, practiced_at) VALUES (?, ?, ?, ?)",
            (g.user["id"], problem, topic, practiced_at),
        )
        database.commit()
        flash("Solved problem recorded.", "success")
    return redirect(url_for("practice.index"))


@practice.route("/coding/<int:record_id>/delete", methods=("POST",))
@login_required
def delete_coding_log(record_id):
    owned_record("practice_logs", record_id)
    database = get_db()
    database.execute(
        "DELETE FROM practice_logs WHERE id = ? AND user_id = ?",
        (record_id, g.user["id"]),
    )
    database.commit()
    flash("Practice record removed.", "success")
    return redirect(url_for("practice.index"))


@practice.route("/interview/add", methods=("POST",))
@login_required
def add_interview_topic():
    topic = request.form.get("topic", "").strip()
    practiced_at = parse_practice_date(request.form.get("practiced_at", ""))
    completed = 1 if request.form.get("completed") == "on" else 0

    if not topic or len(topic) > 120:
        flash("Interview topic is required and must be 120 characters or fewer.", "error")
    elif practiced_at is None:
        flash("Enter a valid practice date that is not in the future.", "error")
    else:
        database = get_db()
        database.execute(
            "INSERT INTO interview_topics (user_id, topic, completed, practiced_at) VALUES (?, ?, ?, ?)",
            (g.user["id"], topic, completed, practiced_at),
        )
        database.commit()
        flash("Interview preparation topic added.", "success")
    return redirect(url_for("practice.index"))


@practice.route("/interview/<int:record_id>/toggle", methods=("POST",))
@login_required
def toggle_interview_topic(record_id):
    owned_record("interview_topics", record_id)
    database = get_db()
    database.execute(
        """
        UPDATE interview_topics
        SET completed = CASE completed WHEN 1 THEN 0 ELSE 1 END
        WHERE id = ? AND user_id = ?
        """,
        (record_id, g.user["id"]),
    )
    database.commit()
    flash("Interview topic status updated.", "success")
    return redirect(url_for("practice.index"))


@practice.route("/interview/<int:record_id>/delete", methods=("POST",))
@login_required
def delete_interview_topic(record_id):
    owned_record("interview_topics", record_id)
    database = get_db()
    database.execute(
        "DELETE FROM interview_topics WHERE id = ? AND user_id = ?",
        (record_id, g.user["id"]),
    )
    database.commit()
    flash("Interview topic removed.", "success")
    return redirect(url_for("practice.index"))
