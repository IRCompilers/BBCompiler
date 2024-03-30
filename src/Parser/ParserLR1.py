from src.Parser.ShiftReduceParser import ShiftReduceParser
from src.Parser.UtilMethods import build_lr1_automaton
from src.Parser.SROperations import SROperations
import os
import dill
import sys


class ParserLR1(ShiftReduceParser):
    def __init__(self, grammar, verbose=False):
        super().__init__(grammar, verbose)

    def _build_parsing_table(self):
        aug_grammar = self.Grammar.AugmentedGrammar(True)

        if self.goto == {} or self.action == {}:
            pass
        else:
            return

        os.chdir("..")
        file_path = os.path.join(os.getcwd(), "models")
        sys.setrecursionlimit(5000)
        if os.path.exists(f"{file_path}/parser_automaton.pkl"):
            with open(f"{file_path}/parser_automaton.pkl", 'rb') as f:
                self.automaton = dill.load(f)
        else:
            with open(f"{file_path}/parser_automaton.pkl", 'wb') as f:
                self.automaton = build_lr1_automaton(aug_grammar)
                dill.dump(self.automaton, f)

        for i, node in enumerate(self.automaton):
            if self.verbose:
                print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in self.automaton:
            idx = node.idx
            for item in node.state:
                if item.IsReduceItem:
                    prod = item.production
                    if prod.Left == aug_grammar.startSymbol:
                        self._register(self.action, (idx, aug_grammar.EOF), (SROperations.OK, None))
                    else:
                        for lookahead in item.lookaheads:
                            self._register(self.action, (idx, lookahead), (SROperations.REDUCE, prod))
                else:
                    next_symbol = item.NextSymbol
                    if next_symbol.IsTerminal:
                        self._register(self.action, (idx, next_symbol),
                                       (SROperations.SHIFT, node[next_symbol.Name][0].idx))
                    else:
                        self._register(self.goto, (idx, next_symbol), node[next_symbol.Name][0].idx)

        for x, y in self.action.items():
            self.copy[(x[0], str(x[1]))] = y

    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, f'Shift-Reduce or Reduce-Reduce conflict!!! {key} {table[key]} {value} '
        table[key] = value
