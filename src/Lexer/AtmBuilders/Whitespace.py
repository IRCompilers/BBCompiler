from src.Common.Automata import State


def whitespace_automaton():
    ws_state = State("Whitespace")
    for ws_char in " \t\n":
        ws_state.add_transition(ws_char, ws_state)
    return ws_state