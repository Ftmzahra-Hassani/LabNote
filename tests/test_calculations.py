import unittest

from core.calculations import describe, linear_regression


class TestCalculations(unittest.TestCase):
    def test_describe(self):
        result = describe([2, 4, 6])
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["mean"], 4)
        self.assertEqual(result["median"], 4)

    def test_linear_regression(self):
        result = linear_regression([1, 2, 3], [2, 4, 6])
        self.assertAlmostEqual(result["slope"], 2)
        self.assertAlmostEqual(result["intercept"], 0)
        self.assertAlmostEqual(result["r_squared"], 1)

    def test_regression_rejects_identical_x(self):
        with self.assertRaises(ValueError):
            linear_regression([2, 2, 2], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
