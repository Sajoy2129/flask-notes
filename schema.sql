-- Create the "notes" table if it doesn't exist yet.
-- Running this again is safe: IF NOT EXISTS skips it when the table is there.
CREATE TABLE IF NOT EXISTS notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique number, filled in for us
    title      TEXT NOT NULL,                      -- every note must have a title
    body       TEXT NOT NULL DEFAULT '',           -- empty string if not given
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP  -- when the note was saved
);
