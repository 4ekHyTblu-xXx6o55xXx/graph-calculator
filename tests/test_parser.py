import unittest
from src.parser import Parser, ParseError


class TestParser(unittest.TestCase):

    def test_empty_expression_raises_error(self):
        with self.assertRaises(ParseError):
            Parser("").parse()
        with self.assertRaises(ParseError):
            Parser("   ").parse()

    def test_variable_extraction(self):
        expr = Parser("sin(x) + cos(y) - x * 2").parse()
        self.assertEqual(expr.variables, {"x", "y"})

    def test_constants_distinguished_from_variables(self):
        expr = Parser("sin(pi * x) + e").parse()
        self.assertEqual(expr.variables, {"x"})

    def test_unary_minus_detection(self):
        expr1 = Parser("-x + 5").parse()
        ops = [item.value for item in expr1.rpn if item.kind == 'op']
        self.assertIn('neg', ops)

        expr2 = Parser("2 * -3").parse()
        ops2 = [item.value for item in expr2.rpn if item.kind == 'op']
        self.assertIn('neg', ops2)

    def test_binary_minus_detection(self):
        expr = Parser("x - y").parse()
        ops = [item.value for item in expr.rpn if item.kind == 'op']
        self.assertEqual(ops, ['-'])

    def test_mismatched_parentheses_raises_error(self):
        with self.assertRaises(ParseError) as ctx:
            Parser("(x + 2").parse()
        self.assertIn("Несогласованная открывающая скобка", str(ctx.exception))

        with self.assertRaises(ParseError) as ctx:
            Parser("x + 2)").parse()
        self.assertIn("Несогласованная закрывающая скобка", str(ctx.exception))

    def test_unexpected_operator_raises_error(self):
        with self.assertRaises(ParseError):
            Parser("* x + 5").parse()
        with self.assertRaises(ParseError):
            Parser("x / * 2").parse()

    def test_multi_argument_function_call(self):
        expr = Parser("min(x, 10)").parse()
        funcs = [item for item in expr.rpn if item.kind == 'func']
        self.assertEqual(len(funcs), 1)
        self.assertEqual(funcs[0].value, 'min')
        self.assertEqual(funcs[0].arity, 2)


if __name__ == '__main__':
    unittest.main()
