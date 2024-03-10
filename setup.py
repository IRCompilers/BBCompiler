import click

from src.Common.Automaton import Automaton
from src.Lexer.Lexer import Lexer


@click.group()
def hulk():
    pass


@hulk.command()
@click.argument('filename')
def run(filename):
    lexer = Lexer()

    # Define transitions
    transitions = {
        ('q0', 'a'): 'q1',
        ('q1', 'b'): 'q2',
        ('q2', 'c'): 'q3',
        ('q3', 'd'): 'q3'
    }

    # Define start state
    start_state = 'q0'

    # Define accept states
    accept_states = {'q3'}

    # Initialize the Automaton
    automaton = Automaton(transitions, start_state, accept_states)

    # Check if a string is accepted
    print(automaton.is_accepted('abcd'))  # True
    print(automaton.is_accepted('abc'))  # False

    # with open(filename, 'r') as file:
    #     for line in file:
    #         tokens = lexer.Tokenize(line)
    #         for token in tokens:
    #             print(token.Lemma, token.Type)


pass

if __name__ == '__main__':
    hulk()
