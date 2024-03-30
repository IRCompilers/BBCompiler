import os
import dill
from typing import List
from src.Common.Token import Token
from src.Parser.SROperations import SROperations


class ShiftReduceParser(object):
    """
    Base Class for Shift-Reduce Parsers

    :param grammar: Grammar
    :param verbose: boolean, if True prints the stack and the input at each step
    """
    def __init__(self, grammar, verbose=False, action={}, goto={}, file_path=None):
        self.Grammar = grammar
        self.verbose = verbose
        if not file_path:
            file_path = "models"

        os.chdir("..")
        print(os.getcwd())

        self.action = action
        self.goto = goto
        self.copy = {}
        self._build_parsing_table()
        with open(f"{file_path}/parser_action.pkl", 'wb') as f:
            dill.dump(self.action, f)
        with open(f"{file_path}/parser_goto.pkl", 'wb') as f:
            dill.dump(self.goto, f)
        with open(f"{file_path}/parser_copy.pkl", 'wb') as f:
            dill.dump(self.copy, f)

        print(f'Building parsing table...\n\n '
              f'G: {self.Grammar},\n')

    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w: List[Token], get_shift_reduce=True):
        stack = [0]
        cursor = 0
        output = []
        operations = []

        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose:
                print(stack, '<---||--->', w[cursor:])

            if (state, str(lookahead)) not in self.copy:
                print("Error. Aborting...")
                print(state)
                print(lookahead)
                return None

            if self.copy[(state, str(lookahead))] == SROperations.OK:
                action = SROperations.OK
            else:
                action, tag = self.copy[(state, str(lookahead))]
            if action == SROperations.SHIFT:
                operations.append(SROperations.SHIFT)
                stack += [str(lookahead), tag]
                cursor += 1
            elif action == SROperations.REDUCE:
                operations.append(SROperations.REDUCE)
                output.append(tag)
                head, body = tag
                for symbol in reversed(body):
                    stack.pop()
                    assert str(stack.pop()) == str(symbol)
                    state = stack[-1]
                goto = self.goto[state, head]
                stack += [head, goto]
            elif action == SROperations.OK:
                stack.pop()
                assert stack.pop() == self.Grammar.startSymbol
                assert len(stack) == 1
                return output if not get_shift_reduce else (output, operations)
            else:
                raise Exception('Invalid action!!!')
