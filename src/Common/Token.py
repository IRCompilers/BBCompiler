from src.Common.TokenType import TokenType


class Token:
    def __init__(self, lemma: str, type: TokenType):
        self.Lemma = lemma
        self.Type = type
