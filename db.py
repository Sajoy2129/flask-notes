"""Everything that talks to the SQLite database lives in this file."""

import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_db():
    """Return the database connection for the current request.

    Flask's `g` object stores data for one request, so the connection is
    opened once and reused if we call get_db() several times.
    """
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        # Return rows that work like dicts: row["title"] instead of row[1]
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    """Close the connection when the request is finished."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the tables described in schema.sql (safe to run many times)."""
    db = get_db()
    db.executescript(SCHEMA_PATH.read_text())


def get_all_notes():
    """Return every note, newest first."""
    db = get_db()
    return db.execute(
        "SELECT id, title, body, created_at FROM notes ORDER BY id DESC"
    ).fetchall()


def add_note(title, body=""):
    """Save a new note and return its id."""
    db = get_db()
    # The ? placeholders let sqlite3 insert the values safely.
    # Never build SQL with f-strings from user input (SQL injection!).
    cursor = db.execute(
        "INSERT INTO notes (title, body) VALUES (?, ?)",
        (title, body),
    )
    db.commit()  # Save the change to the file on disk
    return cursor.lastrowid


def init_app(app):
    """Hook the database into a Flask app."""
    # Run close_db automatically after every request
    app.teardown_appcontext(close_db)
    # Make sure the table exists before the app handles any request
    with app.app_context():
        init_db()
