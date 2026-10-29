from typing import List
from src.tabulator import Point2D, Grid2D


class PlotWindow:
    GRADIENT = " .:-=+*#%@"

    def __init__(self, width: int = 65, height: int = 20):
        self.width = max(20, width)
        self.height = max(10, height)

    # 1D график в ASCII
    def render_1d(self, points: List[Point2D], title: str = "График функции") -> str:
        valid_points = [p for p in points if p.is_valid and p.y is not None]
        if not valid_points:
            return f"[{title}]\nНет точек для отображения."

        xs = [p.x for p in points]
        x_min, x_max = min(xs), max(xs)

        ys = [p.y for p in valid_points]
        y_min, y_max = min(ys), max(ys)

        if abs(y_max - y_min) < 1e-9:
            y_min -= 1.0
            y_max += 1.0

        canvas = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Оси координат
        y_axis_col = -1
        if x_min <= 0 <= x_max and x_max > x_min:
            y_axis_col = int(round((0 - x_min) / (x_max - x_min) * (self.width - 1)))

        x_axis_row = -1
        if y_min <= 0 <= y_max and y_max > y_min:
            x_axis_row = int(round((y_max - 0) / (y_max - y_min) * (self.height - 1)))

        if 0 <= y_axis_col < self.width:
            for r in range(self.height):
                canvas[r][y_axis_col] = '|'

        if 0 <= x_axis_row < self.height:
            for c in range(self.width):
                canvas[x_axis_row][c] = '-'

        if 0 <= y_axis_col < self.width and 0 <= x_axis_row < self.height:
            canvas[x_axis_row][y_axis_col] = '+'

        # Точки графика
        for p in points:
            col = int(round((p.x - x_min) / (x_max - x_min) * (self.width - 1)))
            col = max(0, min(self.width - 1, col))

            if p.is_valid and p.y is not None:
                row = int(round((y_max - p.y) / (y_max - y_min) * (self.height - 1)))
                if 0 <= row < self.height:
                    canvas[row][col] = '*'
            else:
                if 0 <= x_axis_row < self.height:
                    canvas[x_axis_row][col] = '!'
                else:
                    canvas[self.height - 1][col] = '!'

        lines: List[str] = [
            f"=== {title} ===",
            f"y_max: {y_max:+.4f}",
        ]
        for row in canvas:
            lines.append("".join(row))
        lines.append(f"y_min: {y_min:+.4f}")
        lines.append(f"x_min: {x_min:+.4f}" + " " * (self.width - 24) + f"x_max: {x_max:+.4f}")

        return "\n".join(lines)

    # 2D heatmap на плоскости
    def render_2d_heatmap(self, grid: Grid2D, title: str = "Карта уровней") -> str:
        lines: List[str] = [
            f"=== {title} ===",
            f"Область: x in [{grid.xs[0]:.2f}, {grid.xs[-1]:.2f}], y in [{grid.ys[0]:.2f}, {grid.ys[-1]:.2f}]",
        ]

        if grid.z_min is None or grid.z_max is None:
            lines.append("Нет точек для отображения.")
            return "\n".join(lines)

        z_span = grid.z_max - grid.z_min
        if z_span < 1e-12:
            z_span = 1.0

        n_levels = len(self.GRADIENT)

        lines.append(f"Диапазон z: [{grid.z_min:.4f} ... {grid.z_max:.4f}]")
        lines.append("+" + "-" * grid.width + "+")

        for y_idx in reversed(range(grid.height)):
            row_chars = []
            for x_idx in range(grid.width):
                val = grid.value_at(x_idx, y_idx)
                if val is None:
                    row_chars.append("?")
                else:
                    norm = (val - grid.z_min) / z_span
                    norm = max(0.0, min(1.0, norm))
                    char_idx = int(norm * (n_levels - 1))
                    row_chars.append(self.GRADIENT[char_idx])
            y_val = grid.ys[y_idx]
            lines.append(f"|{''.join(row_chars)}| y={y_val:+.2f}")

        lines.append("+" + "-" * grid.width + "+")
        lines.append(f"  x={grid.xs[0]:+.2f}" + " " * max(1, grid.width - 18) + f"x={grid.xs[-1]:+.2f}")

        return "\n".join(lines)
