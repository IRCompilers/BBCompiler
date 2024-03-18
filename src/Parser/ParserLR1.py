from src.Parser.ShiftReduceParser import ShiftReduceParser
from src.Parser.UtilMethods import update_table


class ParserLR1(ShiftReduceParser):
    def _build_parsing_table(self):
        self.ok = True
        aug_grammar = self.Augmented = self.Grammar.AugmentedGrammar(True)

        automaton = self.automaton = build_LR1_automaton(aug_grammar)
        for i, node in enumerate(automaton):
            if self.verbose:
                print(i, "\t", "\n\t ".join(str(x) for x in node.state), "\n")
            node.idx = i
            node.tag = f"I{i}"

        for node in automaton:
            idx = node.idx
            for item in node.state:
                if item.IsReduceItem:
                    prod = item.production
                    if prod.Left == aug_grammar.startSymbol:
                        self.ok &= update_table(
                            self.action, idx, aug_grammar.EOF, (ShiftReduceParser.OK, "")
                        )
                    else:
                        for lookahead in item.lookaheads:
                            self.ok &= update_table(
                                self.action,
                                idx,
                                lookahead,
                                (ShiftReduceParser.REDUCE, prod),
                            )
                else:
                    next_symbol = item.NextSymbol
                    if next_symbol.IsTerminal:
                        self.ok &= update_table(
                            self.action,
                            idx,
                            next_symbol,
                            (ShiftReduceParser.SHIFT, node[next_symbol.Name][0].idx),
                        )
                    else:
                        self.ok &= update_table(
                            self.goto, idx, next_symbol,
                            node[next_symbol.Name][0].idx
                        )
