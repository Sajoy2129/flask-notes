# Flask Notes

A small notes app (create, view, edit, delete, search by title) built with
Flask and SQLite. It is a learning project, so code should stay simple and
well commented for a beginner.

## Commands

Always use the virtual environment in `.venv/`.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt  # setup
.venv/bin/python app.py                 # run the dev server on :5000
.venv/bin/flask --app app seed          # add 3 sample notes
.venv/bin/python -m pytest -q           # run all tests
```

## Layout

- `app.py`: app factory `create_app(database_path=None)`, all routes, and the
  `format_date` template filter. Routes are defined inside the factory.
- `db.py`: **all** SQL lives here, one small function per query
  (`get_all_notes`, `search_notes`, `get_note`, `add_note`, `update_note`,
  `delete_note`). Routes call these and never write SQL themselves.
- `schema.sql`: the `notes` table (`id`, `title`, `body`, `created_at`).
  Applied automatically on startup with `CREATE TABLE IF NOT EXISTS`.
- `templates/`: Jinja templates. Every page `{% extends "base.html" %}`.
- `static/style.css`: the only stylesheet, linked in `base.html`.
- `test_app.py`: pytest tests. The `app` fixture gives each test a fresh
  database in `tmp_path`, so tests never touch `notes.db`.

## Conventions

- SQL always uses `?` placeholders, never f-strings with user input.
- Actions that change data (delete) use POST forms, never plain links.
- Form routes follow Post/Redirect/Get: redirect after a successful POST;
  on a validation error, re-render the form with `error=...` and status 400.
- Styling goes in `static/style.css` using the `:root` color variables and
  CSS classes, not inline `style=""` attributes.
- Follow PEP 8. Add a pytest test for every new feature, and run the full
  suite before committing.
- Small commits with clear messages, one feature per commit.

## Don't commit

`.venv/`, `notes.db`, `.env`, or cache folders. They're already in
`.gitignore`.
