"""SQL schema used to create the LabNote database."""

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id INTEGER NOT NULL,
    label TEXT DEFAULT '',
    x_value REAL NOT NULL,
    y_value REAL NOT NULL,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
        ON DELETE CASCADE
);
"""
