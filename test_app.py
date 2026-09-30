import pytest

import db
from app import create_app


@pytest.fixture
def app(tmp_path):
    """An app that uses a brand-new database file in a temp folder."""
    return create_app(database_path=tmp_path / "test.db")


def test_home_shows_empty_message_when_no_notes(app):
    response = app.test_client().get("/")
    assert b"No notes yet." in response.data


def test_added_note_is_saved_and_shown(app):
    with app.app_context():
        db.add_note("Groceries", "Buy apples")

    response = app.test_client().get("/")
    assert b"Groceries" in response.data
    assert b"Buy apples" in response.data


def test_notes_come_back_newest_first(app):
    with app.app_context():
        db.add_note("First")
        db.add_note("Second")
        titles = [note["title"] for note in db.get_all_notes()]

    assert titles == ["Second", "First"]
