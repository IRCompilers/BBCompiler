from src.Common.ContainerSet import ContainerSet
from src.Common.Compiler import Item
from src.Common.Automata import State


def update_table(table, head, symbol, production) -> bool:
    """
    Updates the parsing table

    :param table: current parsing table
    :param head:
    :param symbol:
    :param production:
    :return:
    Boolean: If the table was updated
    """
    if not head in table:
        table[head] = {}

    if not symbol in table[head]:
        table[head][symbol] = []

    if production not in table[head][symbol]:
        table[head][symbol].append(production)

    return len(table[head][symbol]) <= 1


def closure_for_lr1(items, firsts):
    closure = ContainerSet(*items)

    changed = True
    while changed:
        changed = False

        new_items = ContainerSet()
        for item in closure:
            new_items.extend(expand(item, firsts))

        changed = closure.update(new_items)

    return compress(closure)


def goto_for_lr1(items, symbol, firsts=None, just_kernel=False):
    assert (
        just_kernel or firsts is not None
    ), "`firsts` must be provided if `just_kernel=False`"
    items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
    return items if just_kernel else closure_for_lr1(items, firsts)


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


