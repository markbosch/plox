from enum import Enum
from .expr import Expr, ExprVisitor
from .stmt import Stmt, StmtVisitor
from .token import Token

class FunctionType(Enum):
    NONE = 0,
    FUNCTION = 1,
    INITIALIZER = 2,
    METHOD = 3,

class ClassType(Enum):
    NONE = 0,
    CLASS = 1,
    SUBCLASS = 2,

class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpreter, lox):
        self.interpreter = interpreter
        self.lox = lox
        self.scopes = []
        self.current_function = FunctionType.NONE
        self._current_class = ClassType.NONE

    @property
    def scopes_is_empty(self):
        return len(self.scopes) == 0

    def visit_block_stmt(self, stmt):
        self._begin_scope()
        self.resolve(stmt.statements)
        self._end_scope()

    def resolve(self, statements):
        if isinstance(statements, Stmt):
            statements.accept(self)
        elif isinstance(statements, Expr):
            statements.accept(self)
        else:
            for statement in statements:
                self.resolve(statement)

    def _resolve_local(self, expr, name):
        for i in range(len(self.scopes) -1, -1, -1):
            if name.lexeme in self.scopes[i].keys():
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

    def _resolve_function(self, function, function_type):
        enclosing_function = self.current_function
        self.current_function = function_type

        self._begin_scope()

        for param in function.params:
            self._declare(param)
            self._define(param)

        self.resolve(function.body)
        self._end_scope()

        self.current_function = enclosing_function

    def visit_class_stmt(self, stmt):
        enclosing_class = self._current_class
        self._current_class = ClassType.CLASS

        self._declare(stmt.name)
        self._define(stmt.name)

        if stmt.superclass != None and stmt.name.lexeme == stmt.superclass.name.lexeme:
            self.lox.error(stmt.superclass.name,
                           "A class can't inherit from itself.")

        if stmt.superclass != None:
            self._current_class = ClassType.SUBCLASS
            self.resolve(stmt.superclass)

        if stmt.superclass != None:
            self._begin_scope()
            self.scopes[-1]["super"] = True

        self._begin_scope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self._resolve_function(method, declaration)

        self._end_scope()

        if stmt.superclass != None:
            self._end_scope()

        self._current_class = enclosing_class

    def _begin_scope(self):
        self.scopes.append({})

    def _end_scope(self):
        self.scopes.pop()

    def _declare(self, name: Token):
        if self.scopes_is_empty:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope.keys():
            self.lox.error(
                name, "Already a variable with this name in this scope.")

        scope[name.lexeme] = False

    def _define(self, name: Token):
        if self.scopes_is_empty:
            return

        self.scopes[-1][name.lexeme] = True

    def visit_var_stmt(self, stmt):
        self._declare(stmt.name)
        if stmt.initializer != None:
            self.resolve(stmt.initializer)

        self._define(stmt.name)

    def visit_function_stmt(self, stmt):
        self._declare(stmt.name)
        self._define(stmt.name)
        self._resolve_function(stmt, FunctionType.FUNCTION)

    def visit_expression_stmt(self, stmt):
        self.resolve(stmt.expression)

    def visit_if_stmt(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)

        if stmt.else_branch:
            self.resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt):
        self.resolve(stmt.expression)

    def visit_return_stmt(self, stmt):
        if self.current_function == FunctionType.NONE:
            self.lox.error(stmt.keyword, "Can't return from top-level code.")

        if stmt.value:
            if self.current_function == FunctionType.INITIALIZER:
                self.lox.error(stmt.keyword,
                               "Can't return a value from an initializer")
            self.resolve(stmt.value)

    def visit_while_stmt(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_assign_expr(self, expr):
        self.resolve(expr.value)
        self._resolve_local(expr, expr.name)

    def visit_variable_expr(self, expr):
        if (not self.scopes_is_empty) and self.scopes[-1].get(expr.name.lexeme, None) == False:
            self.lox.error("Can't read local variable in its own initializer.")

        self._resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call_expr(self, expr):
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)

    def visit_group_expr(self, expr):
        self.resolve(expr.expression)

    def visit_logical_expr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_unary_expr(self, expr):
        self.resolve(expr.right)

    def visit_get_expr(self, expr):
        self.resolve(expr.object_)

    def visit_set_expr(self, expr):
        self.resolve(expr.value)
        self.resolve(expr.object_)

    def visit_super_expr(self, expr):
        if self._current_class == ClassType.NONE:
            self.lox.error(expr.keyword,
                           "Can't use 'super' outside a class")
        elif self._current_class != ClassType.SUBCLASS:
            self.lox.error(expr.keyword,
                           "Can't use 'super' in a class with no superclass.")

        self._resolve_local(expr, expr.keyword)

    def visit_this_expr(self, expr):
        if self._current_class == ClassType.NONE:
            self.lox.error(expr.keyword,
                "Can't use 'this' outside of a class.")
            return
        self._resolve_local(expr, expr.keyword)

    def visit_literal_expr(self, expr):
        pass

    def visit_grouping_expr(self, expr):
        pass
