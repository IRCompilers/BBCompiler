from src.CodeGen.Interpreter import InterpretVisitor
from src.Common.Exceptions import SemanticCheckError
from src.Lexer.Lexer import Lexer
from src.Lexer.SymbolTable import regex_table
from src.Parser.ParserLR1 import ParserLR1, evaluate_reverse_parse
from src.Project.Grammar import G
from src.SemanticChecking.PatronVisitor import SemanticCheckerVisitor


def run_pipeline(text: str, model_folder: str):
    lexer = Lexer(regex_table, file_path=f"{model_folder}/lexer_automaton.pkl")
    tokens, errors_lexer = lexer.Tokenize(text)

    for e in errors_lexer:
        print('\033[91m' + str(e) + '\033[0m')

    parser = ParserLR1(G, verbose=False)
    derivation, operations = parser(tokens)

    ast = evaluate_reverse_parse(derivation, operations, tokens)

    semantic_checker = SemanticCheckerVisitor()
    errors = semantic_checker.visit(ast)

    if len(errors_lexer) > 0:
        return

    if len(errors) > 0:
        for e in errors:
            error = SemanticCheckError("SEMANTIC ERROR: " + e)
            print('\033[91m' + str(error) + '\033[0m')

        return

    interpreter = InterpretVisitor()
    interpreter.visit(ast)


if __name__ == '__main__':
    run_pipeline("5;", "../../models")
