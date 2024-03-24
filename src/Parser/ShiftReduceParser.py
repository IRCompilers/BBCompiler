from typing import List
from src.Common.Token import Token
from src.Parser.SROperations import SROperations


class ShiftReduceParser:

    def __init__(self, grammar, verbose=False):
        self.Grammar = grammar
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self.build_parsing_table()

    def build_parsing_table(self):
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

            if (state, lookahead) not in self.action:
                print("Error. Aborting...")
                return None

            if self.action[state, lookahead] == SROperations.OK:
                action = SROperations.OK

            else:
                action, tag = self.action[state, lookahead]

            if action == SROperations.SHIFT:
                operations.append(SROperations.SHIFT)
                stack += [lookahead, tag]
                cursor += 1

            elif action == SROperations.REDUCE:
                operations.append(SROperations.REDUCE)
                output.append(tag)
                head, body = tag
                for symbol in reversed(body):
                    stack.pop()
                    assert stack.pop() == symbol
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
