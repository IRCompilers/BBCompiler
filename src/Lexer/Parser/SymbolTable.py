from src.Project.Grammar import *

regex_table = [
    (for_, "for"),
    (let, "let"),
    (if_, "if"),
    (else_, "else"),
    (elif_, "elif"),
    (while_, "while"),
    (function, "function"),
    (print_, "print"),
    (pi, "pi"),
    (e, "e"),
    (new, "new"),
    (inherits, "inherits"),
    (protocol, "protocol"),
    (type_, "type"),
    (self_, "self"),
    (in_, "in"),
    (range_, "range"),
    (true, "true"),
    (false, "false"),
    (extends, "extends"),
    (identifier, "([a..z]|[A..Z]|_)([a..z]|[A..Z]|_|[0..9])*"),
    (number, "([0..9]+\.)?[0..9]+"),
    (string, "\"((\\\\\\\")|(\\*))*\"")
]

['"', '(', '(', '\\', '\\', '\\', '"', ')', '|', '(', '\\', '*', ')', ')', '*', '"', '$']