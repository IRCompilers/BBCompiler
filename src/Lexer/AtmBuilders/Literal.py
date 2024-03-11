import string

from src.Lexer.Utils.Automata import State

Letters = string.ascii_letters
Digits = string.digits
Digits_and_Letters = Digits + Letters


def literal_automaton():
    literal_start_state = State("LiteralStart")
    literal_content_state = State("LiteralContent")
    literal_escape_state = State("LiteralEscape")
    literal_end_state = State("FinalLiteral", True)
    literal_end_state.tag = "Literal"

    literal_start_state.add_transition('"', literal_content_state)

    for char in (Digits_and_Letters + string.punctuation.replace('"', "") + " "):
        literal_content_state.add_transition(char, literal_content_state)

    literal_content_state.add_transition("\\", literal_escape_state)
    literal_escape_state.add_transition('"', literal_content_state)

    for char in ("\\", '"', "n", "t", "r"):
        literal_escape_state.add_transition(char, literal_content_state)

    literal_content_state.add_transition('"', literal_end_state)

    return literal_start_state
