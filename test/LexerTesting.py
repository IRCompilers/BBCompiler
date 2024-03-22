import unittest

from src.Lexer.Lexer import Lexer
from src.Lexer.SymbolTable import regex_table
from src.Project.Grammar import *


class TestLexer(unittest.TestCase):

    def setUp(self):
        self.lexer = Lexer(regex_table, file_path="../models/lexer_automaton.pkl")

    def test_tokenization(self):
        # Test the tokenization of a simple string
        tokens, errors = self.lexer.Tokenize('your test string')

        expected_lemmas = ['your', 'test', 'string', '$']
        expected_types = [identifier.Name, identifier.Name, identifier.Name, G.EOF.Name]

        self.check_equal(expected_types, expected_lemmas, tokens)

    def test_tokenization_2(self):
        # Test the tokenization of a string with two words
        tokens, errors = self.lexer.Tokenize('\"Hello World\"')
        expected_lemmas = ['\"Hello World\"', '$']
        expected_types = [string.Name, G.EOF.Name]
        self.check_equal(expected_types, expected_lemmas, tokens)

    def test_tokenization_3(self):
        # Test the tokenization of a string with special characters
        tokens, errors = self.lexer.Tokenize('let x = 10;')
        expected_lemmas = ['let', 'x', '=', '10', ';', '$']
        expected_types = [let.Name, identifier.Name, equal.Name, number.Name,
                          semicolon.Name, G.EOF.Name]
        self.check_equal(expected_types, expected_lemmas, tokens)

    def test_tokenization_4(self):
        # Test the tokenization of a string with a function call
        tokens, errors = self.lexer.Tokenize('print("Hello World");')
        expected_lemmas = ['print', '(', '"Hello World"', ')', ';', '$']
        expected_types = [print_.Name, lparen.Name, string.Name, rparen.Name, semicolon.Name, G.EOF.Name]
        self.check_equal(expected_types, expected_lemmas, tokens)

    def test_tokenization_5(self):
        # Test the tokenization of a string with a function definition
        tokens, errors = self.lexer.Tokenize('function add(x: Number, y: Number) { \n\t return cos(x) *tan(y); \n }')
        expected_lemmas = ['function', 'add', '(', 'x', ':', 'Number', ',', 'y', ':', 'Number', ')', '{', 'return',
                           'cos', '(', 'x', ')', '*', 'tan', '(', 'y', ')', ';', '}', '$']
        expected_types = [function.Name, identifier.Name, lparen.Name, identifier.Name, colon.Name, identifier.Name,
                          comma.Name, identifier.Name, colon.Name, identifier.Name, rparen.Name, lbrace.Name,
                          identifier.Name,
                          cos.Name, lparen.Name, identifier.Name, rparen.Name, times.Name, tan.Name, lparen.Name,
                          identifier.Name, rparen.Name, semicolon.Name, rbrace.Name, G.EOF.Name]

        self.check_equal(expected_types, expected_lemmas, tokens)

    def test_tokenization_6(self):
        # Test the tokenization of a string with a complex code snippet
        tokens, errors = self.lexer.Tokenize(
            'if (x > 10) { print("x is greater than 10"); } else { print("x is not g \\" reater than 10"); }')
        expected_lemmas = ['if', '(', 'x', '>', '10', ')', '{', 'print', '(', '"x is greater than 10"', ')', ';', '}',
                           'else', '{', 'print', '(', '"x is not g \\" reater than 10"', ')', ';', '}', '$']
        expected_types = [if_.Name, lparen.Name, identifier.Name, greatt.Name, number.Name, rparen.Name, lbrace.Name,
                          print_.Name, lparen.Name, string.Name, rparen.Name, semicolon.Name, rbrace.Name, else_.Name,
                          lbrace.Name, print_.Name, lparen.Name, string.Name, rparen.Name, semicolon.Name, rbrace.Name,
                          G.EOF.Name]

        self.check_equal(expected_types, expected_lemmas, tokens)

    def test_tokenization_7(self):
        # Test with assign and incorrect tokens
        tokens, errors = self.lexer.Tokenize("let a=243.12 in := temp; \n let b=312 in ?? a-b+1")
        expected_lemmas = ['let', 'a', '=', '243.12', 'in', ':=', 'temp', ';', 'let', 'b', '=', '312', 'in', 'a', '-',
                           'b', '+', '1', '$']
        expected_types = [let.Name, identifier.Name, equal.Name, number.Name, in_.Name, destruct.Name, identifier.Name,
                          semicolon.Name, let.Name, identifier.Name, equal.Name, number.Name, in_.Name, identifier.Name,
                          minus.Name, identifier.Name, plus.Name, number.Name, G.EOF.Name]
        self.check_equal(expected_types, expected_lemmas, tokens)

    def test_tokenization_8(self):
        # Testing 2 strings in the same expression and identifier with number
        tokens, errors = self.lexer.Tokenize(
            "def \n \n \n plus (a2, b) \n 50 + 12.3  \"long string def : let print\" let x = 10 \"Hola Mundo\"")

        expected_lemmas = ['def', 'plus', '(', 'a2', ',', 'b', ')', '50', '+', '12.3', '\"long string def : let print\"',
                           'let', 'x', '=', '10', '\"Hola Mundo\"', '$']
        expected_types = [identifier.Name, identifier.Name, lparen.Name, identifier.Name, comma.Name, identifier.Name,
                          rparen.Name, number.Name, plus.Name, number.Name, string.Name, let.Name, identifier.Name,
                          equal.Name, number.Name, string.Name, G.EOF.Name]

        self.check_equal(expected_types, expected_lemmas, tokens)

    def check_equal(self, expected_types, expected_lemmas, tokens):
        token_lemmas = [token.Lemma for token in tokens]
        token_types = [token.TokenType.Name for token in tokens]
        self.assertEqual(expected_types, token_types)
        self.assertEqual(expected_lemmas, token_lemmas)


if __name__ == '__main__':
    unittest.main()
