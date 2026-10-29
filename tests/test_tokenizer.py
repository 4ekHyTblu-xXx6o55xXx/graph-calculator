import unittest
from src.tokenizer import Tokenizer, TokenType, LexerError


class TestTokenizer(unittest.TestCase):

    def test_numbers_integers_and_floats(self):
        tokenizer = Tokenizer("42 3.1415 0.001 .5 1e3 2.5e-2")
        tokens = tokenizer.tokenize()
        expected = ["42", "3.1415", "0.001", ".5", "1e3", "2.5e-2"]
        num_tokens = [t.value for t in tokens if t.type == TokenType.NUMBER]
        self.assertEqual(num_tokens, expected)

    def test_identifiers_and_constants(self):
        tokenizer = Tokenizer("x y sin cos tan pi e my_var")
        tokens = tokenizer.tokenize()
        ident_tokens = [t.value for t in tokens if t.type == TokenType.IDENTIFIER]
        self.assertEqual(ident_tokens, ["x", "y", "sin", "cos", "tan", "pi", "e", "my_var"])

    def test_operators_and_delimiters(self):
        tokenizer = Tokenizer("+ - * / ^ % ( ) ,")
        tokens = tokenizer.tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        expected_types = [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
            TokenType.POWER,
            TokenType.MODULO,
            TokenType.LPAREN,
            TokenType.RPAREN,
            TokenType.COMMA,
        ]
        self.assertEqual(types, expected_types)

    def test_token_positions(self):
        expr = "sin( x )"
        tokenizer = Tokenizer(expr)
        tokens = tokenizer.tokenize()
        self.assertEqual(tokens[0].value, "sin")
        self.assertEqual(tokens[0].position, 0)
        self.assertEqual(tokens[1].type, TokenType.LPAREN)
        self.assertEqual(tokens[1].position, 3)
        self.assertEqual(tokens[2].value, "x")
        self.assertEqual(tokens[2].position, 5)

    def test_invalid_characters_raise_lexer_error(self):
        tokenizer = Tokenizer("x + 5 $ 2")
        with self.assertRaises(LexerError) as ctx:
            tokenizer.tokenize()
        self.assertIn("Недопустимый символ '$'", str(ctx.exception))

    def test_multiple_dots_in_number_raises_lexer_error(self):
        tokenizer = Tokenizer("3.14.15")
        with self.assertRaises(LexerError):
            tokenizer.tokenize()


if __name__ == '__main__':
    unittest.main()
