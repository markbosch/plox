import pytest

from lox.lox import Lox
from lox.token import TokenType
from lox.scanner import Scanner

def scan_tokens(source):
    lox = Lox()
    scanner = Scanner(source, lox)
    return scanner.scan_tokens()

def test_scan_token():
    result = scan_tokens('var a = b + c')

    assert result is not None

@pytest.mark.parametrize('source, expected_token_type', 
    (
        ("!", TokenType.BANG),
        ("var", TokenType.VAR), ("and", TokenType.AND),
        ("for", TokenType.FOR), ("-", TokenType.MINUS)
    ))
def test_addition(source, expected_token_type):
    assert scan_tokens(source)[0].token_type == expected_token_type