from typing import Any


from src.Common.Compiler import Terminal


class Token:
    def __init__(self, lemma: str, token_type: Terminal, pos: int):
        self.Lemma = lemma
        self.TokenType = token_type
        self.Pos = pos
