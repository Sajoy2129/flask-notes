import pytest

import db
from app import create_app, format_date


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


def test_edit_page_shows_form_filled_with_note(app):
    with app.app_context():
        note_id = db.add_note("Old title", "Old body")

    response = app.test_client().get(f"/notes/{note_id}/edit")

    assert response.status_code == 200
    assert b'value="Old title"' in response.data
    assert b"Old body" in response.data


def test_editing_note_saves_changes_and_redirects(app):
    with app.app_context():
        note_id = db.add_note("Old title", "Old body")

    response = app.test_client().post(
        f"/notes/{note_id}/edit", data={"title": "New title", "body": "New body"}
    )

    # After saving we should land back on the note's own page
    assert response.status_code == 302
    assert response.headers["Location"] == f"/notes/{note_id}"
    with app.app_context():
        note = db.get_note(note_id)
        assert note["title"] == "New title"
        assert note["body"] == "New body"


def test_edit_with_empty_title_shows_error_and_keeps_old_note(app):
    with app.app_context():
        note_id = db.add_note("Keep this title")

    response = app.test_client().post(
        f"/notes/{note_id}/edit", data={"title": "  ", "body": "x"}
    )

    assert response.status_code == 400
    assert b"Title is required." in response.data
    with app.app_context():
        assert db.get_note(note_id)["title"] == "Keep this title"


def test_editing_missing_note_returns_404(app):
    client = app.test_client()
    assert client.get("/notes/999/edit").status_code == 404
    assert client.post("/notes/999/edit", data={"title": "x"}).status_code == 404


def test_search_shows_only_matching_titles(app):
    with app.app_context():
        db.add_note("Buy milk")
        db.add_note("Call mom")

    response = app.test_client().get("/?q=milk")

    assert b"Buy milk" in response.data
    assert b"Call mom" not in response.data


def test_search_ignores_upper_and_lower_case(app):
    with app.app_context():
        db.add_note("Learn Flask")
        titles = [note["title"] for note in db.search_notes("flask")]

    assert titles == ["Learn Flask"]


def test_search_only_looks_at_titles_not_body(app):
    with app.app_context():
        db.add_note("Shopping", "milk and eggs")
        assert db.search_notes("milk") == []


def test_search_with_no_matches_shows_message(app):
    with app.app_context():
        db.add_note("Something")

    response = app.test_client().get("/?q=zzz")

    assert b"No notes match your search." in response.data


def test_empty_search_shows_all_notes(app):
    with app.app_context():
        db.add_note("One")
        db.add_note("Two")

    response = app.test_client().get("/?q=+")  # "+" is a space in a URL

    assert b"One" in response.data
    assert b"Two" in response.data


def test_format_date_turns_timestamp_into_readable_date():
    assert format_date("2026-09-30 14:05:12") == "30 Sep 2026"


def set_created_at(note_id, timestamp):
    """Test helper: give a note a fixed creation time."""
    connection = db.get_db()
    connection.execute(
        "UPDATE notes SET created_at = ? WHERE id = ?", (timestamp, note_id)
    )
    connection.commit()


def test_home_and_note_pages_show_created_date(app):
    with app.app_context():
        note_id = db.add_note("Dated note")
        set_created_at(note_id, "2025-01-15 09:30:00")

    client = app.test_client()
    assert b"15 Jan 2025" in client.get("/").data
    assert b"Created 15 Jan 2025" in client.get(f"/notes/{note_id}").data


def test_pages_link_the_stylesheet_and_it_is_served(app):
    client = app.test_client()
    assert b"/static/style.css" in client.get("/").data

    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert b"body" in response.data
    response.close()  # Flask streams static files; close to free the file
