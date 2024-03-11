from enum import Enum


class TokenType(Enum):
    # Regex
    NUMBER = 1
    IDENTIFIER = 2
    STRING = 18

    # Operators
    PLUS = 3
    MINUS = 4
    MULTIPLY = 5
    DIVIDE = 6
    EQUAL = 7
    LESS_THAN = 8
    LESS_THAN_OR_EQUAL = 9
    GREATER_THAN = 10
    GREATER_THAN_OR_EQUAL = 11
    DEQUAL = 30
    NOT_EQUAL = 31
    AND = 32
    OR = 33
    NOT = 34
    POWER = 35
    ASSIGN = 36
    MODULUS = 37
    BITWISE_AND = 51
    BITWISE_OR = 52

    # Keywords
    FOR = 12
    LET = 13
    IF = 14
    ELSE = 15
    WHILE = 16
    ELSE_IF = 17
    RETURN = 28
    FUNCTION = 29
    PI = 39
    E = 40
    NEW = 41
    INHERITS = 42
    PROTOCOL = 43
    TYPE = 44
    SELF = 45
    IN = 46
    RANGE = 47
    TRUE = 48
    FALSE = 49
    EXTENDS = 50

    # Punctuation
    OPARENT = 19
    CPARENT = 20
    OBRACKET = 21
    CBRACKET = 22
    OBRACE = 23
    CBRACE = 24
    COMMA = 25
    SEMICOLON = 26
    COLON = 27
    DOT = 38

    # Misc
    EOF = 100
