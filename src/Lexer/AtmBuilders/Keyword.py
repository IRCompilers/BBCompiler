from src.Common.Automata import State
from src.Lexer.Utils.KeywordTokens import KEYWORD_TOKENS


def keyword_automaton():
    Keyword_start = State("Keyword_start")
    for keyword, token_type in KEYWORD_TOKENS:
        current_state = Keyword_start
        for char in keyword[:-1]:
            next_state = current_state.transitions.get(char)
            if next_state is None:
                next_state = State(f"{char}")
                current_state.add_transition(char, next_state)
            else:
                next_state = next_state[0]
            current_state = next_state

        final_state = State(f"{keyword}_final", True)
        final_state.tag = token_type
        current_state.add_transition(keyword[-1], final_state)

    return Keyword_start
