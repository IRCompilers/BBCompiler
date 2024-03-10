from src.Common.Exceptions import InvalidTransitionException
from src.Common.Token import Token
from src.Common.TokenType import TokenType
from src.Lexer.LexerAutomaton import LexerAutomaton

boilerplate_chars = [' ']


def get_automaton() -> LexerAutomaton:
    automaton = LexerAutomaton(9, [3, 6, 7, 8], {
        (0, 'f'): 1,
        (1, 'o'): 2,
        (2, 'r'): 3,
        (0, 'l'): 4,
        (4, 'e'): 5,
        (5, 't'): 6,
        (0, '<'): 7,
        (7, '='): 8
    })

    automaton.add_final_token(3, TokenType.FOR)
    automaton.add_final_token(6, TokenType.LET)
    automaton.add_final_token(7, TokenType.LESS_THAN)
    automaton.add_final_token(8, TokenType.LESS_THAN_OR_EQUAL)

    return automaton


class Lexer:
    def __init__(self):
        self.automaton = get_automaton()

    def Tokenize(self, input_string: str):
        tokens = []
        i = 0
        while i < len(input_string):

            # print(i)

            try:
                if input_string[i] in boilerplate_chars:
                    self.chop(tokens, input_string, i)
                    i += 1
                    self.automaton.reset(i + 1)
                else:
                    self.automaton.walk(input_string[i], i)

            except InvalidTransitionException:
                self.chop(tokens, input_string, i)
                i -= 1

            i += 1

        # Handle the last token
        token_type, last_start_pointer = self.automaton.get_final()
        if token_type is not None:
            tokens.append(Token(input_string[last_start_pointer:], token_type))
        return tokens

    # Synonym for chopping but more elegant
    def chop(self, tokens, input_string, i):
        token_type, last_start_pointer = self.automaton.get_final()
        if token_type is not None:
            tokens.append(Token(input_string[last_start_pointer:i], token_type))
        self.automaton.reset(i)


lexer = Lexer()
for temp in lexer.Tokenize("for<=let< =letfor"):
    print(temp.Type, temp.Lemma, len(temp.Lemma))
