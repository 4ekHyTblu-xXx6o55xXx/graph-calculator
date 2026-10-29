import math
from typing import Dict, Callable, Optional
from src.parser import Expression, RpnItem


class EvaluationError(Exception):
    pass


class MathDomainError(EvaluationError):
    pass


class Evaluator:
    CONSTANTS = {
        'pi': math.pi,
        'e': math.e,
    }

    def __init__(self):
        # Функции 1 аргумента
        self.functions_1arg: Dict[str, Callable[[float], float]] = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': self._tan,
            'cot': self._cot,
            'asin': self._asin,
            'acos': self._acos,
            'atan': math.atan,
            'sqrt': self._sqrt,
            'cbrt': self._cbrt,
            'abs': abs,
            'ln': self._ln,
            'log': self._ln,
            'log10': self._log10,
            'log2': self._log2,
            'exp': self._exp,
            'floor': math.floor,
            'ceil': math.ceil,
            'sinh': math.sinh,
            'cosh': math.cosh,
        }

        # Функции 2 аргументов
        self.functions_2arg: Dict[str, Callable[[float, float], float]] = {
            'min': min,
            'max': max,
            'pow': self._pow,
            'hypot': math.hypot,
            'atan2': math.atan2,
        }

    @staticmethod
    def _tan(x: float) -> float:
        c = math.cos(x)
        if abs(c) < 1e-15:
            raise MathDomainError(f"Тангенс не определен при x = {x}")
        return math.tan(x)

    @staticmethod
    def _cot(x: float) -> float:
        s = math.sin(x)
        if abs(s) < 1e-15:
            raise MathDomainError(f"Котангенс не определен при x = {x}")
        return math.cos(x) / s

    @staticmethod
    def _sqrt(x: float) -> float:
        if x < 0:
            raise MathDomainError(f"Квадратный корень из отрицательного числа: {x}")
        return math.sqrt(x)

    @staticmethod
    def _cbrt(x: float) -> float:
        if hasattr(math, 'cbrt'):
            return math.cbrt(x)
        return math.copysign(abs(x) ** (1.0 / 3.0), x)

    @staticmethod
    def _ln(x: float) -> float:
        if x <= 0:
            raise MathDomainError(f"Логарифм определен только для положительных чисел: {x}")
        return math.log(x)

    @staticmethod
    def _log10(x: float) -> float:
        if x <= 0:
            raise MathDomainError(f"Десятичный логарифм определен только для положительных чисел: {x}")
        return math.log10(x)

    @staticmethod
    def _log2(x: float) -> float:
        if x <= 0:
            raise MathDomainError(f"Двоичный логарифм определен только для положительных чисел: {x}")
        return math.log2(x)

    @staticmethod
    def _asin(x: float) -> float:
        if not (-1.0 <= x <= 1.0):
            raise MathDomainError(f"Арксинус определен на отрезке [-1, 1], получено: {x}")
        return math.asin(x)

    @staticmethod
    def _acos(x: float) -> float:
        if not (-1.0 <= x <= 1.0):
            raise MathDomainError(f"Арккосинус определен на отрезке [-1, 1], получено: {x}")
        return math.acos(x)

    @staticmethod
    def _exp(x: float) -> float:
        try:
            return math.exp(x)
        except OverflowError:
            raise EvaluationError(f"Численное переполнение в exp({x})")

    @classmethod
    def _pow(cls, base: float, exp: float) -> float:
        if base == 0 and exp < 0:
            raise MathDomainError("Деление на ноль: возведение 0 в отрицательную степень")
        if base < 0 and not exp.is_integer():
            raise MathDomainError(f"Возведение отрицательного числа {base} в нецелую степень {exp}")
        try:
            return math.pow(base, exp)
        except OverflowError:
            raise EvaluationError(f"Численное переполнение при возведении {base}^{exp}")

    def evaluate(self, expr: Expression, context: Optional[Dict[str, float]] = None) -> float:
        ctx = context or {}
        normalized_ctx = {k.lower(): v for k, v in ctx.items()}
        stack: list[float] = []

        for item in expr.rpn:
            if item.kind == 'num':
                stack.append(float(item.value))

            elif item.kind == 'const':
                const_name = str(item.value).lower()
                if const_name in self.CONSTANTS:
                    stack.append(self.CONSTANTS[const_name])
                else:
                    raise EvaluationError(f"Неизвестная константа: {item.value}")

            elif item.kind == 'var':
                var_name = str(item.value)
                var_lower = var_name.lower()
                if var_lower in normalized_ctx:
                    stack.append(float(normalized_ctx[var_lower]))
                else:
                    raise EvaluationError(f"Переменная '{var_name}' не определена")

            elif item.kind == 'op':
                op_name = item.value
                if item.arity == 1:
                    if not stack:
                        raise EvaluationError("Недостаточно операндов")
                    arg = stack.pop()
                    if op_name == 'neg':
                        stack.append(-arg)
                    elif op_name == 'pos':
                        stack.append(+arg)
                    else:
                        raise EvaluationError(f"Неизвестный оператор '{op_name}'")

                elif item.arity == 2:
                    if len(stack) < 2:
                        raise EvaluationError(f"Недостаточно операндов для '{op_name}'")
                    b = stack.pop()
                    a = stack.pop()

                    if op_name == '+':
                        res = a + b
                    elif op_name == '-':
                        res = a - b
                    elif op_name == '*':
                        res = a * b
                    elif op_name == '/':
                        if b == 0:
                            raise MathDomainError("Деление на ноль")
                        res = a / b
                    elif op_name == '%':
                        if b == 0:
                            raise MathDomainError("Деление на ноль")
                        res = a % b
                    elif op_name == '^':
                        res = self._pow(a, b)
                    else:
                        raise EvaluationError(f"Неизвестный оператор '{op_name}'")

                    if math.isnan(res) or math.isinf(res):
                        raise EvaluationError("Результат не является числом")
                    stack.append(res)

            elif item.kind == 'func':
                func_name = str(item.value).lower()
                arity = item.arity

                if arity == 1:
                    if not stack:
                        raise EvaluationError(f"Нет аргумента для функции '{func_name}'")
                    arg = stack.pop()
                    if func_name in self.functions_1arg:
                        res = self.functions_1arg[func_name](arg)
                    else:
                        raise EvaluationError(f"Неизвестная функция '{func_name}'")
                    stack.append(res)

                elif arity == 2:
                    if len(stack) < 2:
                        raise EvaluationError(f"Недостаточно аргументов для '{func_name}'")
                    arg2 = stack.pop()
                    arg1 = stack.pop()
                    if func_name in self.functions_2arg:
                        res = self.functions_2arg[func_name](arg1, arg2)
                    else:
                        raise EvaluationError(f"Неизвестная функция '{func_name}'")
                    stack.append(res)

                else:
                    raise EvaluationError(f"Неподдерживаемая арность ({arity}) для '{func_name}'")

        if len(stack) != 1:
            raise EvaluationError("Некорректное выражение")

        result = stack[0]
        if math.isnan(result) or math.isinf(result):
            raise EvaluationError("Результат вычисления не является числом")

        return result
