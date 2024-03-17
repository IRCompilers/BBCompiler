from src.Common.Automaton import DFA
from src.Common.ContainerSet import ContainerSet
from src.Common.DisjointSet import DisjointSet


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


def distinguish_states(group, automaton, partition):
    split = {}
    vocabulary = tuple(automaton.vocabulary)

    for member in group:
        transitions = automaton.transitions[member.value]
        labels = ((transitions[symbol][0] if symbol in transitions else None) for symbol in vocabulary)
        key = tuple((partition[node].representative if node in partition.nodes else None) for node in labels)
        try:
            split[key].append(member.value)
        except KeyError:
            split[key] = [member.value]

    return [group for group in split.values()]


def state_minimization(automaton):
    partition = DisjointSet(*range(automaton.states))
    partition.merge(s for s in automaton.finals)
    partition.merge(s for s in range(automaton.states) if s not in automaton.finals)

    while True:
        new_partition = DisjointSet(*range(automaton.states))
        for group in partition.groups:
            for subgroup in distinguish_states(group, automaton, partition):
                new_partition.merge(subgroup)
        if len(new_partition) == len(partition):
            break
        partition = new_partition

    return partition


def automata_minimization(automaton):
    partition = state_minimization(automaton)
    representatives = [state for state in partition.representatives]
    transitions = {}

    for i, state in enumerate(representatives):
        origin = state.value
        for symbol, destinations in automaton.transitions[origin].items():
            representative = partition[destinations[0]].representative
            j = representatives.index(representative)
            try:
                transitions[i, symbol]
                assert False
            except KeyError:
                transitions[i, symbol] = j

    finals = [i for i, state in enumerate(representatives) if state.value in automaton.finals]
    start = representatives.index(partition[automaton.start].representative)

    return DFA(len(representatives), finals, transitions, start)
