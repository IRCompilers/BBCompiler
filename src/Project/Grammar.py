from src.Common.Compiler import Grammar

G = Grammar()

string, identifier, number = G.Terminals("<string> <id> <number>")
plus, minus, times, divide = G.Terminals("+ - * /")
equal, dequal, lesst, greatt, lequal, gequal = G.Terminals("= == < > <= >=")
lparen, rparen, lbrack, rbrack, lbrace, rbrace = G.Terminals("( ) [ ] { }")
comma, period, colon, semicolon = G.Terminals(", . : ;")
arrow, darrow = G.Terminals("-> =>")
and_, or_, not_ = G.Terminals("& | !")
modulus, power = G.Terminals("% ^")
destruct, concat = G.Terminals(":= @")

for_, let, if_, else_, elif_ = G.Terminals("for let if else elif")
while_, function, pi, e, print_ = G.Terminals("while function pi e print")
new, inherits, protocol, type_, self_, in_, range_ = G.Terminals("new inherits protocol type self in range")
true, false = G.Terminals("true false")
extends = G.Terminals("extends")
sin, cos, tan, sqrt, exp, log, rand = G.Terminals("sin cos tan sqrt exp log rand")


def GetKeywords():
    return [for_, let, if_, else_, elif_, while_, function, pi, e, print_,
            new, inherits, protocol, type_, self_, in_, range_, true, false, extends,
            sin, cos, tan]
