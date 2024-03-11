from src.Lexer.Lexer import Lexer

Text = "-123.534 + 200 = a; a > b && b <= 9let identity in print(x);"

lexer = Lexer()
Tokens = lexer(Text)

for token in Tokens:
    print(token)