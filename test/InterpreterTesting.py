import unittest

from src.CodeGen.CodeContext import CodeContext
from src.CodeGen.Interpreter import InterpretVisitor
from src.SemanticChecking.PatronVisitor import SemanticCheckerVisitor
from src.Common.ASTNodes import *
from src.SemanticChecking.Scope import Scope

semantic_checker = SemanticCheckerVisitor()
interpreter = InterpretVisitor()


def assert_expected(capsys, node, expected):
    errors = semantic_checker.visit(node)

    if len(errors) > 0:
        raise Exception(f"Not semantically correct because {errors[0]}")

    interpreter.visit(node)

    captured = capsys.readouterr()

    assert captured.out == expected


def test_empty(capsys):
    node = ProgramNode([], FunctionCallNode("print", [NumberNode(2)]))
    assert_expected(capsys, node, "2\n")


def test_func_decl_and_call(capsys):
    sum_of_squares = ArithmeticExpression(operation="+",
                                          left=ArithmeticExpression("*", VariableNode("a"), VariableNode("a")),
                                          right=ArithmeticExpression("*", VariableNode("b"), VariableNode("b")))
    function = FunctionNode(name="sumOfSquares",
                            parameters=[ParameterNode("a", type="Number"), ParameterNode("b", type="Number")],
                            corpus=sum_of_squares, type="Number")

    invocation = FunctionCallNode("sumOfSquares", [NumberNode(2), NumberNode(2)])
    print_ = FunctionCallNode("print", [invocation])
    node = ProgramNode([function], print_)

    assert_expected(capsys, node, "8\n")


def test_let(capsys):
    let_ = LetNode([ParameterNode("a", "Number")], [NumberNode(2)],
                   ArithmeticExpression("+", VariableNode("a"), NumberNode(2)))

    print_ = FunctionCallNode("print", [let_])

    node = ProgramNode([], print_)

    assert_expected(capsys, node, "4\n")


def test_simple_type_decl(capsys):
    type_ = TypeNode("Person", [TypeAtributeNode(ParameterNode("name", "String"), StringNode("Unnamed"))],
                     [ParameterNode("name", "String")])

    print_ = FunctionCallNode("print", [StringNode("a")])
    let_ = LetNode([ParameterNode("a", "Person")], [NewNode("Person", [StringNode("John")])], print_)
    node = ProgramNode([type_], let_)

    assert_expected(capsys, node, "a\n")


def test_if(capsys):
    if_ = IfElseExpression([ComparationExpression("==", NumberNode(2), NumberNode(2))],
                           [NumberNode(1), NumberNode(0)])
    node = ProgramNode([], FunctionCallNode("print", [if_]))

    assert_expected(capsys, node, "1\n")


def test_type_function_call(capsys):
    greet_params = [ParameterNode("name", "String"), ParameterNode("date", "Number")]
    greet_body = StringConcatenationNode(StringNode("Hello"), StringConcatenationNode(StringNode("on"),
                                                                                      StringConcatenationNode(
                                                                                          SelfVariableNode(True,
                                                                                                           "name"),
                                                                                          VariableNode("date"))))

    type_corpus = [TypeAtributeNode(ParameterNode("name", "String"), StringNode("Unnamed")),
                   FunctionNode("greet", greet_params, greet_body, "String")]
    type_ = TypeNode("Person", type_corpus, [ParameterNode("name", "String")])

    function_call = TypeFunctionCallNode(VariableNode("person"), "greet", [StringNode("John"), NumberNode(2)])
    print_ = FunctionCallNode("print", [function_call])
    expression_block = LetNode([ParameterNode("person", "Person")], [NewNode("Person", [StringNode("John")])],
                               print_)
    node = ProgramNode([type_], expression_block)

    assert_expected(capsys, node, "Hello on John2\n")


def test_for_node(capsys):
    for_node = ForNode("i", FunctionCallNode("range", [NumberNode(0), NumberNode(10)]), VariableNode("i"))
    print_ = FunctionCallNode("print", [for_node])
    node = ProgramNode([], print_)
    assert_expected(capsys, node, "9\n")


def test_while_node(capsys):
    destructive_expr = DestructiveExpression("i", ArithmeticExpression("+", VariableNode("i"), NumberNode(1)))
    expr_block_1 = ExpressionBlockNode([FunctionCallNode("print", [VariableNode("i")]), destructive_expr])
    while_ = WhileNode(ComparationExpression("<", VariableNode("i"), NumberNode(10)), expr_block_1)

    expr_block_2 = ExpressionBlockNode([while_])
    let_ = LetNode([ParameterNode("i", "Number")], [NumberNode(0)], expr_block_2)
    node = ProgramNode([], let_)

    assert_expected(capsys, node, '0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n')


def test_inheritance(capsys):
    base_type = TypeNode("Human", [], [])
    sub_type = TypeNode("Person", [], [], "Human")

    instantiation = NewNode("Person", [])
    let_ = LetNode([ParameterNode("john", "Human")], [instantiation], VariableNode("john"))
    node = ProgramNode([base_type, sub_type], let_)

    assert_expected(capsys, node, "")


def test_base_call_polymorphism(capsys):
    """
    Equivalent to:

    type Human {
        greet(name: String) => name;
    }

    type Person(name: String) {
        greet(name: String) => print(base())
    }

    let john: Human = new Person("John")
        in john.greet("johnny")

    """
    simple_greet = FunctionNode("greet", [ParameterNode("name", "String")], VariableNode("name"))
    greet_body = FunctionCallNode("print", [FunctionCallNode("base", [])])
    greet = FunctionNode("greet", [ParameterNode("name", "String")], greet_body)

    type_b = TypeNode("Human", [simple_greet], [])
    type_a = TypeNode("Person", [greet], [ParameterNode("name", "String")], "Human", [])

    instantiation = NewNode("Person", [StringNode("John")])
    john_param = ParameterNode("john", "Human")
    type_call = TypeFunctionCallNode(VariableNode("john"), "greet", [StringNode("johnny")])
    let_ = LetNode([john_param], [instantiation], type_call)

    node = ProgramNode([type_a, type_b], let_)

    assert_expected(capsys, node, "johnny\n")


def test_protocol_inherits_from_protocol(capsys):
    protocol_base = ProtocolNode("ProtocolBase", [])
    protocol = ProtocolNode("ProtocolA", [], "ProtocolBase")

    node = ProgramNode([protocol_base, protocol], NumberNode(2))
    assert_expected(capsys, node, "")


def test_protocol_polymorphism(capsys):
    protocol = ProtocolNode("Flyable", [ProtocolMethodNode("fly", [ParameterNode("distance", "Number")], "Object")])

    fly_type_func = FunctionNode("fly", [ParameterNode("distance", "Number")],
                                 FunctionCallNode("print", [StringNode("temp")]), "Object")
    type_a = TypeNode("Bird", [fly_type_func], [])

    let_ = LetNode([ParameterNode("rocio", "Flyable")], [NewNode("Bird", [])],
                   TypeFunctionCallNode(VariableNode("rocio"), "fly", [NumberNode(2)]))

    node = ProgramNode([protocol, type_a], let_)

    assert_expected(capsys, node, "temp\n")


def test_recursion(capsys):
    fact_body_recursion = FunctionCallNode("factorial",
                                           [ArithmeticExpression("-", VariableNode("x"), NumberNode(1))])
    fact_body = ArithmeticExpression("*", VariableNode("x"), fact_body_recursion)
    fact = FunctionNode("factorial", [ParameterNode("x", "Number")], fact_body)
    print_ = FunctionCallNode("print", [FunctionCallNode("factorial", [NumberNode(5)])])
    node = ProgramNode([fact], print_)

    assert_expected(capsys, node, "120\n")


def test_ultimate(capsys):
    """
    Equivalent to

    protocol BaseProtocol{
        method(param: Number): Object
    }

    protocol ChildProtocol extends BaseProtocol{
    }

    type TypeA {
        method(param: Number){
            print("temp")
        }

        another(){
            5;
        }
    }

    print(for i in range(0, 10) {
            let instance: BaseProtocol = new TypeA() in
                if i < 2 instance.method(2)
                elif i >= 4 (instance as TypeA).another()
                else "Temp";
        })
    """

    base_protocol = ProtocolNode("BaseProtocol",
                                 [ProtocolMethodNode("method", [ParameterNode("param", "Number")], "Object")])

    child_protocol = ProtocolNode("ChildProtocol", [], "BaseProtocol")

    method_func = FunctionNode("method", [ParameterNode("param", "Number")],
                               FunctionCallNode("print", [StringNode("temp")]), "Object")

    type_a = TypeNode("TypeA", [method_func, FunctionNode("another", [], NumberNode(5))], [])

    conditions = [ComparationExpression("<", VariableNode("i"), NumberNode(2)),
                  ComparationExpression(">=", VariableNode("i"), NumberNode(4))]

    first_branch = TypeFunctionCallNode(VariableNode("instance"), "method", [NumberNode(2)])
    second_branch = TypeFunctionCallNode(AsNode(VariableNode("instance"), "TypeA"), "another", [])
    third_branch = StringNode("Temp")

    expressions = [first_branch, second_branch, third_branch]

    if_ = IfElseExpression(conditions, expressions)

    let_params = [ParameterNode("instance", "BaseProtocol")]
    value_params = [NewNode("TypeA", [])]
    let = LetNode(let_params, value_params, if_)

    for_node = ForNode("i", FunctionCallNode("range", [NumberNode(0), NumberNode(10)]), let)
    print_ = FunctionCallNode("print", [for_node])

    node = ProgramNode([base_protocol, child_protocol, type_a], print_)

    assert_expected(capsys, node, "5\n")
