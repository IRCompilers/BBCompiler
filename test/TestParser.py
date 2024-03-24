from src.Project.Grammar import G
from src.Parser.ParserLR1 import ParserLR1

parser = ParserLR1(G, verbose=True)
