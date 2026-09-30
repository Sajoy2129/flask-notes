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


def test_new_note_page_shows_form(app):
    response = app.test_client().get("/notes/new")
    assert response.status_code == 200
    assert b"<form" in response.data


def test_submitting_form_saves_note_and_redirects(app):
    client = app.test_client()
    response = client.post(
        "/notes/new", data={"title": "From the form", "body": "Hello"}
    )

    # 302 = "go to another page"; it should send us back home
    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert b"From the form" in client.get("/").data


def test_empty_title_shows_error_and_saves_nothing(app):
    client = app.test_client()
    response = client.post("/notes/new", data={"title": "   ", "body": "x"})

    assert response.status_code == 400
    assert b"Title is required." in response.data
    with app.app_context():
        assert db.get_all_notes() == []


def test_note_page_shows_the_note(app):
    with app.app_context():
        note_id = db.add_note("My note", "Some details")

    response = app.test_client().get(f"/notes/{note_id}")
    assert response.status_code == 200
    assert b"My note" in response.data
    assert b"Some details" in response.data


def test_missing_note_returns_404(app):
    response = app.test_client().get("/notes/999")
    assert response.status_code == 404


def test_delete_removes_note_and_redirects(app):
    with app.app_context():
        note_id = db.add_note("Delete me")

    response = app.test_client().post(f"/notes/{note_id}/delete")

    assert response.status_code == 302
    with app.app_context():
        assert db.get_note(note_id) is None


def test_delete_does_not_work_with_get(app):
    with app.app_context():
        note_id = db.add_note("Keep me")

    response = app.test_client().get(f"/notes/{note_id}/delete")

    # 405 = "Method Not Allowed"; the note must still exist
    assert response.status_code == 405
    with app.app_context():
        assert db.get_note(note_id) is not None
