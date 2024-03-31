import os

from src.CodeGen.Interpreter import InterpretVisitor
from src.Common.Exceptions import SemanticCheckError
from src.Lexer.Lexer import Lexer
from src.Lexer.SymbolTable import regex_table
from src.Parser.ParserLR1 import ParserLR1
from src.Parser.UtilMethods import evaluate_reverse_parse
from src.Project.Grammar import G
from src.SemanticChecking.PatronVisitor import SemanticCheckerVisitor


def run_pipeline(text: str, model_folder: str):
    # print(os.getcwd())
    # os.chdir("..")
    # os.chdir("..")
    # print(os.getcwd())
    lexer = Lexer(regex_table, file_path=f"{model_folder}/lexer_automaton.pkl")
    tokens, errors_lexer = lexer.Tokenize(text)

    # print([(x.Lemma, x.TokenType) for x in tokens])

    for e in errors_lexer:
        print('\033[91m' + str(e) + '\033[0m')
    
    if len(errors_lexer)>0:
        return    
    
    parser = ParserLR1(G, verbose=False)
    derivation, operations = parser([t.TokenType for t in tokens], get_shift_reduce=True)
    #QUE HACER SI HAY ERRORES EN EL PARSER??
    if(derivation==None):
        return
    ast = evaluate_reverse_parse(derivation, operations, tokens)

    semantic_checker = SemanticCheckerVisitor()
    errors = semantic_checker.visit(ast)

    if len(errors) > 0:
        for e in errors:
            error = SemanticCheckError("SEMANTIC ERROR: " + e)
            print('\033[91m' + str(error) + '\033[0m')

        return

    interpreter = InterpretVisitor()
    interpreter.visit(ast)


if __name__ == '__main__':
    run_pipeline( "type ArrayIterator(array: Vector, max : Number) {array : Vector = array; index : Number = -1; max "
                  ": Number = max; next() : Boolean { self.index := self.index + 1;self.index < max;} current() : "
                  "Object { self.array[self.index]; }} let array: Iterable = new ArrayIterator(range(0,5), "
                  "5) in { while(array.next()) { print(array.current()); }}", "models")
