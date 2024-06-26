from src.Common.ContainerSet import ContainerSet
from src.Common.Compiler import Item, EOF
from src.Common.Automata import State
from src.Parser.SROperations import SROperations


def multiline_formatter(state):
    return '\n'.join(str(item) for item in state)


def compute_firsts(grammar):
    """
    Computes the firsts sets for the given grammar

    :param grammar: Grammar
    :return: dict
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
            x = production.Left
            alpha = production.Right

            first_x = firsts[x]

            try:
                first_alpha = firsts[alpha]
            except KeyError:
                first_alpha = firsts[alpha] = ContainerSet()

            local_first = compute_local_first(firsts, alpha)

            change |= first_alpha.hard_update(local_first)
            change |= first_x.hard_update(local_first)

    return firsts


def expand(item, firsts):
    """
    Expands the given item

    :param item:
    :param firsts:
    :return: list
    """
    next_symbol = item.NextSymbol
    if next_symbol is None or not next_symbol.IsNonTerminal:
        return []

    lookaheads = ContainerSet()
    for preview in item.Preview():
        lookaheads.hard_update(compute_local_first(firsts, preview))

    assert not lookaheads.contains_epsilon
    return [Item(prod, 0, lookaheads) for prod in next_symbol.productions]


def compress(items):
    """
    Compresses the given items
    :param items:
    :return: set
    """
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


def compute_local_first(firsts, alpha):
    """
    Computes the local firsts for a given alpha

    :param firsts:
    :param alpha:
    :return: ContainerSet
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


def build_lr1_automaton(grammar):
    """
    Build the automaton for the LR1 parser

    :param grammar: Grammar
    :return: State
    """
    assert len(grammar.startSymbol.productions) == 1, "Grammar must be augmented"

    firsts = compute_firsts(grammar)
    firsts[grammar.EOF] = ContainerSet(grammar.EOF)

    start_production = grammar.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(grammar.EOF,))
    start = frozenset([start_item])

    closure = closure_lr1(start, firsts)
    automaton = State(frozenset(closure), True)

    pending = [start]
    visited = {start: automaton}

    while pending:
        current = pending.pop()
        current_state = visited[current]

        for symbol in grammar.terminals + grammar.nonTerminals:
            items = current_state.state
            kernel = goto_lr1(items, symbol, just_kernel=True)
            if not kernel:
                continue
            try:
                next_state = visited[kernel]
            except KeyError:
                closure = goto_lr1(items, symbol, firsts)
                next_state = visited[kernel] = State(frozenset(closure), True)
                pending.append(kernel)

            current_state.add_transition(symbol.Name, next_state)

    automaton.set_formatter(multiline_formatter)
    return automaton


def closure_lr1(items, firsts):
    """
    It makes the closure for LR1 parser

    :param items:
    :param firsts:
    :return: set
    """
    closure = ContainerSet(*items)
    changed = True
    while changed:
        changed = False
        new_items = ContainerSet()
        for item in closure:
            new_items.extend(expand(item, firsts))
        changed = closure.update(new_items)

    return compress(closure)


def goto_lr1(items, symbol, firsts=None, just_kernel=False):
    """
    `Goto` of LR1 parser

    :param items:
    :param symbol:
    :param firsts:
    :param just_kernel:
    :return: frozenset | set
    """
    assert (
        just_kernel or firsts is not None
    ), "`firsts` must be provided if `just_kernel=False`"
    items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
    return items if just_kernel else closure_lr1(items, firsts)


def evaluate_reverse_parse(right_parse, operations, tokens):
    """
    Evaluate the operations of the parser to build the AST

    :param right_parse:
    :param operations:
    :param tokens:
    :return:
    """
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
            print("Invalid action!!!")
            return None, "Invalid Operation"

    if not len(stack) == 1:
        print(f'Stack:{stack}')
        return None, "Invalid AST construction"
    if not isinstance(next(tokens).TokenType, EOF):
        print('Next Token is not EOF')
        return None, "Invalid AST construction"
    return stack[0], None
