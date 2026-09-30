from pathlib import Path

from flask import Flask, render_template

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
