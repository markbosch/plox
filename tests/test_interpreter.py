import pytest

from lox.stmt import Class, Expression, Function, Print, Var
from lox.expr import Binary, Literal, Variable
from lox.token import TokenType, Token
from lox.interpreter import Interpreter
from lox.lox import Lox

@pytest.fixture
def lox():
    return Lox()

@pytest.fixture
def interpreter(lox):
    return Interpreter(lox)

def test_less(interpreter, lox):
    left = Literal(1)
    operator = Token(TokenType.LESS, '>', '', 1)
    right = Literal(2)
    binary = Binary(left, operator, right)
    expression = Expression(binary)

    interpreter.interpret([expression])

    assert lox.had_error == False

def test_variable(interpreter, lox):
    # var foo = "foo"
    name = Token(TokenType.IDENTIFIER, 'foo', None, 1)
    initializer = Literal("foo")
    variable = Var(name, initializer)

    interpreter.interpret([variable])

    assert lox.had_error == False

def test_fun_with_param(interpreter, lox):
    # fun foo(a) { print a; }
    # Arrange
    name = Token(TokenType.IDENTIFIER, 'foo', None, 1)
    param = Token(TokenType.IDENTIFIER, 'a', None, 1)
    body = Print(Variable(name))
    expression = Function(name, param, body)

    # Act
    interpreter.interpret([expression])

    # Assert
    assert lox.had_error == False

def test_fun_without_param(interpreter, lox):
    # fun foo() { print "foo"; }
    name = Token(TokenType.IDENTIFIER, "foo", None, 1)
    body = Print(Literal("foo"))
    expression = Function(name, None, body)

    interpreter.interpret([expression])

    assert lox.had_error == False

def test_class_declartion(interpreter, lox):
    token = Token(TokenType.IDENTIFIER, "Foo", None, 1)
    expression = Class(token, None, [])

    interpreter.interpret([expression])

    assert lox.had_error == False
