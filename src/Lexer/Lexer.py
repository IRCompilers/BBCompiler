from src.Common.Token import Token
from src.Common.TokenType import TokenType
from src.Lexer.AtmBuilders.Identifier import identifier_automaton
from src.Lexer.AtmBuilders.Keyword import keyword_automaton
from src.Lexer.AtmBuilders.Literal import literal_automaton
from src.Lexer.AtmBuilders.Number import number_automaton
from src.Lexer.AtmBuilders.Operator import operator_automaton
from src.Lexer.AtmBuilders.Punctuation import punctuation_automaton
from src.Lexer.AtmBuilders.Whitespace import whitespace_automaton
from src.Lexer.Utils.Automata import State


class Lexer:
    def __init__(self):
        self.eof = "$"
        self.regexs = self._build_regex()
        self.automaton = self._build_automaton()

    def _build_regex(self):
        return [
            whitespace_automaton(),
            keyword_automaton(),
            number_automaton(),
            identifier_automaton(),
            operator_automaton(),
            punctuation_automaton(),
            literal_automaton()
        ]

    def _build_automaton(self):
        start = State("start")

        for state in self.regexs:
            start.add_epsilon_transition(state)
        return start.to_deterministic()

    def _walk(self, string):
        state = self.automaton
        final = state if state.final else None
        lex = ""

        for symbol in string:
            if state.has_transition(symbol):
                lex += symbol
                state = state[symbol][0]

                if state.final:
                    final = state
                    final.lex = lex
            else:
                break

        if final:
            return final, final.lex

        return None, lex

    def Tokenize(self, text):
        while text:
            final, lex = self._walk(text)
            text = text[len(lex):]

            if final:
                yield Token(lex, final.tag)

        yield Token("$", TokenType.EOF)

    def __call__(self, text):
        return [token for token in self.Tokenize(text)]
