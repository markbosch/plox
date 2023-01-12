import time

from .loxcallable import LoxCallable
from .expr import Call, Expr, Logical, Variable
from .loxclass import LoxClass
from .loxfunction import Loxfunction
from .loxinstance import LoxInstance
from .stmt import Block, If, Stmt, Var, While, Return
from .token import TokenType
from .environment import Environment
from .exception import RuntimeException
from .returnvalue import ReturnValue

class Interpreter(Expr, Stmt):
    def __init__(self, lox):
        self.lox = lox
        self.globals = Environment()
        self.globals.define("clock", Clock())
        self.environment = self.globals
        self.locals = {}

    def interpret(self, statements):
        try:
            for statement in statements:
                self._execute(statement)
        except RuntimeException as re:
            self.lox.runtime_error(re)

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_grouping_expr(self, expr):
        return self._evaluate(expr.expression)

    def visit_unary_expr(self, expr):
        right = self._evaluate(expr)

        if expr.operator.token_type == TokenType.MINUS:
            self._check_number_operand(expr.operator, right)
            return -float(right)
        if expr.operator.token_type == TokenType.BANG:
            return not self._is_thruthy(right)

        # Unreachable code
        return None

    def visit_binary_expr(self, expr):
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        if expr.operator.token_type == TokenType.GREATER:
            self._check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        if expr.operator.token_type == TokenType.GREATER_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        if expr.operator.token_type == TokenType.LESS:
            self._check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        if expr.operator.token_type == TokenType.LESS_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        if expr.operator.token_type == TokenType.BANG_EQUAL:
            return not self._is_equal(left, right)
        if expr.operator.token_type == TokenType.EQUAL_EQUAL:
            return self._is_equal(left, right)
        if expr.operator.token_type == TokenType.MINUS:
            self._check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        if expr.operator.token_type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)

            raise RuntimeException(expr.operator,
                                    "Operands must be two numbers or two strings.")
        if expr.operator.token_type == TokenType.SLASH:
            self._check_number_operands(expr.operator, left, right)
            return float(left) / float(right)
        if expr.operator.token_type == TokenType.STAR:
            self._check_number_operands(expr.operator, left, right)
            return float(left) * float(right)

    def visit_assign_expr(self, expr):
        value = self._evaluate(expr.value)

        distance = self.locals[expr] if expr in self.locals else None

        if distance != None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

        return value

    def visit_call_expr(self, expr : Call):
        callee = self._evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            arguments.append(self._evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeException(
                expr.paren, "Can only call functions and classes.")

        if len(arguments) != callee.arity:
            raise RuntimeException(expr.paren,
                                    f"Expected {callee.arity} arguments but got {len(arguments)}.")

        return callee.__call__(self, arguments)

    def visit_get_expr(self, expr):
        obj = self._evaluate(expr.object_)

        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)

        raise RuntimeException(expr.name,
            "Only instances have properties.")

    def visit_logical_expr(self, expr : Logical):
        left = self._evaluate(expr.left)

        if expr.operator.token_type == TokenType.OR:
            if self._is_thruthy(left):
                return left
            else:
                if self._is_thruthy(left) == False:
                    return left

        return self._evaluate(expr.right)

    def visit_set_expr(self, expr):
        obj = self._evaluate(expr.object_)

        if not isinstance(obj, LoxInstance):
            raise RuntimeException(expr.name, "Only instances have fields.")

        value = self._evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    def visit_super_expr(self, expr):
        distance = self.locals.get(expr)
        super_class = self.environment.get_at(
            distance, "super")
        obj = self.environment.get_at(
            distance - 1, "this")

        method = super_class.find_method(expr.method.lexeme)

        if method == None:
            raise RuntimeException(expr.method,
                                   f"Undefined property {expr.method.lexeme}.")
        return method.bind(obj)

    def visit_this_expr(self, expr):
        return self._lookup_variable(expr.keyword, expr)

    def visit_variable_expr(self, expr : Variable):
        return self._lookup_variable(expr.name, expr)

    def _lookup_variable(self, name, expr):
        distance = self.locals.get(expr, None)
        if distance != None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def visit_block_stmt(self, stmt : Block):
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_class_stmt(self, stmt):
        super_class = None
        if stmt.superclass != None:
            super_class = self._evaluate(stmt.superclass)
            if not isinstance(super_class, LoxClass):
                raise RuntimeException(stmt.superclass.name,
                                       "Superclass must be a class.")

        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass != None:
            self.environment = Environment(self.environment)
            self.environment.define("super", super_class)

        methods = {}

        for method in stmt.methods:
            func = Loxfunction(method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = func

        klass = LoxClass(stmt.name.lexeme, super_class, methods)

        if super_class != None:
            self.environment = self.environment.enclosing

        self.environment.assign(stmt.name, klass)

    def visit_expression_stmt(self, stmt):
        self._evaluate(stmt.expression)

    def visit_print_stmt(self, stmt):
        value = self._evaluate(stmt.expression)
        print(self._stringify(value))

    def visit_function_stmt(self, stmt):
        func = Loxfunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, func)

    def visit_if_stmt(self, stmt : If):
        if self._is_thruthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch:
            self._execute(stmt.else_branch)

    def visit_return_stmt(self, stmt : Return):
        value = None;
        if stmt.value:
            value = self._evaluate(stmt.value)

        raise ReturnValue(value)

    def visit_var_stmt(self, stmt : Var):
        value = None
        if stmt.initializer:
            value = self._evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt : While):
        while self._is_thruthy(self._evaluate(stmt.condition)):
            self._execute(stmt.body)

    def _evaluate(self, expr):
        return expr.accept(self)

    def _execute(self, stmt):
        stmt.accept(self)

    def resolve(self, expr, depth):
        self.locals[expr] = depth

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment

            for statement in statements:
                self._execute(statement)
        finally:
            self.environment = previous

    def _is_thruthy(self, value):
        if value is None:
            return False
        elif isinstance(value, bool):
            return value
        else:
            return True

    def _is_equal(self, a, b):
        if a == None and b == None:
            return True
        if a == None:
            return False

        return a == b

    def _stringify(self, obj):
        if obj is None:
            return 'nil'

        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[0:len(text) - 2]

            return text

        return str(obj)

    def _check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return

        raise RuntimeException(operator, "Operand must be a number.")

    def _check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return

        raise RuntimeException(operator, "Operands must be numbers.")

class Clock(LoxCallable):
    @property
    def arity(self) -> int:
        return 0

    def __call__(self, interpreter: Interpreter, arguments):
        return time.time()

    def __repr__(self) -> str:
        return "<native fun>"
