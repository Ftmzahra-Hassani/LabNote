"""Validation and higher-level experiment operations."""

from database.db_manager import DatabaseManager


class ExperimentManager:
    def __init__(self, database):
        self.database = database

    @staticmethod
    def validate_experiment(title, description):
        title = title.strip()
        if not title:
            raise ValueError("Experiment title cannot be empty.")
        if len(title) > 100:
            raise ValueError("Experiment title must be 100 characters or fewer.")
        return title, description.strip()

    @staticmethod
    def validate_measurement(label, x_text, y_text):
        try:
            x_value = float(x_text)
            y_value = float(y_text)
        except ValueError:
            raise ValueError("X and Y must be valid numbers.")

        return label.strip(), x_value, y_value

    def create(self, title, description):
        title, description = self.validate_experiment(title, description)
        return self.database.add_experiment(title, description)

    def update(self, experiment_id, title, description):
        title, description = self.validate_experiment(title, description)
        self.database.update_experiment(experiment_id, title, description)

    def add_measurement(self, experiment_id, label, x_text, y_text):
        label, x_value, y_value = self.validate_measurement(
            label, x_text, y_text
        )
        self.database.add_measurement(
            experiment_id, label, x_value, y_value
        )
