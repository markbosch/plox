from .expr import ExprVisitor

class AtsPrinter(ExprVisitor):
    def print(self, expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_assign_expr(self, expr):
        pass

    def visit_call_expr(self, expr):
        pass

    def visit_get_expr(self, expr):
        pass

    def visit_grouping_expr(self, expr):
        return self.parenthesize('group', expr.expression)

    def visit_literal_expr(self, expr):
        if expr.value == None:
            return 'nil'

        return expr.value

    def visit_logical_expr(self, expr):
        pass

    def visit_set_expr(self, expr):
        pass

    def visit_super_expr(self, expr):
        pass

    def visit_this_expr(self, expr):
        pass

    def visit_unary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def visit_variable_expr(self, expr):
        pass

    def parenthesize(self, name: str, *exprs):
        result = f"({name}"
        for expr in exprs:
            result += f" {expr.accept(self)}"

        result += ")"
        return result
