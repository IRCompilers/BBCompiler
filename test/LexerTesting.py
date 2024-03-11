from src.Lexer.Lexer import Lexer

Text = "-123.534 + 200 = a; for v in a; \" the great fenomenon \"; let identity in print(x);"

lexer = Lexer()
Tokens = lexer(Text)

for token in Tokens:
    print(token)