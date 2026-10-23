import hmac
import re
import sqlite3
from functools import wraps

from flask import (
    Blueprint,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db

auth = Blueprint("auth", __name__, url_prefix="/auth")
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


@auth.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, username FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    if request.method == "POST":
        expected = session.get("csrf_token", "")
        submitted = request.form.get("csrf_token", "")
        if not expected or not hmac.compare_digest(expected, submitted):
            abort(400, description="Invalid form token. Please reload the page and try again.")


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


@auth.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirm_password", "")
        error = None

        if not USERNAME_PATTERN.fullmatch(username):
            error = "Username must be 3–32 letters, numbers, or underscores."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif password != confirmation:
            error = "Passwords do not match."

        if error is None:
            try:
                database = get_db()
                database.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                database.commit()
            except sqlite3.IntegrityError:
                database.rollback()
                error = "That username is already registered."
            else:
                flash("Account created. You can now sign in.", "success")
                return redirect(url_for("auth.login"))

        flash(error, "error")

    return render_template("auth/register.html")


@auth.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth.route("/logout", methods=("POST",))
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("index"))
