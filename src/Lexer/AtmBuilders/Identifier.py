import string

from src.Common.TokenType import TokenType
from src.Common.Automata import State

Letters = string.ascii_letters
Digits = string.digits

Digits_and_Letters = Digits + Letters
Digits_Letters_and_Underscore = Digits_and_Letters + "_"
Letters_and_Underscore = Letters + "_"


def identifier_automaton():
    id_state = State("ID")
    id_state_final = State("FinalID", True)
    id_state_final.tag = TokenType.IDENTIFIER
    for i in Letters_and_Underscore:
        id_state.add_transition(i, id_state_final)
    for i in Digits_Letters_and_Underscore:
        id_state_final.add_transition(i, id_state_final)
    return id_state
