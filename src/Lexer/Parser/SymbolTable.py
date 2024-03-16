from src.Project.Grammar import *

regex_table = [
    (number, "([0..9]+\.)?[0..9]+"),
    (for_, "for"),
    (let, "let")
]