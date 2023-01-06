from .token import TokenType
from .expr import Binary, Call, Get, Logical, Set, This, Unary, Literal, Grouping, Variable, Assign, Super
from .stmt import Block, Class, Function, If, Print, Expression, Var, While, Return

class ParseError(RuntimeError):
    pass

class Parser:
    def __init__(self, tokens, lox):
        self.tokens = tokens
        self.current = 0
        self.lox = lox

    def parse(self):
        try:
            statements = []
            while not self._is_at_end():
                statements.append(self._declaration())

            return statements
        except ParseError:
            return None

    def _expression(self):
        return self._assignment()

    def _declaration(self):
        try:
            if self._match(TokenType.CLASS):
                return self._class_declaration()
            if self._match(TokenType.FUN):
                return self._function("function ")
            if self._match(TokenType.VAR):
                return self._var_declaration()

            return self._statement()
        except ParseError:
            self._synchronize()
            return None

    def _class_declaration(self):
        name = self._consume(TokenType.IDENTIFIER, "Expect class name.")

        super_class = None
        if self._match(TokenType.LESS):
            self._consume(TokenType.IDENTIFIER, "Expect superclass name.")
            super_class = Variable(self._previous())

        self._consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            methods.append(self._function("method"))

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return Class(name, super_class, methods)

    def _statement(self):
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.LEFT_BRACE):
            return Block(self._block())

        return self._expression_statement()

    def _for_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        initializer = None
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()

        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after for clause.")

        body = self._statement()
        if increment != None:
            body = Block([body, Expression(increment)])

        if condition is None:
            condition = Literal(True)

        body = While(condition, body)

        if initializer != None:
            body = Block([initializer, body])

        return body

    def _if_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self._statement()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()

        return If(condition, then_branch, else_branch)

    def _print_statement(self):
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def _return_statement(self):
        keyword = self._previous()
        value = None
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def _var_declaration(self):
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def _while_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self._statement()

        return While(condition, body)

    def _expression_statement(self):
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Expression(expr)

    def _function(self, kind: str):
        name = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True: # do while
                if len(parameters) >= 255:
                    self._error(self._peek(), "Can't have more than 255 parameters.")

                parameters.append(self._consume(
                    TokenType.IDENTIFIER, "Expect parameter name."))

                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self._consume(
            TokenType.LEFT_BRACE, "Expect '{' before " + kind + " body.")
        body = self._block()
        return Function(name, parameters, body)

    def _block(self):
        statements = []

        while (not self._check(TokenType.RIGHT_BRACE)) and (not self._is_at_end()):
            statements.append(self._declaration())

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def _assignment(self):
        expr = self._or()

        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                get = expr
                return Set(get.object_, get.name, value)

            self._error(equals, "Invalid assignment target.")

        return expr

    def _or(self):
        expr = self._and()

        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._and()
            expr = Logical(expr, operator, right)

        return expr

    def _and(self):
        expr = self._equality()

        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality()
            expr = Logical(expr, operator, right)

        return expr

    def _equality(self):
        expr = self._comparison()
        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self):
        expr = self._term()

        while self._match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self._previous()
            right = self._term()
            expr = Binary(expr, operator, right)

        return expr

    def _term(self):
        expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self):
        expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self):
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)

        return self._call()

    def _finish_call(self, callee):
        arguments = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True: # simulate a do while
                arguments.append(self._expression())
                if len(arguments) >= 255:
                    self._error(self._peek(), "Can't have more than 255 arguments.")

                if not self._match(TokenType.COMMA):
                    break

        paren = self._consume(TokenType.RIGHT_PAREN,
                                "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def _call(self):
        expr = self._primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name = self._consume(TokenType.IDENTIFIER,
                                     "Expect property name after '.'.")
                expr = Get(expr, name)
            else:
                break

        return expr

    def _primary(self):
        if self._match(TokenType.FALSE):
            return Literal(False)
        if self._match(TokenType.TRUE):
            return Literal(True)
        if self._match(TokenType.NIL):
            return Literal(None)
        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)
        if self._match(TokenType.SUPER):
            keyword = self._previous()
            self._consume(TokenType.DOT, "Expect '.' after 'super'.")
            method = self._consume(TokenType.IDENTIFIER,
                                   "Expect superclass method name.")
            return Super(keyword, method)
        if self._match(TokenType.THIS):
            return This(self._previous())
        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())
        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expext ')' after expression.")
            return Grouping(expr)

        raise self._error(self._peek(), "Expect expression.")

    def _match(self, *token_types):
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True

        return False

    def _check(self, token_type):
        if self._is_at_end():
            return False

        return self._peek().token_type == token_type

    def _advance(self):
        if not self._is_at_end():
            self.current += 1

        return self._previous()

    def _is_at_end(self):
        return self._peek().token_type == TokenType.EOF

    def _peek(self):
        return self.tokens[self.current]

    def _previous(self):
        return self.tokens[self.current - 1]

    def _consume(self, token_type, message):
        if self._check(token_type):
            return self._advance()

        raise self._error(self._peek(), message)

    def _error(self, token, message):
        self.lox.error(token, message)
        return ParseError()

    def _synchronize(self):
        self._advance()

        while not self._is_at_end():
            if self._previous().token_type == TokenType.SEMICOLON:
                return

            token_type = self._peek().token_type
            if token_type == TokenType.CLASS:
                return
            if token_type == TokenType.FUN:
                return
            if token_type == TokenType.VAR:
                return
            if token_type == TokenType.FOR:
                return
            if token_type == TokenType.IF:
                return
            if token_type == TokenType.WHILE:
                return
            if token_type == TokenType.PRINT:
                return
            if token_type == TokenType.RETURN:
                return

            self._advance()
