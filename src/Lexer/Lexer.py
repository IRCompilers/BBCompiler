from src.Common.Token import Token
from src.Common.TokenType import TokenType
from src.Lexer.SymbolTable import SymbolTable


class Lexer:
    def __init__(self):
        self.symbol_table = SymbolTable

    def Tokenize(self, input_string: str):
        tokens = []
        for v in input_string.split():
            tokens.append(Token(v, TokenType.IDENTIFIER))

        return tokens
