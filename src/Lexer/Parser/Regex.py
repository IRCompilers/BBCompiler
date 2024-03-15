from typing import List

from src.Common.Automaton import NFA
from src.Common.Token import Token
from src.Lexer.Parser.EvaluateVisitor import EvaluateVisitor
from src.Lexer.Parser.Grammar import GetRegexGrammar
from src.Lexer.Parser.Parser import SLR1Parser, evaluate_reverse_parse


class RegexBuilder:

    def __init__(self):
        self.grammar = GetRegexGrammar()
        self.parser = SLR1Parser(self.grammar)

    def build_regex(self, regex: str) -> (NFA, List[str]):
        tokens = []
        errors = []

        for i, c in enumerate(regex):

            token = [x for x in self.grammar.terminals if x.Name == c]
            if len(token) > 0:
                tokens.append(token[0])
            else:
                errors.append(f"Invalid character {c} on column {i}")

        tokens.append(self.grammar.EOF)
        derivation, operations = self.parser(tokens)
        tokens = [Token(x.Name, x, 0) for x in tokens]
        ast = evaluate_reverse_parse(derivation, operations, tokens)
        evaluator = EvaluateVisitor()
        nfa = evaluator.visit(ast)
        return nfa, errors
