from src.Common.Compiler import Grammar

G = Grammar()


# No Terminals
program = G.NonTerminal("<program>", startSymbol=True)
expression = G.NonTerminals("<expression>")
statement = G.NonTerminal("<statement>")
parameters, parameter_list, variable = G.NonTerminals("<parameters> <parameter_list> <variable>")
function_style = G.NonTerminal("<function_style>")
type_def = G.NonTerminal("<type_def>")
protocol_declare, protocol_body = G.NonTerminals("<protocol_declare> <protocol_body>")
simple_expression = G.NonTerminal("<simple_expression>")
expression_block = G.NonTerminal("<expression_block>")
class_block, class_body, class_declaration = G.NonTerminals("<class_block> <class_body> <class_declaration>")
arguments, argument_list = G.NonTerminals("<arguments> <argument_list>")
typed_parameters, typed_parameter_list = G.NonTerminals("<typed_parameters> <typed_parameter_list>")
declaration = G.NonTerminal("<declaration>")
if_block = G.NonTerminal("<if_block>")
else_block = G.NonTerminal("<else_block>")
disjunction, conjunction = G.NonTerminals("<disjunction> <conjunction>")
literal, proposition, boolean = G.NonTerminals("<literal> <proposition> <boolean>")
concatenation = G.NonTerminal("<concatenation>")
arithmetic_expression = G.NonTerminal("<arithmetic_expression>")
module, product, monomial, pow_ = G.NonTerminals("<module> <product> <monomial> <pow>")
high_hierarchy_object, object_exp = G.NonTerminals("<high_hierarchy_object> <object_exp>")
list_ = G.NonTerminal("<list>")

# Terminals
string, identifier, number = G.Terminals("<string> <id> <number>")
plus, minus, times, divide, int_divide = G.Terminals("+ - * / //")
equal, dequal, lesst, greatt, lequal, gequal, notequal = G.Terminals("= == < > <= >= !=")
lparen, rparen, lbrack, rbrack, lbrace, rbrace = G.Terminals("( ) [ ] { }")
comma, period, colon, semicolon = G.Terminals(", . : ;")
arrow, darrow = G.Terminals("-> =>")
and_, or_, not_ = G.Terminals("& | !")
modulus, power, power_asterisk = G.Terminals("% ^ **")
assign, concat = G.Terminals(":= @")
concat_space = G.Terminal("@@")
list_comprehension = G.Terminal("||")

for_, let, if_, else_, elif_ = G.Terminals("for let if else elif")
while_, return_, function, pi, e, print_ = G.Terminals("while return function pi e print")
new, inherits, protocol, type_, self_, in_, range_ = G.Terminals("new inherits protocol type self in range")
true, false = G.Terminals("true false")
extends = G.Terminal("extends")
rand = G.Terminal("rand")
sin, cosine, sqrt, exp, log = G.Terminals("sin cosine sqrt exp log")
as_ = G.Terminal("as")


def GetKeywords():
    return [for_, let, if_, else_, elif_, while_, return_, function, pi, e, print_,
            new, inherits, protocol, type_, self_, in_, range_, true, false, extends, as_,
            rand, sin, cosine, sqrt, exp, log]
