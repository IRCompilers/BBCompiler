import os
import pickle
from typing import List

import dill

from src.Common.Automata import State
from src.Common.Exceptions import LexerError
from src.Common.Token import Token
from src.Lexer.Parser.Regex import RegexBuilder
from src.Lexer.SymbolTable import regex_table
from src.Project.Grammar import G


class Lexer:
    def __init__(self, table, file_path=None):
        if not file_path:
            file_path = "../../models/lexer_automaton.pkl"

        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                self.automaton = dill.load(f)
        else:
            self.regex_builder = RegexBuilder()
            self.regexs = self._build_regexs(table)
            self.automaton = self._build_automaton()
            with open(file_path, 'wb') as f:
                dill.dump(self.automaton, f)

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

    def _walk(self, string, start_index):
        state = self.automaton
        final = state if state.final else None
        lex = ""
        index = start_index

        while index < len(string):
            symbol = string[index]

            if state.has_transition(symbol):
                lex += symbol
                state = state[symbol][0]

                if state.final:
                    final = state
                    final.lex = lex
            else:
                break

            index += 1

        if final:
            return final, final.lex, index

    @staticmethod
    def CleanupText(start_index, text, start_cols, start_rows, skip=0):
        index = start_index + skip
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

        return index, rows, cols

    def Tokenize(self, text):
        tokens = []
        errors: List[LexerError] = []
        index, rows, cols = self.CleanupText(0, text, 0, 0)
        while index < len(text):
            try:
                final, lex, end_index = self._walk(text, index)
            except TypeError:
                errors.append(LexerError(f"LEXER ERROR: Invalid token \"{text[index]}\" at position: {(rows, cols)}"))
                index, rows, cols = self.CleanupText(index, text, cols, rows, skip=1)
                cols += 1
                continue
            except AttributeError:
                continue

            if not final:
                continue

            tokens.append(Token(lex, final.tag, (rows, cols)))

            cols += len(lex)
            index = end_index
            index, rows, cols = self.CleanupText(index, text, cols, rows)

        tokens.append(Token("$", G.EOF, (rows, cols)))

        return tokens, errors
