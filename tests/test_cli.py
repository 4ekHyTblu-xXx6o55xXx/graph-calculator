import contextlib
import io
import sys
import unittest
from unittest.mock import patch

from src.cli import main, parse_args, run_1d, run_2d
from src.parser import Parser
from src.plotter import PlotWindow
from src.tabulator import Tabulator


class TestCliAndPlotter(unittest.TestCase):

    def test_cli_args_parsing(self):
        args = parse_args(["--expr", "sin(x)", "--xmin", "-1.0", "--xmax", "1.0", "--steps", "20", "--plot"])
        self.assertEqual(args.expr, "sin(x)")
        self.assertEqual(args.xmin, -1.0)
        self.assertEqual(args.xmax, 1.0)
        self.assertEqual(args.steps, 20)
        self.assertTrue(args.plot)

    def test_run_1d_success(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = run_1d("cos(x)", xmin=-3.14, xmax=3.14, steps=15, show_plot=False, show_table=False)
        self.assertEqual(code, 0)

    def test_run_1d_syntax_error_returns_nonzero(self):
        err_buf = io.StringIO()
        with contextlib.redirect_stderr(err_buf):
            code = run_1d("cos(x +", xmin=-1.0, xmax=1.0, steps=10, show_plot=False, show_table=False)
        self.assertEqual(code, 1)

    def test_run_1d_invalid_range_returns_nonzero(self):
        err_buf = io.StringIO()
        with contextlib.redirect_stderr(err_buf):
            code = run_1d("x", xmin=5.0, xmax=1.0, steps=10, show_plot=False, show_table=False)
        self.assertEqual(code, 1)

    def test_run_2d_success(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = run_2d("x^2 + y^2", xmin=-2.0, xmax=2.0, ymin=-2.0, ymax=2.0, steps=16, show_plot=False)
        self.assertEqual(code, 0)

    def test_run_2d_invalid_steps_returns_nonzero(self):
        for steps in (-4, -1, 0, 1):
            with self.subTest(steps=steps):
                err_buf = io.StringIO()
                with contextlib.redirect_stderr(err_buf):
                    code = run_2d("x + y", -1.0, 1.0, -1.0, 1.0, steps, show_plot=False)
                self.assertEqual(code, 1)
                self.assertIn("число шагов должно быть >= 2", err_buf.getvalue())

    def test_main_table_only_skips_plot(self):
        out_buf = io.StringIO()
        argv = ["cli", "--expr", "2 * x", "--xmin", "0", "--xmax", "2", "--steps", "3", "--table"]
        # при --table без --plot график не должен выводиться
        with patch.object(sys, "argv", argv), contextlib.redirect_stdout(out_buf):
            code = main()
        output = out_buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("Таблица значений:", output)
        self.assertNotIn("y_max:", output)

    def test_main_default_renders_plot(self):
        out_buf = io.StringIO()
        argv = ["cli", "--expr", "x", "--xmin", "-1", "--xmax", "1", "--steps", "5"]
        with patch.object(sys, "argv", argv), contextlib.redirect_stdout(out_buf):
            code = main()
        output = out_buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("y_max:", output)

    def test_plotter_1d_rendering(self):
        expr = Parser("x").parse()
        tab = Tabulator()
        pts = tab.tabulate_1d(expr, x_min=-5.0, x_max=5.0, steps=25)
        window = PlotWindow(width=30, height=10)
        output = window.render_1d(pts, title="Test 1D")
        self.assertIn("=== Test 1D ===", output)
        self.assertIn("y_max", output)
        self.assertIn("y_min", output)
        self.assertIn("*", output)

    def test_plotter_2d_heatmap_rendering(self):
        expr = Parser("x * y").parse()
        tab = Tabulator()
        grid = tab.tabulate_2d(expr, x_min=-1.0, x_max=1.0, y_min=-1.0, y_max=1.0, x_steps=5, y_steps=5)
        window = PlotWindow()
        output = window.render_2d_heatmap(grid, title="Test Heatmap")
        self.assertIn("=== Test Heatmap ===", output)


if __name__ == '__main__':
    unittest.main()
