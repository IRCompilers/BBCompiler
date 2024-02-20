from enum import Enum


class TokenType(Enum):
    NUMBER = 1
    STRING = 2
    IDENTIFIER = 3
    FUNCTION = 4
    FOR = 5
    IF = 6
    ELSE = 7
    ELSE_IF = 8
    LET = 9
    RETURN = 10
    BOOLEAN = 11
    WHILE = 12
    OPEN_PARENTHESES = 13
    CLOSE_PARENTHESES = 14
    OPEN_BRACKET = 15
    CLOSE_BRACKET = 16
    OPEN_BRACE = 17
    CLOSE_BRACE = 18
    COMMA = 19
    SEMICOLON = 20
    PLUS = 21
    MINUS = 22
    MULTIPLY = 23
    DIVIDE = 24
    MODULUS = 25
    EQUAL = 26
    NOT_EQUAL = 27
    LESS_THAN = 28
    LESS_THAN_OR_EQUAL = 29
    GREATER_THAN = 30
    GREATER_THAN_OR_EQUAL = 31
    AND = 32
    OR = 33
    NOT = 34
    ASSIGN = 35
    POWER = 36
