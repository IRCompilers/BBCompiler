from src.Common.Compiler import Grammar


def GetLexerGrammar():
    G = Grammar()
    R = G.NonTerminal('R', startSymbol=True)
    B, P, A, L, CC, CCB, CCC, B_prime, P_prime, CCB_prime = G.NonTerminals('B P A L CC CCB CCC B_ P_ CCB_')
    plus, star, question, opar, cpar, obrack, cbrack, pipe, dot, a, b, c = G.Terminals('+ * ? ( ) [ ] | . a b c')

    R %= B + G.Epsilon
    B %= P + B_prime
    B_prime %= pipe + P + B_prime | G.Epsilon
    P %= A + P_prime
    P_prime %= plus + A + P_prime | star + A + P_prime | question + A + P_prime | G.Epsilon
    A %= L | opar + R + cpar | CC
    L %= a | b + G.Epsilon | c + G.Epsilon
    CC %= obrack + CCB + cbrack
    CCB %= CCC + CCB_prime
    CCB_prime %= G.Epsilon | CCC + CCB_prime
    CCC %= L | L + dot + dot + L

    GG = G.AugmentedGrammar()
    return GG