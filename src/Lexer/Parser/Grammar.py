from Ast import *
from src.Common.Compiler import Grammar
from src.Common.Token import Token
from src.Lexer.Parser.Parser import SLR1Parser, evaluate_reverse_parse


def GetLexerGrammar():
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
    branch %= piece + pipe + branch, lambda h, s: UnionNode(left=s[1], right=s[3])

    piece %= atom + symbol, lambda h, s: s[2](child=s[1]),
    piece %= atom, lambda h, s: s[1]

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

    # B %= P | P + B | P + pipe + B
    # P %= A + S | A
    # S %= star | minus + G.Epsilon | plus + G.Epsilon | question + G.Epsilon | G.Epsilon
    # A %= L | opar + B + cpar | obrack + CCB + cbrack
    # CCB %= CCC | CCC + CCB
    # CCC %= L | L + dot + dot + L

    # G = Grammar()
    # R = G.NonTerminal('regex', startSymbol=True)
    # B, P, A, L, CCB, CCC, S = G.NonTerminals('branch piece atom literal CCB CCC symbol')
    # plus, star, question, minus, opar, cpar, obrack, cbrack, pipe, dot = G.Terminals('+ * ? - ( ) [ ] | .')
    # literals = G.Terminals(
    #     'a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z # $ % &  @ ^ _ 0 1 2 3 4 5 6 7 8 9')
    #
    # for v in literals:
    #     L %= v
    #
    # R %= B, lambda h, s: s[1]
    #
    # print(G)

    # for op in [plus, star, question, bang, opar, cpar, obrack, cbrack, pipe, dot]:
    #     L %= op

    # stat_list %= stat + semi, lambda h, s: [s[1]]  # Your code here!!! (add rule)
    # stat_list %= stat + semi + stat_list, lambda h, s: [s[1]] + s[3]  # Your code here!!! (add rule)

    # grammar = GetLexerGrammar()
    parser = SLR1Parser(G, verbose=False)
    zero = [x for x in G.terminals if x.Name == '0'][0]
    nine = [x for x in G.terminals if x.Name == '9'][0]
    tokens = [obrack, zero, dot, dot, nine, cbrack, plus, G.EOF]
    derivation, operations = parser(tokens)
    tokens = [Token(x.Name, x, 0) for x in tokens]
    ast = evaluate_reverse_parse(derivation, operations, tokens)
    print(ast)

    return G


g = GetLexerGrammar()
