import sqlite3

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    database = g.pop("db", None)
    if database is not None:
        database.close()


def init_db():
    database = get_db()
    database.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL COLLATE NOCASE UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT '',
            level INTEGER NOT NULL DEFAULT 1 CHECK (level BETWEEN 1 AND 5),
            UNIQUE (user_id, name)
        );
        CREATE TABLE IF NOT EXISTS practice_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
            problem TEXT NOT NULL,
            topic TEXT NOT NULL,
            practiced_at TEXT NOT NULL DEFAULT CURRENT_DATE
        );
        CREATE TABLE IF NOT EXISTS interview_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
            topic TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
            practiced_at TEXT NOT NULL DEFAULT CURRENT_DATE
        );
        """
    )
    database.commit()
