from typing import List, Dict, Tuple, Set


class NFA:
    def __init__(self, states: int, finals: List[int], transitions: Dict[Tuple[int, str], List[int]], start: int = 0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = {state: {} for state in range(states)}
        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, '__iter__'), 'Invalid collection of states'
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)
        self.vocabulary.discard('')

    def epsilon_transitions(self, state: int) -> List[int]:
        assert state in self.transitions, 'Invalid state'
        try:
            return self.transitions[state]['']
        except KeyError:
            return []

    def epsilon_closure(self, states: Set[int]) -> Set[int]:
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            for next_state in self.epsilon_transitions(state):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    def move(self, states: Set[int], symbol: str) -> Set[int]:
        next_states = set()
        for state in states:
            try:
                next_states.update(self.transitions[state][symbol])
            except KeyError:
                pass
        return self.epsilon_closure(next_states)

    def recognize(self, string: str) -> bool:
        current_states = self.epsilon_closure({self.start})
        for symbol in string:
            current_states = self.move(current_states, symbol)
        return bool(self.finals.intersection(current_states))


class DFA(NFA):
    def __init__(self, states: int, finals: List[int], transitions: Dict[Tuple[int, str], int], start: int = 0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)

        transitions = {key: [value] for key, value in transitions.items()}
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start

    def _move(self, symbol: str) -> None:
        currentSymbol = self.current

        if symbol not in self.transitions[currentSymbol]:
            raise Exception("Invalid symbol transition")

        self.current = self.transitions[currentSymbol][symbol][0]

    def _reset(self) -> None:
        self.current = self.start

    def recognize(self, string: str) -> bool:
        self._reset()

        try:
            for symbol in string:
                self._move(symbol)
        except Exception:
            return False

        return self.current in self.finals
