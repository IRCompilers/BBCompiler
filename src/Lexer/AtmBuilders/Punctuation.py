from src.Common.TokenType import TokenType
from src.Common.Automata import State

PUNCTUATION_TOKENS = {
    ("(", TokenType.OPARENT),
    (")", TokenType.CPARENT),
    ("[", TokenType.OBRACKET),
    ("]", TokenType.CBRACKET),
    ("{", TokenType.OBRACE),
    ("}", TokenType.CBRACE),
    (",", TokenType.COMMA),
    (";", TokenType.SEMICOLON),
    (".", TokenType.DOT),
    (":", TokenType.COLON),
}


def punctuation_automaton():
    punctuation_state = State("Punctuation")
    for sign, token_type in PUNCTUATION_TOKENS:
        punctuation_state_final = State("FinalPunctuation", True)
        punctuation_state_final.tag = token_type
        punctuation_state.add_transition(sign, punctuation_state_final)
    return punctuation_state
