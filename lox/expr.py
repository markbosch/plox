from abc import ABC, abstractmethod

class Expr(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class ExprVisitor(ABC):

    @abstractmethod
    def visit_assign_expr(self, expr):
        pass

    @abstractmethod
    def visit_binary_expr(self, expr):
        pass

    @abstractmethod
    def visit_call_expr(self, expr):
        pass

    @abstractmethod
    def visit_get_expr(self, expr):
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr):
        pass

    @abstractmethod
    def visit_literal_expr(self, expr):
        pass

    @abstractmethod
    def visit_logical_expr(self, expr):
        pass

    @abstractmethod
    def visit_set_expr(self, expr):
        pass

    @abstractmethod
    def visit_super_expr(self, expr):
        pass

    @abstractmethod
    def visit_this_expr(self, expr):
        pass

    @abstractmethod
    def visit_unary_expr(self, expr):
        pass

    @abstractmethod
    def visit_variable_expr(self, expr):
        pass

class Assign(Expr):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_assign_expr(self)

class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)

class Call(Expr):
    def __init__(self, callee, paren, arguments):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor):
        return visitor.visit_call_expr(self)

class Get(Expr):
    def __init__(self, object_, name):
        self.object_ = object_
        self.name = name

    def accept(self, visitor):
        return visitor.visit_get_expr(self)

class Grouping(Expr):
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)

class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)

class Logical(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_logical_expr(self)

class Set(Expr):
    def __init__(self, object_, name, value):
        self.object_ = object_
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_set_expr(self)

class Super(Expr):
    def __init__(self, keyword, method):
        self.keyword = keyword
        self.method = method

    def accept(self, visitor):
        return visitor.visit_super_expr(self)

class This(Expr):
    def __init__(self, keyword):
        self.keyword = keyword

    def accept(self, visitor):
        return visitor.visit_this_expr(self)

class Unary(Expr):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)

class Variable(Expr):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable_expr(self)
