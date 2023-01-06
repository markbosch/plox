from .loxcallable import LoxCallable
from .loxinstance import LoxInstance

class LoxClass(LoxCallable):
    def __init__(self, name : str, superclass, methods):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def __call__(self, interpreter, arguments):
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer != None:
            initializer.bind(instance).__call__(interpreter, arguments)

        return instance

    def find_method(self, name):
        if name in self.methods.keys():
            return self.methods[name]

        if self.superclass != None:
            return self.superclass.find_method(name)

        return None

    @property
    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer == None:
            return 0;

        return initializer.arity

    def __repr__(self) -> str:
        return f'{self.name}'
