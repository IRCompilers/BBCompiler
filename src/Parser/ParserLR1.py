from src.Parser.ShiftReduceParser import ShiftReduceParser
from src.Parser.UtilMethods import update_table, build_automaton_for_lr1_parser
from src.Parser.SROperations import SROperations


class ParserLR1(ShiftReduceParser):
    def _build_parsing_table(self):
        aug_grammar = self.Grammar.AugmentedGrammar(True)

        if self.goto == {} or self.action == {}:
            pass
        else:
            return

        automaton = build_automaton_for_lr1_parser(aug_grammar)
        for i, node in enumerate(automaton):
            if self.verbose:
                print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                if item.IsReduceItem:
                    prod = item.production
                    if prod.Left == aug_grammar.startSymbol:
                        self.add(self.action, (idx, aug_grammar.EOF), (SROperations.OK, None))
                    else:
                        for lookahead in item.lookaheads:
                            self.add(self.action, (idx, lookahead), (SROperations.REDUCE, prod))
                else:
                    next_symbol = item.NextSymbol
                    if next_symbol.IsTerminal:
                        self.add(self.action, (idx, next_symbol),
                                       (SROperations.SHIFT, node[next_symbol.Name][0].idx))
                    else:
                        self.add(self.goto, (idx, next_symbol), node[next_symbol.Name][0].idx)

    @staticmethod
    def add(table, key, value):
        assert key not in table or table[key] == value, f'Conflict {key} {table[key]} {value}'
        table[key] = value
