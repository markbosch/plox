from .token import Token
from .exception import RuntimeException

class Environment:
    def __init__(self, enclosing=None):
        self.values = { }
        self.enclosing = enclosing

    def get(self, name : Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing != None:
            return self.enclosing.get(name)

        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance, name):
        return self._ancestor(distance).values.get(name)

    def define(self, name, value):
        self.values[name] = value

    def assign(self, name : Token, value : any):
        if name.lexeme in self.values:
            self.define(name.lexeme, value)
            return

        if self.enclosing != None:
            self.enclosing.assign(name, value)
            return

        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, distance, name : Token, value):
        self._ancestor(distance).values[name.lexeme] = value

    def _ancestor(self, distance):
        environment = self
        for _ in range(distance):
            environment = environment.enclosing

        return environment
