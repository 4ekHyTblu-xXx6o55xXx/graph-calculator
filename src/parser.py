from typing import List, Set, Union, Optional
from src.tokenizer import Token, TokenType, Tokenizer, LexerError


class ParseError(Exception):
    def __init__(self, message: str, position: int = -1):
        if position >= 0:
            super().__init__(f"Синтаксическая ошибка в позиции {position}: {message}")
        else:
            super().__init__(f"Синтаксическая ошибка: {message}")
        self.position = position


class RpnItem:
    def __init__(self, kind: str, value: Union[str, float], arity: int = 0):
        self.kind = kind    # num, var, const, op, func
        self.value = value
        self.arity = arity

    def __repr__(self) -> str:
        if self.kind == 'func':
            return f"func:{self.value}({self.arity})"
        return f"{self.kind}:{self.value}"


class Expression:
    def __init__(self, raw_expression: str, rpn: List[RpnItem]):
        self.raw = raw_expression
        self.rpn = rpn
        self._variables: Set[str] = {
            item.value for item in rpn
            if item.kind == 'var' and isinstance(item.value, str)
        }

    @property
    def variables(self) -> Set[str]:
        return set(self._variables)

    def __repr__(self) -> str:
        return f"Expression('{self.raw}', vars={sorted(self.variables)})"


class Parser:
    # Приоритеты операций
    PRECEDENCE = {
        '^': 4,
        'neg': 3,
        'pos': 3,
        '*': 2,
        '/': 2,
        '%': 2,
        '+': 1,
        '-': 1,
    }

    RIGHT_ASSOCIATIVE = {'^', 'neg', 'pos'}
    KNOWN_CONSTANTS = {"pi", "e"}

    def __init__(self, text: str):
        self.text = text
        self.tokens: List[Token] = []
        self.index = 0

    def parse(self) -> Expression:
        if not self.text or not self.text.strip():
            raise ParseError("Выражение не может быть пустым", 0)

        tokenizer = Tokenizer(self.text)
        self.tokens = tokenizer.tokenize()
        self.index = 0

        rpn: List[RpnItem] = []
        op_stack: List[dict] = []
        arg_counts: List[int] = []

        may_be_unary = True

        while self.index < len(self.tokens):
            token = self.tokens[self.index]

            if token.type == TokenType.EOF:
                break

            if token.type == TokenType.NUMBER:
                val = float(token.value)
                rpn.append(RpnItem('num', val))
                may_be_unary = False
                self.index += 1
                continue

            if token.type == TokenType.IDENTIFIER:
                next_tok = self._peek_next()
                if next_tok and next_tok.type == TokenType.LPAREN:
                    # Вызов функции
                    func_name = token.value.lower()
                    op_stack.append({
                        'type': 'func',
                        'name': func_name,
                        'pos': token.position,
                    })
                    self.index += 1
                    may_be_unary = True
                    continue
                else:
                    # Переменная или константа
                    ident = token.value
                    ident_lower = ident.lower()
                    if ident_lower in self.KNOWN_CONSTANTS:
                        rpn.append(RpnItem('const', ident_lower))
                    else:
                        rpn.append(RpnItem('var', ident))
                    may_be_unary = False
                    self.index += 1
                    continue

            if token.type in (TokenType.PLUS, TokenType.MINUS):
                op_symbol = token.value
                if may_be_unary:
                    op_symbol = 'neg' if op_symbol == '-' else 'pos'

                while op_stack:
                    top = op_stack[-1]
                    if top['type'] == 'op':
                        top_prec = self.PRECEDENCE.get(top['name'], 0)
                        curr_prec = self.PRECEDENCE.get(op_symbol, 0)
                        if (op_symbol not in self.RIGHT_ASSOCIATIVE and curr_prec <= top_prec) or \
                           (op_symbol in self.RIGHT_ASSOCIATIVE and curr_prec < top_prec):
                            rpn.append(RpnItem('op', top['name'], top['arity']))
                            op_stack.pop()
                            continue
                    break

                arity = 1 if op_symbol in ('neg', 'pos') else 2
                op_stack.append({'type': 'op', 'name': op_symbol, 'pos': token.position, 'arity': arity})
                may_be_unary = True
                self.index += 1
                continue

            if token.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.POWER, TokenType.MODULO):
                if may_be_unary:
                    raise ParseError(f"Неожиданный оператор '{token.value}'", token.position)

                op_symbol = token.value
                while op_stack:
                    top = op_stack[-1]
                    if top['type'] == 'op':
                        top_prec = self.PRECEDENCE.get(top['name'], 0)
                        curr_prec = self.PRECEDENCE.get(op_symbol, 0)
                        if (op_symbol not in self.RIGHT_ASSOCIATIVE and curr_prec <= top_prec) or \
                           (op_symbol in self.RIGHT_ASSOCIATIVE and curr_prec < top_prec):
                            rpn.append(RpnItem('op', top['name'], top['arity']))
                            op_stack.pop()
                            continue
                    break

                op_stack.append({'type': 'op', 'name': op_symbol, 'pos': token.position, 'arity': 2})
                may_be_unary = True
                self.index += 1
                continue

            if token.type == TokenType.LPAREN:
                is_function_call = bool(op_stack and op_stack[-1]['type'] == 'func')
                if is_function_call:
                    arg_counts.append(1)

                op_stack.append({
                    'type': 'paren',
                    'name': '(',
                    'pos': token.position,
                    'is_func': is_function_call
                })

                next_tok = self._peek_next()
                if next_tok and next_tok.type == TokenType.RPAREN:
                    if is_function_call:
                        arg_counts[-1] = 0

                may_be_unary = True
                self.index += 1
                continue

            if token.type == TokenType.COMMA:
                if not arg_counts:
                    raise ParseError("Запятая вне аргументов функции", token.position)

                found_lparen = False
                while op_stack:
                    top = op_stack[-1]
                    if top['type'] == 'paren' and top['name'] == '(':
                        found_lparen = True
                        break
                    rpn.append(RpnItem(top['type'], top['name'], top.get('arity', 0)))
                    op_stack.pop()

                if not found_lparen or not op_stack[-1].get('is_func', False):
                    raise ParseError("Запятая вне контекста функции", token.position)

                arg_counts[-1] += 1
                may_be_unary = True
                self.index += 1
                continue

            if token.type == TokenType.RPAREN:
                found_lparen = False
                while op_stack:
                    top = op_stack[-1]
                    if top['type'] == 'paren' and top['name'] == '(':
                        paren_info = op_stack.pop()
                        found_lparen = True
                        if paren_info.get('is_func', False):
                            func_info = op_stack.pop()
                            arity = arg_counts.pop() if arg_counts else 1
                            rpn.append(RpnItem('func', func_info['name'], arity))
                        break
                    rpn.append(RpnItem(top['type'], top['name'], top.get('arity', 0)))
                    op_stack.pop()

                if not found_lparen:
                    raise ParseError("Несогласованная закрывающая скобка ')'", token.position)

                may_be_unary = False
                self.index += 1
                continue

            raise ParseError(f"Неизвестный токен {token}", token.position)

        if may_be_unary and op_stack:
            last_op = op_stack[-1]
            raise ParseError("Выражение неожиданно заканчивается оператором", last_op.get('pos', len(self.text)))

        while op_stack:
            top = op_stack.pop()
            if top['type'] == 'paren':
                raise ParseError("Несогласованная открывающая скобка '('", top['pos'])
            if top['type'] == 'func':
                raise ParseError(f"Незавершенный вызов функции '{top['name']}'", top['pos'])
            rpn.append(RpnItem(top['type'], top['name'], top.get('arity', 0)))

        if not rpn:
            raise ParseError("Пустое выражение после разбора")

        # Проверка баланса операций и операндов
        depth = 0
        for item in rpn:
            if item.kind in ('num', 'var', 'const'):
                depth += 1
            elif item.kind == 'op':
                if item.arity == 1:
                    if depth < 1:
                        raise ParseError("Недостаточно операндов для унарной операции")
                elif item.arity == 2:
                    if depth < 2:
                        raise ParseError(f"Недостаточно операндов для бинарной операции '{item.value}'")
                    depth -= 1
            elif item.kind == 'func':
                if depth < item.arity:
                    raise ParseError(f"Недостаточно аргументов для функции '{item.value}'")
                depth -= (item.arity - 1)

        if depth != 1:
            raise ParseError("Некорректная структура выражения (пропущен оператор или операнд)")

        return Expression(self.text, rpn)

    def _peek_next(self) -> Optional[Token]:
        if self.index + 1 < len(self.tokens):
            return self.tokens[self.index + 1]
        return None

    def _current(self) -> Optional[Token]:
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return None
