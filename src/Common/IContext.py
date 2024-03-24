# Create a context pydantic class to store the context variables and functions, their types and values
from abc import ABC
from typing import List


class Variable:
    def __init__(self, name: str, type: str, value):
        self.name = name
        self.value = value
        self.type = type


class Function:
    def __init__(self, name: str, type: str, value, parameters: list[(str, str)]):
        self.name = name
        self.value = value
        self.parameters = parameters
        self.type = type


class Class:
    def __init__(self, name: str, attributes: List, methods: List[Function]):
        self.name = name
        self.attributes = attributes
        self.methods = methods


class IContext(ABC):
    variables: dict[str, Variable]
    functions: dict[str, Function]
    types: dict[str, Class]

    def has_variable(self, name: str) -> bool:
        pass

    def has_function(self, name: str) -> bool:
        pass

    def has_type(self, name: str) -> bool:
        pass

    def get_variable(self, name: str):
        pass

    def get_function(self, name: str):
        pass

    def get_type(self, name: str):
        pass
