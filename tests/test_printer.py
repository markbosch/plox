from lox.printer import AtsPrinter
from lox.token import Token, TokenType
from lox.expr import Binary, Grouping, Literal, Unary

def test_binary_expression():
    printer = AtsPrinter()
    expression = Binary(
        Literal(1),
        Token(TokenType.PLUS, "+", None, 1),
        Literal(2))

    result = printer.print(expression)

    assert result == '(+ 1 2)'

def test_binary_group_expression():
    printer = AtsPrinter()
    expression = Binary(
        Unary(
            Token(TokenType.MINUS, "-", None, 1),
            Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)))

    result = printer.print(expression)

    assert result == '(* (- 123) (group 45.67))'
