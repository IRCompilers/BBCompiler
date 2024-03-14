from src.Common.Compiler import Grammar


def GetLexerGrammar():
    G = Grammar()
    R = G.NonTerminal('regex', startSymbol=True)
    B, P, A, L, CCB, CCC, S = G.NonTerminals('branch piece atom literal CCB CCC symbol')
    plus, star, question, minus, opar, cpar, obrack, cbrack, pipe, dot = G.Terminals('+ * ? - ( ) [ ] | .')
    literals = G.Terminals(
        'a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z # $ % &  @ ^ _ 0 1 2 3 4 5 6 7 8 9')

    for v in literals:
        L %= v

    R %= B
    B %= P | P + B | P + pipe + B
    P %= A + S
    S %= star | minus + G.Epsilon | plus + G.Epsilon | question + G.Epsilon | G.Epsilon
    A %= L | opar + B + cpar | obrack + CCB + cbrack
    CCB %= CCC | CCC + CCB
    CCC %= L | L + dot + dot + L

    # for op in [plus, star, question, bang, opar, cpar, obrack, cbrack, pipe, dot]:
    #     L %= op

    GG = G.AugmentedGrammar()
    return GG
