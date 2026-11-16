"""Small SQLite data-access layer for LabNote."""

import sqlite3
from pathlib import Path
from datetime import datetime

from database.schema import CREATE_TABLES


class DatabaseManager:
    def __init__(self, database_path=None):
        # Keep the database in the project folder unless a path is supplied.
        self.database_path = Path(database_path or "labnote.db")
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_database()

    def connect(self):
        """Open a database connection and enable foreign-key rules."""
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize_database(self):
        """Create the tables on the first run."""
        with self.connect() as connection:
            connection.executescript(CREATE_TABLES)

    def get_dashboard_summary(self):
        """Return total experiments, measurements, and latest experiment."""
        with self.connect() as connection:
            experiment_count = connection.execute(
                "SELECT COUNT(*) FROM experiments"
            ).fetchone()[0]
            measurement_count = connection.execute(
                "SELECT COUNT(*) FROM measurements"
            ).fetchone()[0]
            latest = connection.execute(
                "SELECT title, created_at FROM experiments "
                "ORDER BY id DESC LIMIT 1"
            ).fetchone()

        return {
            "experiments": experiment_count,
            "measurements": measurement_count,
            "latest": latest["title"] if latest else "None yet",
        }

    def get_experiments(self, search_text=""):
        """Return all experiments, optionally filtered by title."""
        query = (
            "SELECT e.*, COUNT(m.id) AS measurement_count "
            "FROM experiments e LEFT JOIN measurements m "
            "ON e.id = m.experiment_id "
        )
        parameters = ()
        if search_text:
            query += "WHERE e.title LIKE ? "
            parameters = (f"%{search_text}%",)
        query += "GROUP BY e.id ORDER BY e.id DESC"

        with self.connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]

    def get_experiment(self, experiment_id):
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM experiments WHERE id = ?", (experiment_id,)
            ).fetchone()
        return dict(row) if row else None

    def add_experiment(self, title, description):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO experiments (title, description, created_at) "
                "VALUES (?, ?, ?)",
                (title, description, created_at),
            )
            return cursor.lastrowid

    def update_experiment(self, experiment_id, title, description):
        with self.connect() as connection:
            connection.execute(
                "UPDATE experiments SET title = ?, description = ? "
                "WHERE id = ?",
                (title, description, experiment_id),
            )

    def delete_experiment(self, experiment_id):
        with self.connect() as connection:
            connection.execute(
                "DELETE FROM experiments WHERE id = ?", (experiment_id,)
            )

    def get_measurements(self, experiment_id):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM measurements WHERE experiment_id = ? "
                "ORDER BY id",
                (experiment_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def add_measurement(self, experiment_id, label, x_value, y_value):
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO measurements "
                "(experiment_id, label, x_value, y_value) VALUES (?, ?, ?, ?)",
                (experiment_id, label, x_value, y_value),
            )

    def delete_measurement(self, measurement_id):
        with self.connect() as connection:
            connection.execute(
                "DELETE FROM measurements WHERE id = ?", (measurement_id,)
            )
