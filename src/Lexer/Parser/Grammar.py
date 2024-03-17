from src.Common.AutomatonUtils import nfa_to_dfa
from src.Common.Compiler import Grammar
from src.Common.Token import Token
from src.Lexer.Parser.Ast import *
from src.Lexer.Parser.EvaluateVisitor import EvaluateVisitor
from src.Lexer.Parser.FormatVisitor import FormatVisitor
from src.Lexer.Parser.Parser import SLR1Parser, evaluate_reverse_parse
from src.Project.Chars import regular_chars


def GetRegexGrammar():
    G = Grammar()

    regex = G.NonTerminal('<regex>', startSymbol=True)
    branch, piece, atom, literal = G.NonTerminals('<branch> <piece> <atom> <literal>')
    symbol, char_class_body, char_class_character = G.NonTerminals('<symbol> <char-class-body> <char-class-character>')
    escape_comp = G.NonTerminal("<escape-comp>")

    plus, star, question, bang = G.Terminals('+ * ? !')
    opar, cpar, obrack, cbrack = G.Terminals('( ) [ ]')
    dot, pipe, scape = G.Terminals('. | \\')
    literal_characters = G.Terminals(regular_chars)

    quotes = G.Terminals("\' \"")

    regex %= branch, lambda h, s: s[1]

    branch %= piece, lambda h, s: s[1]
    branch %= piece + branch, lambda h, s: ConcatNode(left=s[1], right=s[2])
    branch %= piece + pipe + branch, lambda h, s: UnionNode(left=s[1], right=s[3])

    piece %= atom, lambda h, s: s[1]
    piece %= atom + symbol, lambda h, s: s[2](child=s[1]),

    symbol %= plus, lambda h, s: PClosureNode
    symbol %= star, lambda h, s: ClosureNode
    symbol %= question, lambda h, s: PossibleNode
    symbol %= bang, lambda h, s: NotNode

    atom %= literal, lambda h, s: s[1]
    atom %= opar + branch + cpar, lambda h, s: s[2]
    atom %= obrack + char_class_body + cbrack, lambda h, s: s[2]

    whitespace = G.addWhitespace()
    literal %= whitespace, lambda h, s: LiteralNode(value=s[1])

    literal %= scape + escape_comp, lambda h, s: s[2]

    escape_comp %= star, lambda h, s: VocabularyNode()

    for v in literal_characters + quotes:
        literal %= v, lambda h, s: LiteralNode(value=s[1])

    # for v in quotes:
    #     literal %= scape + v, lambda h, s: LiteralNode(value=s[2])

    for v in [plus, star, question, bang, opar, cpar, obrack, cbrack, pipe, dot, scape]:
        escape_comp %= v, lambda h, s: LiteralNode(value=s[1])

    for v in quotes:
        escape_comp %= v, lambda h, s: LiteralNode(value=s[1])

    char_class_body %= char_class_character, lambda h, s: s[1]
    char_class_body %= char_class_character + char_class_body, lambda h, s: ConcatNode(left=s[1], right=s[2])

    char_class_character %= literal, lambda h, s: s[1]
    char_class_character %= literal + dot + dot + literal, lambda h, s: EllipsisNode(left=s[1], right=s[4])

    return G


# This is for testing
G = GetRegexGrammar()
parser = SLR1Parser(G, verbose=False)
zero = [x for x in G.terminals if x.Name == '0'][0]
nine = [x for x in G.terminals if x.Name == '9'][0]
plus = [x for x in G.terminals if x.Name == '+'][0]
dot = [x for x in G.terminals if x.Name == '.'][0]
question = [x for x in G.terminals if x.Name == '?'][0]
asterisk = [x for x in G.terminals if x.Name == "*"][0]

# tokens = [obrack, zero, dot, dot, nine, cbrack, plus, G.EOF]

obrack = [x for x in G.terminals if x.Name == '['][0]
opar = [x for x in G.terminals if x.Name == '('][0]
cpar = [x for x in G.terminals if x.Name == ')'][0]
cbrack = [x for x in G.terminals if x.Name == ']'][0]
pipe = [x for x in G.terminals if x.Name == '|'][0]
# scape = [x for x in G.terminals if x.Name == '\\'][0]
# f = [x for x in G.terminals if x.Name == 'f'][0]
# o = [x for x in G.terminals if x.Name == 'o'][0]
# r = [x for x in G.terminals if x.Name == 'r'][0]
# l = [x for x in G.terminals if x.Name == 'l'][0]
a = [x for x in G.terminals if x.Name == 'a'][0]
z = [x for x in G.terminals if x.Name == 'z'][0]
A = [x for x in G.terminals if x.Name == 'A'][0]
Z = [x for x in G.terminals if x.Name == 'Z'][0]
underscore = [x for x in G.terminals if x.Name == "_"][0]
whitespace = [x for x in G.terminals if x.Name == " "][0]
quotes = [x for x in G.terminals if x.Name == "\""][0]
scape = [x for x in G.terminals if x.Name == "\\"][0]

tokens = [quotes, opar, opar, scape, scape, scape, quotes, cpar, pipe, opar, scape, asterisk, cpar, cpar,
          asterisk, quotes, G.EOF]


# regex = "\"((\\\\\\\")|(\\*))*\""
# print(regex)
# print(tokens)
#
# derivation, operations = parser(tokens)
#
# # print(derivation)
#
# tokens = [Token(x.Name, x, 0) for x in tokens]
# ast = evaluate_reverse_parse(derivation, operations, tokens)
#
# formatter = FormatVisitor()
# # print("Formatter: ")
# print(formatter.visit(ast))
#
# evaluator = EvaluateVisitor()
# nfa = evaluator.visit(ast)
# dfa = nfa_to_dfa(nfa)
#
# # print(dfa.transitions)
# # print(dfa.finals)
#
# string_to_recognize ="\"azzzqweraw()erqwe\""
# print(string_to_recognize)
#
# print(dfa.recognize(string_to_recognize))
