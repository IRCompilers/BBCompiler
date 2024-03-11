from src.Common.TokenType import TokenType
from src.Lexer.Utils.Automata import State

digits = "0123456789"


def number_automaton():
    num_state = State("Number")
    num_int_part = State("IntPart", True)
    num_int_part.tag = TokenType.NUMBER
    num_decimal_part = State("DecimalPart")
    num_decimal_part_final = State("FinalDecimalPart", True)
    num_decimal_part_final.tag = TokenType.NUMBER
    num_exp_part = State("ExpPart")
    num_exp_sign = State("ExpSign")
    num_state_final = State("FinalNumb", True)
    num_state_final.tag = TokenType.NUMBER
    sign_state = State("Sign")

    num_state.add_transition("-", sign_state)
    num_state.add_transition("+", sign_state)
    for i in digits:
        sign_state.add_transition(i, num_int_part)
        num_state.add_transition(i, num_int_part)
        num_int_part.add_transition(i, num_int_part)

    num_int_part.add_transition("e", num_exp_part)
    num_int_part.add_transition("E", num_exp_part)
    num_int_part.add_transition("e", num_exp_part)
    num_int_part.add_transition("E", num_exp_part)

    num_int_part.add_transition(".", num_decimal_part)

    for digit in digits:
        num_decimal_part.add_transition(digit, num_decimal_part_final)
        num_decimal_part_final.add_transition(digit, num_decimal_part_final)

    num_decimal_part_final.add_transition("e", num_exp_part)
    num_decimal_part_final.add_transition("E", num_exp_part)
    num_decimal_part_final.add_transition("e", num_exp_part)
    num_decimal_part_final.add_transition("E", num_exp_part)

    num_exp_part.add_transition("+", num_exp_sign)
    num_exp_part.add_transition("-", num_exp_sign)

    for digit in digits:
        num_exp_sign.add_transition(digit, num_exp_part)
        num_exp_part.add_transition(digit, num_state_final)
        num_state_final.add_transition(digit, num_state_final)

    return num_state
