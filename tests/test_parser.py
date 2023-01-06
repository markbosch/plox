import pytest

from lox.expr import Binary
from lox.stmt import Class, Function
from lox.token import Token, TokenType
from lox.parser import Parser
from lox.lox import Lox

@pytest.fixture
def lox():
    return Lox()

def test_parse_one_plus_one(lox):
    tokens = [
        Token(TokenType.NUMBER, "", "1", 1), Token(TokenType.PLUS, "+", None, 1),
        Token(TokenType.NUMBER, "", "1", 1), Token(TokenType.SEMICOLON, ";", None, 1),
        Token(TokenType.EOF, "", None, 1)
    ]
    parser = Parser(tokens, lox)

    expression = parser.parse()

    assert isinstance(expression[-1].expression, Binary)

def test_fun_without_params(lox):
    tokens = [
        Token(TokenType.FUN, 'fun', None, 1), Token(TokenType.IDENTIFIER, 'foo', None, 1),
        Token(TokenType.LEFT_PAREN, '(', None, 1), Token(TokenType.RIGHT_PAREN, ')', None, 1),
        Token(TokenType.LEFT_BRACE, '{', None, 1), Token(TokenType.RIGHT_BRACE, '}', None, 1),
        Token(TokenType.EOF, '', None, 1),
    ]

    parser = Parser(tokens, lox)

    expression = parser.parse()

    assert isinstance(expression[-1], Function)

def test_class(lox):
    tokens = [
        Token(TokenType.CLASS, 'class', None, 1), Token(TokenType.IDENTIFIER, 'Foo', None, 1),
        Token(TokenType.LEFT_BRACE, '{', None, 1), Token(TokenType.RIGHT_BRACE, '}', None, 1),
        Token(TokenType.EOF, '', None, 1),
    ]

    parser = Parser(tokens, lox)

    expression = parser.parse()

    assert isinstance(expression[-1], Class)