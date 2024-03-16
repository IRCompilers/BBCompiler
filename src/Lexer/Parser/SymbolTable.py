from src.Project.Grammar import *

regex_table = [
    (number, "[0..9]+"),
    (for_, "[for]"),
    (let, "[let]")
    # (TokenType.LESS_THAN, "<"),
    # (TokenType.LESS_THAN_OR_EQUAL, "<=")
]
