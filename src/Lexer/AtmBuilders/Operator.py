from src.Common.TokenType import TokenType
from src.Common.Automata import State


SingleCharacterOperators = {
    ("+", TokenType.PLUS),
    ("-", TokenType.MINUS),
    ("*", TokenType.MULTIPLY),
    ("/", TokenType.DIVIDE),
    ("%", TokenType.MODULUS)
}

MultiCharacterOperators = {
    ("=", TokenType.EQUAL): [("=", TokenType.DEQUAL)],
    ("!", TokenType.NOT): [("=", TokenType.NOT_EQUAL)],
    ("<", TokenType.LESS_THAN): [("=", TokenType.LESS_THAN_OR_EQUAL)],
    (">", TokenType.GREATER_THAN): [("=", TokenType.GREATER_THAN_OR_EQUAL)],
    (":", TokenType.COLON): [("=", TokenType.ASSIGN)],
    ("&", TokenType.BITWISE_AND): [("&", TokenType.AND)],
    ("|", TokenType.BITWISE_OR): [("|", TokenType.OR)],
    ("*", TokenType.MULTIPLY): [("=", TokenType.POWER)],
}


def operator_automaton():
    optr_state = State("Operator")

    # Single character operators (both standalone and those part of potential multi-char ops)
    for optr, token_type in SingleCharacterOperators:
        state = State(f"Operator_{optr}_final", True)
        state.tag = token_type
        optr_state.add_transition(optr, state)

    # Multi-character Operators (only the extended parts)
    for (optr, initial_token), extensions in MultiCharacterOperators.items():
        intermediate_state = State(f"Operator_{optr}_intermediate", final=True)
        intermediate_state.tag = initial_token
        optr_state.add_transition(optr, intermediate_state)

        for (next_char, token_type) in extensions:
            final_state = State(f"Operator_{optr}{next_char}_final", True)
            final_state.tag = token_type
            intermediate_state.add_transition(next_char, final_state)

    return optr_state
