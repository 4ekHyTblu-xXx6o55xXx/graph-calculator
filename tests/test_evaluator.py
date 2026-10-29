import math
import unittest
from src.parser import Parser
from src.evaluator import Evaluator, EvaluationError, MathDomainError


class TestEvaluator(unittest.TestCase):

    def setUp(self):
        self.evaluator = Evaluator()

    def eval_expr(self, text: str, context: dict = None) -> float:
        expr = Parser(text).parse()
        return self.evaluator.evaluate(expr, context or {})

    def test_arithmetic_operations(self):
        self.assertAlmostEqual(self.eval_expr("2 + 3 * 4"), 14.0)
        self.assertAlmostEqual(self.eval_expr("(2 + 3) * 4"), 20.0)
        self.assertAlmostEqual(self.eval_expr("10 - 4 - 2"), 4.0)
        self.assertAlmostEqual(self.eval_expr("20 / 4 / 2"), 2.5)
        self.assertAlmostEqual(self.eval_expr("14 % 4"), 2.0)

    def test_power_operator(self):
        self.assertAlmostEqual(self.eval_expr("2 ^ 3"), 8.0)
        self.assertAlmostEqual(self.eval_expr("2 ^ 3 ^ 2"), 512.0)

    def test_unary_minus(self):
        self.assertAlmostEqual(self.eval_expr("-5 + 10"), 5.0)
        self.assertAlmostEqual(self.eval_expr("2 * -3"), -6.0)
        self.assertAlmostEqual(self.eval_expr("- -7"), 7.0)

    def test_constants(self):
        self.assertAlmostEqual(self.eval_expr("pi"), math.pi)
        self.assertAlmostEqual(self.eval_expr("e"), math.e)
        self.assertAlmostEqual(self.eval_expr("sin(pi / 2)"), 1.0)
        self.assertAlmostEqual(self.eval_expr("cos(0)"), 1.0)

    def test_variables_substitution(self):
        self.assertAlmostEqual(self.eval_expr("x * 2 + 1", {'x': 4}), 9.0)
        self.assertAlmostEqual(self.eval_expr("x^2 + y^2", {'x': 3, 'y': 4}), 25.0)

    def test_functions_1arg(self):
        self.assertAlmostEqual(self.eval_expr("sqrt(16)"), 4.0)
        self.assertAlmostEqual(self.eval_expr("abs(-42)"), 42.0)
        self.assertAlmostEqual(self.eval_expr("ln(e)"), 1.0)
        self.assertAlmostEqual(self.eval_expr("exp(0)"), 1.0)
        self.assertAlmostEqual(self.eval_expr("floor(3.7)"), 3.0)
        self.assertAlmostEqual(self.eval_expr("ceil(3.2)"), 4.0)

    def test_functions_2arg(self):
        self.assertAlmostEqual(self.eval_expr("min(10, 3)"), 3.0)
        self.assertAlmostEqual(self.eval_expr("max(10, 3)"), 10.0)
        self.assertAlmostEqual(self.eval_expr("hypot(3, 4)"), 5.0)
        self.assertAlmostEqual(self.eval_expr("pow(2, 5)"), 32.0)

    def test_division_by_zero_raises_domain_error(self):
        with self.assertRaises(MathDomainError):
            self.eval_expr("5 / 0")
        with self.assertRaises(MathDomainError):
            self.eval_expr("10 / (x - 3)", {'x': 3})

    def test_math_domain_errors(self):
        with self.assertRaises(MathDomainError):
            self.eval_expr("sqrt(-4)")
        with self.assertRaises(MathDomainError):
            self.eval_expr("ln(0)")
        with self.assertRaises(MathDomainError):
            self.eval_expr("ln(-5)")
        with self.assertRaises(MathDomainError):
            self.eval_expr("asin(2)")

    def test_missing_variable_raises_error(self):
        with self.assertRaises(EvaluationError):
            self.eval_expr("x + y", {'x': 5})


if __name__ == '__main__':
    unittest.main()
