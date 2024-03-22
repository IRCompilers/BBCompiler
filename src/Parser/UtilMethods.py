from src.Common.ContainerSet import ContainerSet
from src.Common.Compiler import Item, EOF
from src.Common.Automata import State
from src.Parser.SROperations import SROperations
from src.Common.Compiler import Grammar


def compute_local_firsts(firsts, alpha):
    """

    Computes the local firsts for a given alpha

    :param firsts:
    :param alpha:
    :return:
    """
    first_alpha = ContainerSet()

    try:
        alpha_is_epsilon = alpha.IsEpsilon
    except:
        alpha_is_epsilon = False

    if alpha_is_epsilon:
        first_alpha.set_epsilon()

    else:
        for symbol in alpha:
            first_alpha.update(firsts[symbol])
            if not firsts[symbol].contains_epsilon:
                break
        else:
            first_alpha.set_epsilon()

    return first_alpha


def compute_firsts(grammar: Grammar):
    """

    Computes the firsts sets for the given grammar

    :param grammar: Grammar
    :return:
    """
    firsts = {}
    change = True

    for terminal in grammar.terminals:
        firsts[terminal] = ContainerSet(terminal)

    for non_terminal in grammar.nonTerminals:
        firsts[non_terminal] = ContainerSet()

    while change:
        change = False

        for production in grammar.Productions:
            left = production.Left
            alpha = production.Right

            first_left = firsts[left]

            try:
                first_alpha = firsts[alpha]
            except KeyError:
                first_alpha = firsts[alpha] = ContainerSet()

            local_first = compute_local_firsts(firsts, alpha)

            change |= first_alpha.hard_update(local_first)
            change |= first_left.hard_update(local_first)

    return firsts


def expand(item, firsts):
    """

    Expands the given item

    :param item:
    :param firsts:
    :return:
    """
    next_symbol = item.NextSymbol
    if next_symbol is None or not next_symbol.IsNonTerminal:
        return []

    lookaheads = ContainerSet()
    for preview in item.Preview():
        lookaheads.hard_update(compute_local_firsts(firsts, preview))

    assert not lookaheads.contains_epsilon
    return [Item(prod, 0, lookaheads) for prod in next_symbol.productions]


def compress(items):
    '''
    Compresses the given items
    :param items:
    :return:
    '''
    centers = {}

    for item in items:
        center = item.Center()
        try:
            lookaheads = centers[center]
        except KeyError:
            centers[center] = lookaheads = set()
        lookaheads.update(item.lookaheads)

    return {
        Item(x.production, x.pos, set(lookahead)) for x, lookahead in centers.items()
    }


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
    ), "`firsts` values must be provided if `just_kernel=False`"
    items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
    return items if just_kernel else closure_for_lr1(items, firsts)


def build_automaton_for_lr1_parser(grammar: Grammar):
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

