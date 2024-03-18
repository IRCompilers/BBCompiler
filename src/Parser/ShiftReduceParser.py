from typing import List
from src.Common.Token import Token


class ShiftReduceParser:
    SHIFT = "SHIFT"
    REDUCE = "REDUCE"
    OK = "OK"

    def __init__(self, grammar, verbose=False):
        self.Grammar = grammar
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self.build_parsing_table()

    def build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w: List[Token], get_shift_reduce=False):
        stack = [0]
        cursor = 0
        output = []
        operations = []

        while True:
            state = stack[-1]
            lookahead = w[cursor].TokenType
            if self.verbose:
                print(stack, w[cursor:])

            try:
                if state not in self.action or lookahead not in self.action[state]:
                    error = f"{w[cursor].Pos} - SyntacticError: ERROR at or near {w[cursor].Lemma}"
                    return None, error
            except:
                print(state)
                print(self.action)
                print(lookahead)
                error = f"{w[cursor].Pos} - SyntacticError: ERROR at or near {w[cursor].Lemma}"
                return None, error

            action, tag = list(self.action[state][lookahead])[0]

            if action is self.SHIFT:
                operations.append(self.SHIFT)
                stack.append(tag)
                cursor += 1

            elif action is self.REDUCE:
                operations.append(self.REDUCE)

                if len(tag.Right):
                    stack = stack[: -len(tag.Right)]

                stack.append(list(self.goto[stack[-1]][tag.Left])[0])
                output.append(tag)

            elif action is ShiftReduceParser.OK:
                return (output if not get_shift_reduce else (output, operations)), None

            else:
                raise ValueError
