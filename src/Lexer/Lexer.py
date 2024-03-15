from src.Common.Automata import State
from src.Common.Token import Token
from src.Common.TokenType import TokenType
from src.Lexer.Parser.Regex import RegexBuilder
from src.Lexer.Parser.SymbolTable import regex_table


class Lexer:
    def __init__(self, table):
        self.regex_builder = RegexBuilder()
        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()

    def _build_regexs(self, table):
        regexs = []
        for n, (token_type, regex) in enumerate(table):
            regex_automata, errors = self.regex_builder.build_regex(regex)
            automata, states = State.from_nfa(regex_automata, get_states=True)

            for state in states:
                if state.final and state.tag is None:
                    state.tag = (n, token_type)
                elif not state.final:
                    state.tag = None

            regexs.append(automata)

        return regexs

    def _build_automaton(self):
        start = State('start')

        for automata in self.regexs:
            start.add_epsilon_transition(automata)

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
        pos = 0
        while text:
            final, lex = self._walk(text)
            print(lex)
            text = text[len(lex):]
            if final:
                yield Token(lex, final.tag, pos)

            pos += len(lex)

        yield Token("$", TokenType.EOF, pos)

    def __call__(self, text):
        return [token for token in self.Tokenize(text)]


lexer = Lexer(regex_table)
tokens = lexer("124414")
print(tokens)
