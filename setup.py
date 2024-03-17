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
            text += "\n"
            text += line

    tokens = lexer(text)
    for v in tokens:
        print(v.Lemma, v.TokenType)


pass

if __name__ == '__main__':
    hulk()
