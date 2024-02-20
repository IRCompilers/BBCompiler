import click

from src.Lexer.Lexer import Lexer


@click.group()
def hulk():
    pass


@hulk.command()
@click.argument('filename')
def run(filename):
    lexer = Lexer()

    with open(filename, 'r') as file:
        for line in file:
            tokens = lexer.Tokenize(line)
            for token in tokens:
                print(token.Lemma, token.Type)


pass

if __name__ == '__main__':
    hulk()
