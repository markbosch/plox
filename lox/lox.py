# lox.py
import sys

from .scanner import Scanner
from .token import TokenType
from .parser import Parser
from .interpreter import Interpreter
from .resolver import Resolver

class Lox:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
        self.interpreter = Interpreter(self)

    def _report(self, line, where, message):
        print(f'[Line {line}] Error{where}: {message}')

    def error(self, token, message):
        self.had_error = True
        if token.token_type == TokenType.EOF:
            self._report(token.line, " at end", message)
        else:
            self._report(token.line, f" at '{token.lexeme}'", message)

    def runtime_error(self, error):
        print(f"{error.message}\n [line {error.token.line}]")
        self.had_runtime_error = True

    def run_prompt(self):
        while True:
            line = input("> ")
            if not line:
                break

            self.run(line)
            self.had_error = False

    def run_file(self, path: str):
        with open(path) as file:
            data = file.read()
            self.run(data)

        if self.had_error:
            sys.exit(65)
        if self.had_runtime_error:
            sys.exit(70)

    def run(self, line: str):
        scanner = Scanner(line, self)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens, self)
        statements = parser.parse()

        if self.had_error:
            return

        resolver = Resolver(self.interpreter, self)
        resolver.resolve(statements)

        if self.had_error:
            return

        self.interpreter.interpret(statements)

def main():
    l = Lox()
    if len(sys.argv) > 2:
        print("Usage: plox [script]")
    elif len(sys.argv) == 2:
        l.run_file(sys.argv[1])
    else:
        l.run_prompt()

if __name__ == "__main__":
    main()
