"""CSV export helpers."""

import csv
from pathlib import Path


def export_experiment_csv(experiment, measurements, destination):
    """Export one experiment and its measurement rows to a CSV file."""
    destination = Path(destination)

    with destination.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Experiment", experiment["title"]])
        writer.writerow(["Description", experiment["description"]])
        writer.writerow([])
        writer.writerow(["Label", "X", "Y"])

        for measurement in measurements:
            writer.writerow([
                measurement["label"],
                measurement["x_value"],
                measurement["y_value"],
            ])

    return destination
