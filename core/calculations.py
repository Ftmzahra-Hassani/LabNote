"""Pure-Python statistical calculations; no third-party packages required."""

import math
import statistics


def describe(values):
    """Calculate basic descriptive statistics for a non-empty list."""
    if not values:
        raise ValueError("At least one value is required.")

    result = {
        "count": len(values),
        "mean": statistics.mean(values),
        "minimum": min(values),
        "maximum": max(values),
    }

    # Standard deviation and variance need at least two observations.
    if len(values) >= 2:
        result["stdev"] = statistics.stdev(values)
        result["variance"] = statistics.variance(values)
    else:
        result["stdev"] = 0.0
        result["variance"] = 0.0

    result["median"] = statistics.median(values)
    return result


def linear_regression(x_values, y_values):
    """
    Fit y = slope*x + intercept using the least-squares method.
    Return slope, intercept, and coefficient of determination (R²).
    """
    if len(x_values) != len(y_values):
        raise ValueError("X and Y must contain the same number of values.")
    if len(x_values) < 2:
        raise ValueError("At least two measurements are required.")

    mean_x = statistics.mean(x_values)
    mean_y = statistics.mean(y_values)

    denominator = sum((x - mean_x) ** 2 for x in x_values)
    if math.isclose(denominator, 0.0):
        raise ValueError("X values must not all be identical.")

    numerator = sum(
        (x - mean_x) * (y - mean_y)
        for x, y in zip(x_values, y_values)
    )

    slope = numerator / denominator
    intercept = mean_y - slope * mean_x

    predicted = [slope * x + intercept for x in x_values]
    total_sum_squares = sum((y - mean_y) ** 2 for y in y_values)
    residual_sum_squares = sum(
        (actual - estimate) ** 2
        for actual, estimate in zip(y_values, predicted)
    )

    # R² is undefined when every Y value is identical.
    if math.isclose(total_sum_squares, 0.0):
        r_squared = 1.0 if math.isclose(residual_sum_squares, 0.0) else 0.0
    else:
        r_squared = 1 - residual_sum_squares / total_sum_squares

    return {
        "slope": slope,
        "intercept": intercept,
        "r_squared": r_squared,
        "predicted": predicted,
    }
