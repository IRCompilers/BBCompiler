from src.Common.IContext import IContext


class CodeContext(IContext):
    def __init__(self, parent: IContext = None):
        self.parent = parent
        self.variables = {}
        self.functions = {}
        self.types = {}

    def has_variable(self, name: str) -> bool:
        return name in self.variables or (self.parent and self.parent.has_variable(name))

    def has_function(self, name: str) -> bool:
        return name in self.functions or (self.parent and self.parent.has_function(name))

    def has_type(self, name: str) -> bool:
        return name in self.types or (self.parent and self.parent.has_type(name))

    def get_variable(self, name: str):
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get_variable(name)

        return None
