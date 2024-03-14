from typing import List

from src.Common.Automata import State
from src.Common.Compiler import Item, Production, NonTerminal
from src.Common.ContainerSet import ContainerSet
from src.Lexer.Parser.Grammar import GetLexerGrammar
from src.Lexer.Parser.Utils import compute_firsts, compute_follows


def build_LR0_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0)

    automaton = State(start_item, True)

    pending = [start_item]
    visited = {start_item: automaton}

    while pending:
        current_item = pending.pop()
        if current_item.IsReduceItem:
            continue

        new_states_non_delta = []
        new_states_delta = []
        next_symbol = current_item.NextSymbol

        if next_symbol.IsTerminal:
            next_item = current_item.NextItem()
            if next_item not in visited:
                pending.append(next_item)
                visited[next_item] = State(next_item, final=True)
            new_states_non_delta.append(next_item)

        else:
            next_item = current_item.NextItem()
            if next_item not in visited:
                pending.append(next_item)
                visited[next_item] = State(next_item, final=True)
            new_states_non_delta.append(next_item)

            for production in next_symbol.productions:
                next_item = Item(production, 0)
                if next_item not in visited:
                    pending.append(next_item)
                    visited[next_item] = State(next_item, final=True)
                new_states_delta.append(next_item)

        current_state = visited[current_item]

        for v in new_states_non_delta:
            current_state.add_transition(next_symbol.Name, visited[v])

        for v in new_states_delta:
            current_state.add_epsilon_transition(visited[v])

    return automaton


class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'

    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()

    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w) -> List[Production]:
        stack = [0]
        cursor = 0
        output = []

        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, '<---||--->', w[cursor:])

            # Your code here!!! (Detect error)

            action, tag = self.action[state, lookahead]

            if action == ShiftReduceParser.SHIFT:
                stack.append(lookahead)
                stack.append(tag)
                cursor += 1
            elif action == ShiftReduceParser.REDUCE:
                production = tag
                left, right = production
                for _ in range(2 * len(right)):
                    stack.pop()
                state = stack[-1]
                stack.append(left)
                stack.append(self.goto[state, left])
                output.append(production)
            elif action == ShiftReduceParser.OK:
                break

        return output


class SLR1Parser(ShiftReduceParser):

    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        firsts = compute_firsts(G)
        follows = compute_follows(G, firsts)

        automaton = build_LR0_automaton(G).to_deterministic()
        for i, node in enumerate(automaton):
            if self.verbose: print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for state in node.state:
                item = state.state
                # Your code here!!!
                # - Fill `self.Action` and `self.Goto` according to `item`)
                # - Feel free to use `self._register(...)`)

                production_left: NonTerminal = item.production.Left
                left_follows: ContainerSet = follows[production_left]

                if item.IsReduceItem:
                    if item.production.Left.Name == G.startSymbol.Name:
                        self._register(self.action, (idx, G.EOF), (ShiftReduceParser.OK, None))
                    else:
                        for symbol in left_follows:
                            self._register(self.action, (idx, symbol), (ShiftReduceParser.REDUCE, item.production))
                else:
                    symbol = item.NextSymbol
                    if symbol.IsTerminal:
                        next_node = node[symbol.Name][0]
                        self._register(self.action, (idx, symbol), (ShiftReduceParser.SHIFT, next_node.idx))
                    else:
                        next_node = node[symbol.Name][0]
                        self._register(self.goto, (idx, symbol), next_node.idx)

    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value


grammar = GetLexerGrammar()
automaton = build_LR0_automaton(grammar)

print(grammar)




parser = SLR1Parser(grammar, verbose=False)

# derivation = parser([num, plus, num, star, num, G.EOF])
# assert str(derivation) == '[F -> int, T -> F, E -> T, F -> int, T -> F, F -> int, T -> T * F, E -> E + T]'
# print("Derivation: ", derivation)
