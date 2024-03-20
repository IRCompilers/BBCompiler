import os
import pickle
from typing import List

from src.Common.Automata import State
from src.Common.Exceptions import LexerError
from src.Common.Token import Token
from src.Lexer.Parser.Regex import RegexBuilder
from src.Project.Grammar import G


class Lexer:
    def __init__(self, table):

        if os.path.exists("models/lexer_automaton.pkl"):
            with open('models/lexer_automaton.pkl', 'rb') as f:
                self.automaton = pickle.load(f)
        else:
            self.regex_builder = RegexBuilder()
            self.regexs = self._build_regexs(table)
            self.automaton = self._build_automaton()
            with open('models/lexer_automaton.pkl', 'wb') as f:
                pickle.dump(self.automaton, f)

    def _build_regexs(self, table):
        regexs = []
        for n, (token_type, regex) in enumerate(table):
            regex_automata, errors = self.regex_builder.build_regex(regex)
            automata, states = State.from_nfa(regex_automata, get_states=True)

            for state in states:
                if state.final:
                    state.tag = token_type
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

        string_started = False

        for symbol in string:
            if not string_started and symbol == " " or symbol == "\n":
                break

            if symbol == "\"":
                string_started = True

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
        errors: List[LexerError] = []
        text, pos, rows, cols = self.CleanupText("", text, 0, 0)
        while text:
            try:
                final, lex = self._walk(text)
            except TypeError:
                errors.append(LexerError(f"LEXER ERROR: Invalid token \"{text[0]}\" at position: {(rows, cols)}"))
                text, index, rows, cols = self.CleanupText("", text, cols, rows, skip=1)
                pos += index
                cols += 1
                continue

            if final:
                yield Token(lex, final.tag, (rows, cols))

            cols += len(lex)
            text, index, rows, cols = self.CleanupText(lex, text, cols, rows)
            pos += index

        yield Token("$", G.EOF, (rows, cols))

        for e in errors:
            print('\033[91m' + str(e) + '\033[0m')

    @staticmethod
    def CleanupText(lex, text, start_cols, start_rows, skip=0):
        index = len(lex) + skip
        cols = start_cols
        rows = start_rows
        for i, symbol in enumerate(text):
            if i < index:
                continue

            if symbol == " " or symbol == "\t":
                index += 1
                cols += 1
            elif symbol == "\n":
                index += 1
                rows += 1
                cols = 0
            else:
                break

        return text[index:], index, rows, cols

    def __call__(self, text):
        return [token for token in self.Tokenize(text)]

# start_time = time.time()

# Calculate the elapsed time
# lexer = Lexer(regex_table)
# tokens = lexer("let* polish=(36.42).in \n \"this is + 523 =  a great string\": for ; 56.43+@*30.1")
#
# for v in tokens:
#     print(v.Lemma, v.TokenType, v.Pos)
