from src.Common.TokenType import TokenType


class Token:
    def __init__(self, lemma: str, type: TokenType, pos: int):
        self.Lemma = lemma
        self.Type = type
        self.Pos = pos

    def __str__(self):
        return f"Token({self.Lemma}, {self.Type})"
