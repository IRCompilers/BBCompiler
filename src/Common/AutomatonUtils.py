from src.Common.Automaton import DFA, NFA
from src.Common.ContainerSet import ContainerSet


def move(automaton, states, symbol):
    moves = set()
    for state in states:
        try:
            moves.update(automaton.transitions[state][symbol])
        except KeyError:
            pass

    return moves


def epsilon_closure(automaton, states):
    pending = [s for s in states]  # equivalente a list(states) pero me gusta así :p
    closure = {s for s in states}  # equivalente a  set(states) pero me gusta así :p

    while pending:
        state = pending.pop()
        for dest in automaton.epsilon_transitions(state):
            if dest not in closure:
                closure.add(dest)
                pending.append(dest)

    return ContainerSet(*closure)


def nfa_to_dfa(automaton):
    transitions = {}

    start = epsilon_closure(automaton, [automaton.start])
    start.id = 0
    start.is_final = any(s in automaton.finals for s in start)
    states = [start]

    pending = [start]
    while pending:
        state = pending.pop()

        for symbol in automaton.vocabulary:

            next_states = epsilon_closure(automaton, move(automaton, state, symbol))

            if len(next_states) == 0:
                continue

            try:
                transitions[state.id, symbol]
                assert False, 'Invalid DFA!!!'
            except KeyError:

                if not next_states in states:
                    next_states.id = len(states)
                    next_states.is_final = any(s in automaton.finals for s in next_states)
                    states.append(next_states)
                    pending.append(next_states)
                else:
                    next_states.id = states.index(next_states)

                if len(next_states) > 0:
                    transitions[state.id, symbol] = next_states.id

    finals = [state.id for state in states if state.is_final]
    dfa = DFA(len(states), finals, transitions)
    return dfa


