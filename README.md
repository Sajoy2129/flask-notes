# Flask Notes

A simple notes app built with [Flask](https://flask.palletsprojects.com/)
and SQLite, made as a learning project.

## Features

- Create, view, edit and delete notes
- Search notes by title
- Notes shown as a responsive grid of tiles with colored date chips
- Data saved in a local SQLite database (`notes.db`)

## Getting started

You need **Python 3** installed.

```bash
# 1. Get the code and go into the folder
git clone <your-repo-url>
cd flask-notes

# 2. Create a virtual environment and install the dependencies
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. (Optional) Add a few sample notes
flask --app app seed

# 4. Start the app
python app.py
```

Then open <http://127.0.0.1:5000> in your browser.

The database file `notes.db` is created automatically the first time the
app runs.

## Running the tests

```bash
python -m pytest -q
```

Each test uses its own temporary database, so running the tests never
changes your real notes.

## Pages

| URL                  | What it does                        |
|----------------------|-------------------------------------|
| `/`                  | List all notes (search with `?q=`)  |
| `/notes/new`         | Form to create a note               |
| `/notes/<id>`        | View one note                       |
| `/notes/<id>/edit`   | Edit a note                         |
| `/notes/<id>/delete` | Delete a note (POST only)           |

## Project structure

```
flask-notes/
├── app.py            # Flask app and all the routes (URLs)
├── db.py             # All database code (SQL queries)
├── schema.sql        # Creates the notes table
├── static/
│   └── style.css     # The app's styling
├── templates/        # HTML pages (Jinja templates)
│   ├── base.html     # Shared layout: header + stylesheet
│   ├── index.html    # Home page: note tiles and search
│   ├── note.html     # A single note
│   ├── new_note.html
│   └── edit_note.html
├── test_app.py       # pytest tests
└── requirements.txt  # Python packages the app needs
```

## Built with

- Python 3 and Flask
- SQLite (built into Python, nothing extra to install)
- Jinja2 templates and plain CSS
- pytest for testing
