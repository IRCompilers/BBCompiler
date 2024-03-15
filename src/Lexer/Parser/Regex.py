from src.Common.Automaton import NFA
from src.Lexer.Parser.Grammar import GetLexerGrammar
from src.Lexer.Parser.Parser import SLR1Parser

grammar = GetLexerGrammar()
parser = SLR1Parser(grammar)


def build_regex(regex: str) -> NFA:
    pass