import sqlite3

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from auth import login_required
from db import get_db

skills = Blueprint("skills", __name__, url_prefix="/skills")


def parse_skill_form():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    try:
        level = int(request.form.get("level", ""))
    except ValueError:
        return None, "Choose a proficiency rating from 1 to 5."

    if not name or len(name) > 80:
        return None, "Skill name is required and must be 80 characters or fewer."
    if len(category) > 60:
        return None, "Category must be 60 characters or fewer."
    if not 1 <= level <= 5:
        return None, "Choose a proficiency rating from 1 to 5."
    return {"name": name, "category": category, "level": level}, None


def get_owned_skill(skill_id):
    skill = get_db().execute(
        "SELECT id, name, category, level FROM skills WHERE id = ? AND user_id = ?",
        (skill_id, g.user["id"]),
    ).fetchone()
    if skill is None:
        abort(404)
    return skill


@skills.route("/")
@login_required
def index():
    student_skills = get_db().execute(
        "SELECT id, name, category, level FROM skills WHERE user_id = ? ORDER BY name COLLATE NOCASE",
        (g.user["id"],),
    ).fetchall()
    return render_template("skills/index.html", skills=student_skills)


@skills.route("/create", methods=("POST",))
@login_required
def create():
    skill, error = parse_skill_form()
    if error:
        flash(error, "error")
    else:
        database = get_db()
        try:
            database.execute(
                "INSERT INTO skills (user_id, name, category, level) VALUES (?, ?, ?, ?)",
                (g.user["id"], skill["name"], skill["category"], skill["level"]),
            )
            database.commit()
        except sqlite3.IntegrityError:
            database.rollback()
            flash("You have already added that skill.", "error")
        else:
            flash("Skill added to your profile.", "success")
    return redirect(url_for("skills.index"))


@skills.route("/<int:skill_id>/edit", methods=("GET", "POST"))
@login_required
def edit(skill_id):
    skill = get_owned_skill(skill_id)
    if request.method == "POST":
        updated, error = parse_skill_form()
        if error:
            flash(error, "error")
        else:
            database = get_db()
            try:
                database.execute(
                    "UPDATE skills SET name = ?, category = ?, level = ? WHERE id = ? AND user_id = ?",
                    (updated["name"], updated["category"], updated["level"], skill_id, g.user["id"]),
                )
                database.commit()
            except sqlite3.IntegrityError:
                database.rollback()
                flash("You have already added another skill with that name.", "error")
            else:
                flash("Skill updated.", "success")
                return redirect(url_for("skills.index"))
    return render_template("skills/edit.html", skill=skill)


@skills.route("/<int:skill_id>/delete", methods=("POST",))
@login_required
def delete(skill_id):
    get_owned_skill(skill_id)
    database = get_db()
    database.execute(
        "DELETE FROM skills WHERE id = ? AND user_id = ?",
        (skill_id, g.user["id"]),
    )
    database.commit()
    flash("Skill removed.", "success")
    return redirect(url_for("skills.index"))
