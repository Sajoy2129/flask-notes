from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for

import db


def create_app(database_path=None):
    """Build and configure the Flask app.

    Using a function (an "app factory") lets tests create an app that
    uses a throwaway database instead of the real one.
    """
    # __name__ tells Flask where this file lives,
    # so it can find templates and static files.
    app = Flask(__name__)
    app.config["DATABASE"] = database_path or Path(__file__).parent / "notes.db"
    db.init_app(app)

    # A route connects a URL to a Python function.
    # When someone visits "/" (the home page), Flask calls home()
    # and sends whatever it returns to the browser.
    @app.route("/")
    def home():
        return render_template("index.html", notes=db.get_all_notes())

    # This route accepts two methods:
    #   GET  -> show the empty form
    #   POST -> the form was submitted, so save the note
    @app.route("/notes/new", methods=["GET", "POST"])
    def new_note():
        if request.method == "POST":
            # request.form holds the fields the browser sent, by their name=""
            title = request.form.get("title", "").strip()
            body = request.form.get("body", "").strip()

            if not title:
                # Show the form again with an error, keeping what was typed
                return render_template(
                    "new_note.html",
                    error="Title is required.",
                    title=title,
                    body=body,
                ), 400

            db.add_note(title, body)
            # Send the browser to the home page (see "Post/Redirect/Get")
            return redirect(url_for("home"))

        return render_template("new_note.html")

    # <int:note_id> is a URL variable: /notes/3 calls show_note(note_id=3).
    # "int:" means only whole numbers match, so /notes/abc gives a 404.
    @app.route("/notes/<int:note_id>")
    def show_note(note_id):
        note = db.get_note(note_id)
        if note is None:
            abort(404)  # Stop here and send a "404 Not Found" page
        return render_template("note.html", note=note)

    # Works like new_note(), but starts from an existing note:
    #   GET  -> show the form filled in with the note's current text
    #   POST -> save the changes and go back to the note's page
    @app.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
    def edit_note(note_id):
        note = db.get_note(note_id)
        if note is None:
            abort(404)

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            body = request.form.get("body", "").strip()

            if not title:
                return render_template(
                    "edit_note.html",
                    note=note,
                    error="Title is required.",
                    title=title,
                    body=body,
                ), 400

            db.update_note(note_id, title, body)
            return redirect(url_for("show_note", note_id=note_id))

        return render_template(
            "edit_note.html", note=note, title=note["title"], body=note["body"]
        )

    # Deleting changes data, so this route only accepts POST.
    # A plain link (GET) can't trigger it by accident.
    @app.route("/notes/<int:note_id>/delete", methods=["POST"])
    def delete_note(note_id):
        if db.get_note(note_id) is None:
            abort(404)
        db.delete_note(note_id)
        return redirect(url_for("home"))

    # A command you can run in the terminal: flask --app app seed
    @app.cli.command("seed")
    def seed():
        """Add a few sample notes to the database."""
        db.add_note("Shopping list", "Milk, eggs, bread")
        db.add_note("Learn Flask", "Routes, templates, then SQLite")
        db.add_note("Idea", "Build a notes app <b>with</b> Flask")
        print("Added 3 sample notes.")

    return app


app = create_app()

# Start the development server only when this file is run directly
# (python app.py), not when another file imports it (e.g. tests).
if __name__ == "__main__":
    app.run(debug=True, port=5000)
