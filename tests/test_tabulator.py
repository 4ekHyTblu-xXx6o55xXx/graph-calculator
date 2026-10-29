import unittest
from src.parser import Parser
from src.tabulator import Tabulator


class TestTabulator(unittest.TestCase):

    def setUp(self):
        self.tabulator = Tabulator()

    def test_tabulate_1d_linear(self):
        expr = Parser("2 * x").parse()
        points = self.tabulator.tabulate_1d(expr, x_min=0.0, x_max=10.0, steps=11)
        self.assertEqual(len(points), 11)
        self.assertEqual(points[0].x, 0.0)
        self.assertEqual(points[0].y, 0.0)
        self.assertEqual(points[-1].x, 10.0)
        self.assertEqual(points[-1].y, 20.0)
        for p in points:
            self.assertTrue(p.is_valid)

    def test_tabulate_1d_discontinuity(self):
        expr = Parser("1 / x").parse()
        points = self.tabulator.tabulate_1d(expr, x_min=-2.0, x_max=2.0, steps=5)
        self.assertEqual(len(points), 5)
        zero_point = points[2]
        self.assertEqual(zero_point.x, 0.0)
        self.assertFalse(zero_point.is_valid)

    def test_tabulate_1d_invalid_ranges(self):
        expr = Parser("x").parse()
        with self.assertRaises(ValueError):
            self.tabulator.tabulate_1d(expr, x_min=5.0, x_max=2.0)
        with self.assertRaises(ValueError):
            self.tabulator.tabulate_1d(expr, x_min=0.0, x_max=1.0, steps=1)

    def test_tabulate_2d_grid(self):
        expr = Parser("x + y").parse()
        grid = self.tabulator.tabulate_2d(
            expr,
            x_min=0.0, x_max=2.0,
            y_min=0.0, y_max=3.0,
            x_steps=3, y_steps=4
        )
        self.assertEqual(grid.width, 3)
        self.assertEqual(grid.height, 4)
        self.assertEqual(grid.total_points, 12)
        self.assertEqual(grid.valid_count, 12)
        self.assertEqual(grid.error_count, 0)
        self.assertAlmostEqual(grid.z_min, 0.0)
        self.assertAlmostEqual(grid.z_max, 5.0)


if __name__ == '__main__':
    unittest.main()
