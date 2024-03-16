from src.Common.AutomatonUtils import nfa_to_dfa
from src.Common.Compiler import Grammar
from src.Common.Token import Token
from src.Lexer.Parser.Ast import *
from src.Lexer.Parser.EvaluateVisitor import EvaluateVisitor
from src.Lexer.Parser.FormatVisitor import FormatVisitor
from src.Lexer.Parser.Parser import SLR1Parser, evaluate_reverse_parse


def GetRegexGrammar():
    G = Grammar()

    regex = G.NonTerminal('<regex>', startSymbol=True)
    branch, piece, atom, literal = G.NonTerminals('<branch> <piece> <atom> <literal>')
    symbol, char_class_body, char_class_character = G.NonTerminals('<symbol> <char-class-body> <char-class-character>')

    plus, star, question, bang = G.Terminals('+ * ? !')
    opar, cpar, obrack, cbrack = G.Terminals('( ) [ ]')
    dot, pipe, scape = G.Terminals('. | \\')
    literal_characters = G.Terminals(
        'a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z # $ % &  @ ^ _ 0 1 2 3 4 5 6 7 8 9')

    regex %= branch, lambda h, s: s[1]

    branch %= piece, lambda h, s: s[1]
    branch %= piece + branch, lambda h, s: ConcatNode(left=s[1], right=s[2])
    branch %= piece + pipe + branch, lambda h, s: UnionNode(left=s[1], right=s[3])

    piece %= atom, lambda h, s: s[1]
    piece %= atom + symbol, lambda h, s: s[2](child=s[1]),
    # piece %= atom + piece, lambda h, s: ConcatNode(left=s[1], right=s[2])

    symbol %= plus, lambda h, s: PClosureNode
    symbol %= star, lambda h, s: ClosureNode
    symbol %= question, lambda h, s: PossibleNode
    symbol %= bang, lambda h, s: NotNode

    atom %= literal, lambda h, s: s[1]
    atom %= opar + branch + cpar, lambda h, s: s[2]
    atom %= obrack + char_class_body + cbrack, lambda h, s: s[2]

    for v in literal_characters:
        literal %= v, lambda h, s: LiteralNode(value=s[1])

    for v in [plus, star, question, bang, opar, cpar, obrack, cbrack, pipe, dot]:
        literal %= scape + v, lambda h, s: LiteralNode(value=s[2])

    char_class_body %= char_class_character, lambda h, s: s[1]
    char_class_body %= char_class_character + char_class_body, lambda h, s: ConcatNode(left=s[1], right=s[2])

    char_class_character %= literal, lambda h, s: s[1]
    char_class_character %= literal + dot + dot + literal, lambda h, s: EllipsisNode(left=s[1], right=s[4])

    return G


# # This is for testing
# G = GetRegexGrammar()
# parser = SLR1Parser(G, verbose=False)
# zero = [x for x in G.terminals if x.Name == '0'][0]
# nine = [x for x in G.terminals if x.Name == '9'][0]
# plus = [x for x in G.terminals if x.Name == '+'][0]
# dot = [x for x in G.terminals if x.Name == '.'][0]
# question = [x for x in G.terminals if x.Name == '?'][0]
#
# # tokens = [obrack, zero, dot, dot, nine, cbrack, plus, G.EOF]
#
# obrack = [x for x in G.terminals if x.Name == '['][0]
# opar = [x for x in G.terminals if x.Name == '('][0]
# cpar = [x for x in G.terminals if x.Name == ')'][0]
# cbrack = [x for x in G.terminals if x.Name == ']'][0]
# pipe = [x for x in G.terminals if x.Name == '|'][0]
# scape = [x for x in G.terminals if x.Name == '\\'][0]
# f = [x for x in G.terminals if x.Name == 'f'][0]
# o = [x for x in G.terminals if x.Name == 'o'][0]
# r = [x for x in G.terminals if x.Name == 'r'][0]
# l = [x for x in G.terminals if x.Name == 'l'][0]
#
# tokens = [opar, obrack, zero, dot, dot, nine, cbrack, plus, scape, dot, cpar, question, obrack, zero, dot, dot, nine,
#           cbrack, plus, G.EOF]
# print(tokens)
#
# derivation, operations = parser(tokens)
#
# print(derivation)
#
# tokens = [Token(x.Name, x, 0) for x in tokens]
# ast = evaluate_reverse_parse(derivation, operations, tokens)
#
# print(type(ast))
#
# formatter = FormatVisitor()
# print("Formatter: ")
# print(formatter.visit(ast))
#
# evaluator = EvaluateVisitor()
# nfa = evaluator.visit(ast)
# dfa = nfa_to_dfa(nfa)
# print(dfa.transitions)
# print(dfa.finals)
#
# print(dfa.recognize("133.6645"))
