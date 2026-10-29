import sys
import argparse
from typing import Optional

from src.parser import Parser, ParseError
from src.tokenizer import LexerError
from src.evaluator import Evaluator
from src.tabulator import Tabulator
from src.plotter import PlotWindow


def parse_args(args: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Калькулятор с графиками")
    parser.add_argument("--expr", "-e", type=str, help="Математическое выражение")
    parser.add_argument("--2d", dest="is_2d", action="store_true", help="Функция двух переменных z = f(x, y)")
    parser.add_argument("--xmin", type=float, default=-5.0, help="Мин. X")
    parser.add_argument("--xmax", type=float, default=5.0, help="Макс. X")
    parser.add_argument("--ymin", type=float, default=-5.0, help="Мин. Y (для 2D)")
    parser.add_argument("--ymax", type=float, default=5.0, help="Макс. Y (для 2D)")
    parser.add_argument("--steps", "-s", type=int, default=50, help="Число точек")
    parser.add_argument("--plot", "-p", action="store_true", help="Вывести график")
    parser.add_argument("--table", "-t", action="store_true", help="Вывести таблицу значений")
    return parser.parse_args(args)


def run_1d(expr_str: str, xmin: float, xmax: float, steps: int, show_plot: bool, show_table: bool) -> int:
    try:
        parser = Parser(expr_str)
        expression = parser.parse()
    except (LexerError, ParseError) as err:
        print(f"Ошибка разбора: {err}", file=sys.stderr)
        return 1

    tabulator = Tabulator()
    try:
        points = tabulator.tabulate_1d(expression, x_min=xmin, x_max=xmax, steps=steps)
    except Exception as err:
        print(f"Ошибка табуляции: {err}", file=sys.stderr)
        return 1

    valid_points = [p for p in points if p.is_valid]
    print(f"\nВыражение: f(x) = {expr_str}")
    print(f"Переменные: {sorted(expression.variables)}")
    print(f"Всего точек: {len(points)}, корректных: {len(valid_points)}, разрывов: {len(points) - len(valid_points)}")

    if show_table:
        print("\nТаблица значений:")
        print(f"{'x':>10} | {'y = f(x)':>15} | {'Статус':<10}")
        print("-" * 40)
        for p in points[:30]:
            if p.is_valid and p.y is not None:
                print(f"{p.x:10.4f} | {p.y:15.6f} | OK")
            else:
                print(f"{p.x:10.4f} | {'---':>15} | ERROR")
        if len(points) > 30:
            print(f"... и ещё {len(points) - 30} точек ...")

    if show_plot:
        plotter = PlotWindow()
        rendered = plotter.render_1d(points, title=f"f(x) = {expr_str}")
        print("\n" + rendered)

    return 0


def run_2d(expr_str: str, xmin: float, xmax: float, ymin: float, ymax: float, steps: int, show_plot: bool) -> int:
    try:
        parser = Parser(expr_str)
        expression = parser.parse()
    except (LexerError, ParseError) as err:
        print(f"Ошибка разбора: {err}", file=sys.stderr)
        return 1

    tabulator = Tabulator()
    grid_steps = min(30, max(5, int(steps ** 0.5 * 3)))
    try:
        grid = tabulator.tabulate_2d(
            expression,
            x_min=xmin, x_max=xmax,
            y_min=ymin, y_max=ymax,
            x_steps=grid_steps, y_steps=grid_steps
        )
    except Exception as err:
        print(f"Ошибка табуляции: {err}", file=sys.stderr)
        return 1

    print(f"\nВыражение: z = f(x, y) = {expr_str}")
    print(f"Переменные: {sorted(expression.variables)}")
    print(f"Сетка: {grid.width}x{grid.height} ({grid.total_points} точек)")
    print(f"Корректных точек: {grid.valid_count}, разрывов: {grid.error_count}")

    if show_plot:
        plotter = PlotWindow()
        rendered = plotter.render_2d_heatmap(grid, title=f"z = {expr_str}")
        print("\n" + rendered)

    return 0


def interactive_mode():
    print("Калькулятор с графиками (для выхода введите 'exit')")
    evaluator = Evaluator()

    while True:
        try:
            line = input("\nВведите формулу > ").strip()
            if not line:
                continue
            if line.lower() in ('exit', 'quit', 'q'):
                break

            parser = Parser(line)
            expr = parser.parse()
            vars_found = expr.variables

            if not vars_found:
                val = evaluator.evaluate(expr)
                print(f"Результат = {val}")
                continue

            if vars_found == {'x'}:
                run_1d(line, xmin=-5.0, xmax=5.0, steps=50, show_plot=True, show_table=False)
            elif vars_found <= {'x', 'y'}:
                run_2d(line, xmin=-3.0, xmax=3.0, ymin=-3.0, ymax=3.0, steps=25, show_plot=True)
            else:
                print(f"Поддерживаются только переменные x и y (найдено: {vars_found})")
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"Ошибка: {e}")


def main() -> int:
    args = parse_args()
    if not args.expr:
        interactive_mode()
        return 0

    if args.is_2d:
        return run_2d(args.expr, args.xmin, args.xmax, args.ymin, args.ymax, args.steps, show_plot=args.plot or True)
    else:
        return run_1d(args.expr, args.xmin, args.xmax, args.steps, show_plot=args.plot or True, show_table=args.table)


if __name__ == "__main__":
    sys.exit(main())
