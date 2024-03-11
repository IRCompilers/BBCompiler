from src.Common.TokenType import TokenType


class Token:
    def __init__(self, lemma: str, type: TokenType):
        self.Lemma = lemma
        self.Type = type

    def __str__(self):
        return f"Token({self.Lemma}, {self.Type})"
