from src.Parser.ShiftReduceParser import ShiftReduceParser
from src.Parser.UtilMethods import compute_firsts, closure_for_lr1, goto_for_lr1
from src.Parser.SROperations import SROperations
from src.Common.ContainerSet import ContainerSet
from src.Common.Compiler import Item, EOF
from src.Common.Automata import State


class ParserLR1(ShiftReduceParser):
    def build_parsing_table(self):
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


def build_automaton_for_lr1_parser(grammar):
    assert len(grammar.startSymbol.productions) == 1, "Grammar must be augmented"

    firsts = compute_firsts(grammar)
    firsts[grammar.EOF] = ContainerSet(grammar.EOF)

    start_production = grammar.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(grammar.EOF,))
    start = frozenset([start_item])

    closure = closure_for_lr1(start, firsts)
    automaton = State(frozenset(closure), True)

    pending = [start]
    visited = {start: automaton}

    while pending:
        current = pending.pop()
        current_state = visited[current]

        for symbol in grammar.terminals + grammar.nonTerminals:
            items = current_state.state
            kernel = goto_for_lr1(items, symbol, just_kernel=True)
            if not kernel:
                continue
            try:
                next_state = visited[kernel]
            except KeyError:
                closure = goto_for_lr1(items, symbol, firsts)
                next_state = visited[kernel] = State(frozenset(closure), True)
                pending.append(kernel)

            current_state.add_transition(symbol.Name, next_state)

    automaton.set_formatter(lambda x: "")
    return automaton


def evaluate_reverse_parse(right_parse, operations, tokens):
    if not right_parse or not operations or not tokens:
        return

    right_parse = iter(right_parse)
    tokens = iter(tokens)
    stack = []
    for operation in operations:

        if operation == SROperations.SHIFT:
            token = next(tokens)
            stack.append(token)

        elif operation == SROperations.REDUCE:
            production = next(right_parse)
            _, body = production
            attributes = production.attributes
            assert all(
                rule is None for rule in attributes[1:]
            ), "There must be only synthesized attributes."
            rule = attributes[0]

            if len(body):
                synthesized = [None] + stack[-len(body):]
                value = rule(None, synthesized)
                stack[-len(body):] = [value]
            else:
                stack.append(rule(None, None))

        else:
            raise Exception("Invalid action!!!")

    assert len(stack) == 1
    assert isinstance(next(tokens).token_type, EOF)
    return stack[0]
