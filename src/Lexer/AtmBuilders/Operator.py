from src.Lexer.Utils.Automata import State

UnaryOperators = "+-*/%^"

BinaryOperators = {
    "=": ["=", ">"],
    "!": ["="],
    "<": ["="],
    ">": ["="],
    ":": ["="],
    "&": ["&"],
    "@": ["@"],
    "|": ["|"],
    "*": ["*"],
}


def operator_automaton():
    optr_state = State("Operator")

    optr_unary_final_states = {
        optr: State(f"Operator_{optr}_final", True) for optr in UnaryOperators
    }

    for optr, state in optr_unary_final_states.items():
        state.tag = "Operator"
        optr_state.add_transition(optr, state)

    optr_binary_final_states = {}
    optr_binary_intermediate_states = {}

    for optr, next_chars in BinaryOperators.items():
        for next_char in next_chars:
            if optr not in optr_binary_intermediate_states:
                optr_binary_intermediate_states[optr] = State(
                    f"Operator_{optr}_intermediate", True)

                optr_binary_intermediate_states[optr].tag = "Operator"

            final_state = State(f"Operator_{optr}{next_char}_final", True)
            final_state.tag = "Operator"

            optr_binary_final_states[f"{optr}{next_char}"] = final_state

            optr_state.add_transition(optr, optr_binary_intermediate_states[optr])

            optr_binary_intermediate_states[optr].add_transition(next_char, final_state)

    return optr_state
