import click

from src.Lexer.Lexer import Lexer
from src.Lexer.SymbolTable import regex_table


@click.group()
def hulk():
    pass


@hulk.command()
@click.argument('filename')
def run(filename):
    lexer = Lexer(regex_table)
    text = ""
    with open(filename, 'r') as file:
        for line in file:
            text += line

    print(text)

    tokens, errors = lexer.Tokenize(text)
    for v in tokens:
        print(v.Lemma, v.TokenType, v.Pos)

    for e in errors:
        print('\033[91m' + str(e) + '\033[0m')


pass

if __name__ == '__main__':
    hulk()
