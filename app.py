from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

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
