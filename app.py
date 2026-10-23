from pathlib import Path
import secrets

import click
from flask import Flask, redirect, render_template, session, url_for
from flask.cli import with_appcontext

from auth import auth
from dashboard import dashboard
from db import close_db, init_db
from practice import practice
from readiness import calculate_readiness
from skills import skills


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.Config")

    if test_config is not None:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = secrets.token_hex(32)
    calculate_readiness(
        [],
        0,
        0,
        0,
        app.config["READINESS_WEIGHTS"],
        app.config["CODING_TARGET"],
    )

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(skills)
    app.register_blueprint(practice)
    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.route("/")
    def index():
        if session.get("user_id") is not None:
            return redirect(url_for("dashboard.index"))
        return render_template("index.html")

    return app


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Create the application's SQLite tables."""
    init_db()
    click.echo("Initialized the database.")


app = create_app()


if __name__ == "__main__":
    app.run()
