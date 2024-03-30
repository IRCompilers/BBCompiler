import click

from src.Lexer.Lexer import Lexer
from src.Lexer.SymbolTable import regex_table
from src.Project.Pipeline import run_pipeline


@click.group()
def hulk():
    pass


@hulk.command()
@click.argument('filename')
def run(filename):
    text = ""

    with open(filename, 'r') as file:
        for line in file:
            text += line

    run_pipeline(text, "models")


pass

if __name__ == '__main__':
    hulk()
