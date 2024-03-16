import time

from src.Common.Automata import State
from src.Common.Token import Token
from src.Lexer.Parser.Regex import RegexBuilder
from src.Lexer.Parser.SymbolTable import regex_table
from src.Project.Grammar import G


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
                if state.final:
                    state.tag = (n, token_type)
                else:
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

            if symbol == " " or symbol == "\n":
                break

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

    def Tokenize(self, text):
        text, pos = self.CleanupText("", text)
        while text:
            final, lex = self._walk(text)
            text, index = self.CleanupText(lex, text)
            if final:
                yield Token(lex, final.tag, pos)

            pos += index

        yield Token("$", G.EOF, pos)

    @staticmethod
    def CleanupText(lex, text):
        index = len(lex)
        for i, symbol in enumerate(text):
            if i < index:
                continue

            if symbol == " " or symbol == "\n":
                index += 1
            else:
                break

        return text[index:], index

    def __call__(self, text):
        return [token for token in self.Tokenize(text)]


start_time = time.time()

# Calculate the elapsed time
lexer = Lexer(regex_table)
end_time = time.time()
elapsed_time = end_time - start_time
tokens = lexer("for v in range for let 12.54let 94 1\n   4532 ")
after_lex_time = time.time()
elapsed_lex_time = after_lex_time - elapsed_time
tokens = lexer("for v in range for let 12.54let 94 1\n   4532 ")
after_lex_time_second = time.time()
elapsed_lex_time_second = after_lex_time_second - elapsed_lex_time

print("Elapsed: ", elapsed_time)
print("Elapsed lex: ", elapsed_lex_time)
print("Elapsed lex second: ", elapsed_lex_time_second)

for v in tokens:
    print(v.Lemma, v.TokenType, v.Pos)
