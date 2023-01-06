from lox.exception import RuntimeException
from lox.token import Token

class LoxInstance:
    def __init__(self, klass) -> None:
        self.klass = klass
        self.fields = { }

    def get(self, name : Token):
        if name.lexeme in self.fields.keys():
            return self.fields[name.lexeme]
        
        method = self.klass.find_method(name.lexeme)
        if method != None:
            return method.bind(self)

        raise RuntimeException(name, f"Undefined property {name.lexeme}.")

    def set(self, name: Token, value):
        self.fields[name.lexeme] = value

    def __repr__(self) -> str:
        return f"{self.klass.name} instance"