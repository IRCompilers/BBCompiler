from src.Lexer.Lexer import Lexer

Text = "12 + 65*65"

lexer = Lexer()
Tokens = lexer(Text)

for token in Tokens:
    print(token)