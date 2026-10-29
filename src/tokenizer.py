from enum import Enum, auto
from typing import List, Optional


class TokenType(Enum):
    NUMBER = auto()
    IDENTIFIER = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    POWER = auto()
    MODULO = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    EOF = auto()


class Token:
    def __init__(self, token_type: TokenType, value: str, position: int):
        self.type = token_type
        self.value = value
        self.position = position

    def __repr__(self) -> str:
        return f"Token({self.type.name}, '{self.value}', pos={self.position})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value and self.position == other.position


class LexerError(Exception):
    def __init__(self, message: str, position: int):
        super().__init__(f"Ошибка лексического анализа в позиции {position}: {message}")
        self.position = position


class Tokenizer:
    # Одиночные знаки операций и скобки
    SINGLE_CHAR_OPS = {
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '*': TokenType.MULTIPLY,
        '/': TokenType.DIVIDE,
        '^': TokenType.POWER,
        '%': TokenType.MODULO,
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        ',': TokenType.COMMA,
    }

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def _peek(self) -> Optional[str]:
        if self.pos < self.length:
            return self.text[self.pos]
        return None

    def _advance(self) -> str:
        char = self.text[self.pos]
        self.pos += 1
        return char

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while self.pos < self.length:
            char = self._peek()
            if char is None:
                break

            if char.isspace():
                self._advance()
                continue

            start_pos = self.pos

            # Числовые литералы
            if char.isdigit() or char == '.':
                num_str = self._read_number()
                tokens.append(Token(TokenType.NUMBER, num_str, start_pos))
                continue

            # Имена переменных, констант и функций
            if char.isalpha() or char == '_':
                ident_str = self._read_identifier()
                tokens.append(Token(TokenType.IDENTIFIER, ident_str, start_pos))
                continue

            # Операторы и разделители
            if char in self.SINGLE_CHAR_OPS:
                op_char = self._advance()
                tokens.append(Token(self.SINGLE_CHAR_OPS[op_char], op_char, start_pos))
                continue

            raise LexerError(f"Недопустимый символ '{char}'", self.pos)

        tokens.append(Token(TokenType.EOF, "", self.pos))
        return tokens

    def _read_number(self) -> str:
        start = self.pos
        has_dot = False

        if self.text[self.pos] == '.':
            has_dot = True
            self.pos += 1
            if self.pos >= self.length or not self.text[self.pos].isdigit():
                raise LexerError("Одиночная точка не является числом", start)

        while self.pos < self.length:
            ch = self.text[self.pos]
            if ch.isdigit():
                self.pos += 1
            elif ch == '.':
                if has_dot:
                    raise LexerError("Второй символ точки в числе недопустим", self.pos)
                has_dot = True
                self.pos += 1
            else:
                break

        # Экспоненциальная нотация (1e-5, 2E3)
        if self.pos < self.length and self.text[self.pos] in ('e', 'E'):
            exp_pos = self.pos
            self.pos += 1
            if self.pos < self.length and self.text[self.pos] in ('+', '-'):
                self.pos += 1
            if self.pos >= self.length or not self.text[self.pos].isdigit():
                raise LexerError("Некорректная экспоненциальная запись числа", exp_pos)
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1

        return self.text[start:self.pos]

    def _read_identifier(self) -> str:
        start = self.pos
        while self.pos < self.length:
            ch = self.text[self.pos]
            if ch.isalnum() or ch == '_':
                self.pos += 1
            else:
                break
        return self.text[start:self.pos]
