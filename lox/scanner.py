from .token import Token, TokenType

class Scanner:
    keywords = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def __init__(self, source: str, lox):
        self._source = source
        self.lox = lox
        self._tokens : list[Token] = []
        self._start = 0
        self._current = 0
        self._line = 1

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self._start = self._current
            self.scan_token()

        self._tokens.append(self.EOF())
        return self._tokens

    def is_at_end(self) -> bool:
        return self._current >= len(self._source)

    def scan_token(self) -> None:
        c = self.advance()
        if c ==  "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif c == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ",":
            self.add_token(TokenType.COMMA)
        elif c == ".":
            self.add_token(TokenType.DOT)
        elif c == "-":
            self.add_token(TokenType.MINUS)
        elif c == "+":
            self.add_token(TokenType.PLUS)
        elif c == ";":
            self.add_token(TokenType.SEMICOLON)
        elif c == "*":
            self.add_token(TokenType.STAR)
        elif c == "!":
            self.add_token(
                TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == "=":
            self.add_token(
                TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == "<":
            self.add_token(
                TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
        elif c == ">":
            self.add_token(
                TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
        elif c == "/":
            if self.match('/'):
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif c == " " or c == "\r" or c == "\t":
            # ignore whitespaces
            pass
        elif c == "\n":
            self._line += 1
        elif c == '"':
            self.string()
        else:
            if self.is_digit(c):
                self.number()
            elif self.is_alpha(c):
                self.identifier()
            else:
                self.lox.error(self.previous_token(), "Unexpected character.")

    def EOF(self) -> Token:
        return Token(TokenType.EOF, "", None, self._line)

    def previous_token(self) -> Token:
        if len(self._tokens) == 0:
            return self.EOF()
        return self._tokens[-1]

    def identifier(self) -> None:
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        text = self._source[self._start:self._current]
        token_type = self.keywords.get(text)
        if not token_type:
            token_type = TokenType.IDENTIFIER

        self.add_token(token_type)

    def advance(self) -> str:
        current = self._current
        self._current += 1
        return self._source[current]

    def add_token(self, token_type: TokenType, literal = None) -> None:
        text = self._source[self._start:self._current]
        self._tokens.append(Token(token_type, text, literal, self._line))

    def match(self, expected) -> bool:
        if self.is_at_end():
            return False
        if self._source[self._current] != expected:
            return False

        self._current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return '\0'

        return self._source[self._current]

    def peek_next(self) -> str:
        if self._current + 1 >= len(self._source):
            return '\0'

        return self._source[self._current + 1]

    def is_alpha(self, c) -> bool:
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_'

    def is_alpha_numeric(self, c) -> bool:
        return self.is_alpha(c) or self.is_digit(c)

    def is_digit(self, c) -> bool:
        return c >= '0' and c <= '9'

    def string(self) -> None:
        while self.peek() != '"' and self.is_at_end() == False:
            if self.peek() == "\n":
                self._line += 1

            self.advance()

        if self.is_at_end():
            self.lox.error(self.previous_token(), "Unterminated string.")
            return

        self.advance() # The closing "

        value = self._source[self._start + 1:self._current -1]
        self.add_token(TokenType.STRING, value)

    def number(self) -> None:
        while self.is_digit(self.peek()):
            self.advance()

        # Look for a fractional part.
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            # Consume the "."
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(TokenType.NUMBER, float(self._source[self._start:self._current]))

