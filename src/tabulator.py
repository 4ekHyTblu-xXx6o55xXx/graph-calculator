import math
from typing import List, Optional
from src.parser import Expression
from src.evaluator import Evaluator, EvaluationError


class Point2D:
    def __init__(self, x: float, y: Optional[float] = None, is_valid: bool = True, error: Optional[str] = None):
        self.x = x
        self.y = y
        self.is_valid = is_valid
        self.error = error

    def __repr__(self) -> str:
        if self.is_valid:
            return f"Point2D(x={self.x:.4f}, y={self.y:.4f})"
        return f"Point2D(x={self.x:.4f}, INVALID)"


class Grid2D:
    def __init__(self, xs: List[float], ys: List[float], matrix: List[List[Optional[float]]]):
        self.xs = xs
        self.ys = ys
        self.matrix = matrix

        valid_vals = [
            val for row in matrix for val in row
            if val is not None
        ]
        self.valid_count = len(valid_vals)
        self.total_points = len(xs) * len(ys)
        self.error_count = self.total_points - self.valid_count

        if valid_vals:
            self.z_min: Optional[float] = min(valid_vals)
            self.z_max: Optional[float] = max(valid_vals)
        else:
            self.z_min = None
            self.z_max = None

    @property
    def width(self) -> int:
        return len(self.xs)

    @property
    def height(self) -> int:
        return len(self.ys)

    def value_at(self, x_idx: int, y_idx: int) -> Optional[float]:
        return self.matrix[y_idx][x_idx]


class Tabulator:
    def __init__(self, evaluator: Optional[Evaluator] = None):
        self.evaluator = evaluator or Evaluator()

    @staticmethod
    def _validate_range(name: str, lower: float, upper: float) -> None:
        if not math.isfinite(lower) or not math.isfinite(upper):
            raise ValueError(f"Границы диапазона {name} должны быть конечными числами")
        if lower >= upper:
            raise ValueError(f"{name}_min ({lower}) должен быть меньше {name}_max ({upper})")

    @staticmethod
    def _validate_steps(steps: int, name: str = "Число шагов") -> None:
        if isinstance(steps, bool) or not isinstance(steps, int) or steps < 2:
            raise ValueError(f"{name} должно быть целым числом >= 2 (передано {steps})")

    # Табуляция функции 1 переменной f(x)
    def tabulate_1d(
        self,
        expr: Expression,
        x_min: float,
        x_max: float,
        steps: int = 100,
        var_name: str = 'x'
    ) -> List[Point2D]:
        self._validate_range('x', x_min, x_max)
        self._validate_steps(steps)

        points: List[Point2D] = []
        dx = (x_max - x_min) / (steps - 1)

        for i in range(steps):
            x = x_min + i * dx
            if i == steps - 1:
                x = x_max

            try:
                y = self.evaluator.evaluate(expr, {var_name: x})
                points.append(Point2D(x=x, y=y, is_valid=True))
            except EvaluationError as err:
                points.append(Point2D(x=x, y=None, is_valid=False, error=str(err)))

        return points

    # Табуляция функции 2 переменных z = f(x, y)
    def tabulate_2d(
        self,
        expr: Expression,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        x_steps: int = 25,
        y_steps: int = 25,
        var_x: str = 'x',
        var_y: str = 'y'
    ) -> Grid2D:
        self._validate_range('x', x_min, x_max)
        self._validate_range('y', y_min, y_max)
        self._validate_steps(x_steps, "Число шагов по x")
        self._validate_steps(y_steps, "Число шагов по y")

        dx = (x_max - x_min) / (x_steps - 1)
        dy = (y_max - y_min) / (y_steps - 1)

        xs = [x_min + i * dx for i in range(x_steps)]
        xs[-1] = x_max
        ys = [y_min + j * dy for j in range(y_steps)]
        ys[-1] = y_max

        matrix: List[List[Optional[float]]] = []

        for y in ys:
            row: List[Optional[float]] = []
            for x in xs:
                try:
                    z = self.evaluator.evaluate(expr, {var_x: x, var_y: y})
                    row.append(z)
                except EvaluationError:
                    row.append(None)
            matrix.append(row)

        return Grid2D(xs=xs, ys=ys, matrix=matrix)
