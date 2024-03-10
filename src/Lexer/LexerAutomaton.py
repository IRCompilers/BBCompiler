from src.Common.Automaton import DFA
from src.Common.Exceptions import InvalidTransitionException


class LexerAutomaton(DFA):
    def __init__(self, states, finals, transitions):
        super().__init__(states, finals, transitions)
        self.TokenFinals = dict()  # Dictionary mapping integers to TokenType
        self.current_state = 0  # Assuming 0 is the initial state
        self.last_final_state = None
        self.start_pointer = None  # Pointer to the last final position in the input string

    def add_final_token(self, state, token_type):
        self.TokenFinals[state] = token_type

    def walk(self, symbol, pointer):
        try:
            # Update the current state based on the transition function and the input symbol
            self.current_state = self.transitions[self.current_state][symbol][0]
            # If the new current state is a final state, update the last final state and the last final pointer

            if self.current_state in self.finals:
                self.last_final_state = self.current_state

        except KeyError:
            message = f"Invalid transition in pointer {pointer} to symbol {symbol}"
            raise InvalidTransitionException(message)

    def get_final(self):
        # Check if the current state is a final state
        if self.current_state in self.finals:
            # If it is, return the corresponding TokenType and the last final pointer
            return self.TokenFinals[self.current_state], self.start_pointer
        else:
            # If it's not, return None
            return None, -1

    def reset(self, pointer):
        self.current_state = 0
        self.start_pointer = pointer
        self.last_final_state = 0
