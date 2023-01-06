from .environment import Environment
from .loxcallable import LoxCallable
from .stmt import Function
from .returnvalue import ReturnValue

class Loxfunction(LoxCallable):
    def __init__(
            self, declaration : Function,
            closure : Environment,
            is_initializer : bool) -> None:
        self.declaration = declaration
        self.closure = closure
        self._is_initializer = is_initializer

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return Loxfunction(self.declaration, environment, self._is_initializer)

    @property
    def arity(self) -> int:
        return len(self.declaration.params)

    def __repr__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

    def __call__(self, interpreter, arguments):
        environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnValue as ret:
            if self._is_initializer:
                return self.closure.get_at(0, "this")
            return ret.value

        if self._is_initializer:
            return self.closure.get_at(0, "this")
