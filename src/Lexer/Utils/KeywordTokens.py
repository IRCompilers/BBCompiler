from src.Common.TokenType import TokenType

KEYWORD_TOKENS = {
    ("PI", TokenType.PI),
    ("E", TokenType.E),
    ("new", TokenType.NEW),
    ("inherits", TokenType.INHERITS),
    ("true", TokenType.TRUE),
    ("false", TokenType.FALSE),
    ("while", TokenType.WHILE),
    ("for", TokenType.FOR),
    ("range", TokenType.RANGE),
    ("function", TokenType.FUNCTION),
    ("let", TokenType.LET),
    ("in", TokenType.IN),
    ("if", TokenType.IF),
    ("else", TokenType.ELSE),
    ("type", TokenType.TYPE),
    ("self", TokenType.SELF),
    ("protocol", TokenType.PROTOCOL),
    ("extends", TokenType.EXTENDS),
}
