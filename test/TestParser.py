import unittest

from src.Project.Grammar import G
from src.Parser.ParserLR1 import ParserLR1
from src.Parser.UtilMethods import evaluate_reverse_parse
from src.Lexer.Lexer import Lexer
from src.Lexer.SymbolTable import regex_table


# class TestParser(unittest.TestCase):
#
#     def setUp(self):
#         self.lexer = Lexer(regex_table, file_path="../models/lexer_automaton.pkl")
#         self.parser = ParserLR1(G, verbose=False)
#
#     def testParsing(self):
#         testcase0 = '-5;'

lexer = Lexer(regex_table, file_path="../models/lexer_automaton.pkl")
parser = ParserLR1(G, verbose=False)

testcase0 = 'protocol Animal {sound():Object;} type Dog {sound() => print("Woof");} type Cat {sound() => print("Meow");} type Pet inherits Dog {sound() => print("Pet sound");} type SmartCat inherits Cat { square_sum(a, b) {(a + b) * (a + b); }} let b: Animal = new Dog(), c: Animal = new Cat(), d: Animal = new Pet(), e: Animal = new SmartCat() in { print("Call")}'

number = 0


def a(testcase, id):
    global number
    try:
        parse, operations = parser([t.TokenType for t in testcase], get_shift_reduce=True)
        ast = evaluate_reverse_parse(parse, operations, testcase)
        print('\x1b[6;30;42m' + f'Test {id} passed!' + '\x1b[0m')
    except Exception as e:
        number += 1
        print(e)
        print('\x1b[6;30;41m' + f'Test {id} failed!' + '\x1b[0m')


testcases = []
while True:
    try:
        testcases.append(eval(f'testcase{len(testcases)}'))
    except:
        break

for i, testcase in enumerate(testcases):
    tokens, errors = lexer.Tokenize(testcase)
    print([token.Lemma for token in tokens])
    a(tokens, i)
