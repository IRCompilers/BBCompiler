from src.Common.Automaton import NFA


def automata_union(a1, a2):
    transitions = {}

    start = 0
    d1 = 1
    d2 = a1.states + d1
    final = a2.states + d2

    for (origin, symbol), destinations in a1.map.items():
        # Relocate a1 transitions ...
        new_origins = [origin + d1] if origin != a1.start else [0, origin + d1]
        for new_origin in new_origins:
            new_destinations = [dest + d1 for dest in destinations]
            transitions[(new_origin, symbol)] = new_destinations

    for (origin, symbol), destinations in a2.map.items():
        # Relocate a2 transitions ...
        new_origins = [origin + d2] if origin != a2.start else [0, origin + d2]
        for new_origin in new_origins:
            new_destinations = [dest + d2 for dest in destinations]
            transitions[(new_origin, symbol)] = new_destinations

    # Add transitions from start state ...
    transitions[(start, '')] = [a1.start + d1, a2.start + d2]

    # Add transitions to final state ...
    for state in a1.finals:
        transitions[(state + d1, '')] = [final]
    for state in a2.finals:
        transitions[(state + d2, '')] = [final]

    states = a1.states + a2.states + 2
    finals = {final}

    return NFA(states, finals, transitions, start)


def automata_concatenation(a1, a2):
    transitions = {}
    start = 0
    d1 = 0
    d2 = a1.states + d1
    final = a2.states + d2

    # Relocate a1 transitions
    for (origin, symbol), destinations in a1.map.items():
        for destination in destinations:
            transitions[(origin + d1, symbol)] = {dest + d1 for dest in destinations}

    # Relocate a2 transitions
    for (origin, symbol), destinations in a2.map.items():
        for destination in destinations:
            transitions[(origin + d2, symbol)] = {dest + d2 for dest in destinations}

    # Add transitions to final state
    for final_state in a1.finals:
        transitions[(final_state + d1, '')] = {d2}

    for state in a2.finals:
        transitions[(state + d2, '')] = {final}

    states = a1.states + a2.states + 1
    finals = {final}
    return NFA(states, finals, transitions, start)


def automata_closure(a1):
    transitions = {}

    start = 0
    d1 = 1
    final = a1.states + d1

    for (origin, symbol), destinations in a1.map.items():
        new_origin = origin + d1
        new_destinations = [dest + d1 for dest in destinations]
        transitions[(new_origin, symbol)] = new_destinations

    transitions[(start, '')] = [a1.start + d1, final]

    for final_state in a1.finals:
        transitions[(final_state + d1, '')] = [start, final]

    states = a1.states + 2
    finals = {final}

    return NFA(states, finals, transitions, start)


a1 = NFA(states=3, finals=[2], transitions={(0, 'b'): [0], (0, 'a'): [1], (1, 'b'): [2]})
a2 = NFA(states=2, finals=[1], transitions={(0, 'a'): [1]})

union = automata_union(a1, a2)

print(union.transitions)
