import unittest
from src.SemanticChecking.PatronVisitor import SemanticCheckerVisitor
from src.Common.ASTNodes import *
from src.SemanticChecking.Scope import Scope


class TestSemanticCheckerVisitor(unittest.TestCase):
    def setUp(self):
        self.visitor = SemanticCheckerVisitor()

    def test_empty(self):
        node = ProgramNode([], NumberNode(2))
        scope = Scope()
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, [])

    def test_print_correct(self):
        node = ProgramNode([], FunctionCallNode("print", [NumberNode(2)]))
        scope = Scope()
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, [])

    def test_print_with_type_mismatch(self):
        node = ProgramNode([], ArithmeticExpression("+", NumberNode(2), StringNode("hello")))
        scope = Scope()
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ['Number expression was expected instead of String'])

    def test_function_decl_correct(self):
        scope = Scope()
        sum_of_squares = ArithmeticExpression(operation="+",
                                              left=ArithmeticExpression("*", VariableNode("a"), VariableNode("a")),
                                              right=ArithmeticExpression("*", VariableNode("b"), VariableNode("b")))
        function = FunctionNode(name="sumOfSquares",
                                parameters=[ParameterNode("a", type="Number"), ParameterNode("b", type="Number")],
                                corpus=sum_of_squares, type="Number")

        node = ProgramNode([function], ArithmeticExpression(" + ", NumberNode(2), NumberNode(2)))
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, [])

    def test_let_correct(self):
        scope = Scope()
        let_ = LetNode([ParameterNode("a", "Number")], [NumberNode(2)],
                       ArithmeticExpression("+", VariableNode("a"), NumberNode(2)))

        node = ProgramNode([], let_)
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, [])

    def test_let_type_missmatch(self):
        scope = Scope()
        params = [StringNode("true")]
        let_ = LetNode([ParameterNode("a", "Number")], [FunctionCallNode("print", params)],
                       ArithmeticExpression("+", VariableNode("a"), NumberNode(2)))

        node = ProgramNode([], let_)
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ['Number expression was expected instead of object'])

    def test_let_func_call_no_decl(self):
        scope = Scope()
        let_ = LetNode([ParameterNode("a", "Number")], [NumberNode(2)],
                       FunctionCallNode("sumOfSquares", [VariableNode("a"), NumberNode(2)]))

        node = ProgramNode([], let_)
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ["The sumOfSquares function doesn't exist in the current context"])

    def test_let_func_call_type_mismatch(self):
        scope = Scope()
        sum_of_squares = ArithmeticExpression(operation="+",
                                              left=ArithmeticExpression("*", VariableNode("a"), VariableNode("a")),
                                              right=ArithmeticExpression("*", VariableNode("b"), VariableNode("b"))
                                              )
        function = FunctionNode(name="sumOfSquares",
                                parameters=[ParameterNode("a", type="Number"), ParameterNode("b", type="Number")],
                                corpus=sum_of_squares, type="String")

        let_ = LetNode([ParameterNode("a", "Number")], [NumberNode(2)],
                       FunctionCallNode("sumOfSquares", [VariableNode("a"), StringNode("hello")]))
        node = ProgramNode([function], let_)
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ['String expression was expected instead of Number',
                                  'Number expression was expected instead of String'])

    def test_simple_type_decl_correct(self):
        scope = Scope()
        type_ = TypeNode("Person", [TypeAtributeNode(ParameterNode("name", "String"), StringNode("Unnamed"))],
                         [ParameterNode("name", "String")])
        node = ProgramNode([type_], NewNode("Person", [StringNode("John")]))
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, [])

    def test_simple_type_decl_type_missmatch(self):
        scope = Scope()
        type_ = TypeNode("Person",
                         [TypeAtributeNode(ParameterNode("age", "Number"), NumberNode(-1)),
                          TypeAtributeNode(ParameterNode("name", "String"), StringNode("Unnamed"))],
                         [ParameterNode("name", "String"), ParameterNode("age", "Number")])

        node = ProgramNode([type_], NewNode("Person", [StringNode("John"), BooleanNode(True)]))
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ['Number expression was expected instead of Boolean'])

    def test_type_new_call_non_declared(self):
        scope = Scope()
        node = ProgramNode([], NewNode("Person", [StringNode("John"), BooleanNode(True)]))
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ["The Person type doesn't exist in the current context"])

    def test_two_types_one_mismatch_other_non_declared(self):
        scope = Scope()
        type_ = TypeNode("Person",
                         [TypeAtributeNode(ParameterNode("age", "Number"), StringNode('aaa')),
                          TypeAtributeNode(ParameterNode("name", "String"), StringNode("Unnamed"))],
                         [ParameterNode("name", "String"), ParameterNode("age", "Number")])

        node = ProgramNode([type_], NewNode("Animal", [StringNode("John"), BooleanNode(True)]))
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ['Number expression was expected instead of String',
                                  "The Animal type doesn't exist in the current context"])

    def test_if_correct(self):
        scope = Scope()
        if_ = IfElseExpression([ComparationExpression("==", NumberNode(2), NumberNode(2))],
                               [NumberNode(1), NumberNode(0)])
        node = ProgramNode([], if_)
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, [])

    def test_if_should_match_object(self):
        scope = Scope()
        if_ = IfElseExpression([ComparationExpression("==", NumberNode(2), StringNode("hello"))],
                               [StringNode(1), NumberNode(0)])
        node = ProgramNode([], if_)
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, [])

    def test_if_multiple_conditions_non_boolean(self):
        scope = Scope()
        if_ = IfElseExpression([StringNode("John"), NumberNode(1)], [StringNode(1), NumberNode(2), NumberNode(0)])
        node = ProgramNode([], if_)
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ['Boolean expression was expected instead of String',
                                  'Boolean expression was expected instead of Number'])

    def test_type_function_call_correct(self):
        scope = Scope()
        greet_params = [ParameterNode("name", "String"), ParameterNode("date", "Number")]
        greet_body = StringConcatenationNode(StringNode("Hello"), StringConcatenationNode(StringNode("on"),
                                                                                          StringConcatenationNode(
                                                                                              SelfVariableNode(True,
                                                                                                               "name"),
                                                                                              VariableNode("date"))))

        type_corpus = [TypeAtributeNode(ParameterNode("name", "String"), StringNode("Unnamed")),
                       FunctionNode("greet", greet_params, greet_body, "String")]
        type_ = TypeNode("Person", type_corpus, [ParameterNode("name", "String")])

        function_call = TypeFunctionCallNode(VariableNode("John"), "greet", [StringNode("John"), NumberNode(2)])
        expression_block = LetNode([ParameterNode("John",'Person')],[NewNode("Person",[StringNode("John")] )], function_call)
        node = ProgramNode([type_], expression_block)
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, [])

    def test_type_function_call_no_decl(self):
        scope = Scope()
        greet_params = [ParameterNode("name", "String"), ParameterNode("date", "Number")]
        greet_body = StringConcatenationNode(StringNode("Hello"), StringConcatenationNode(StringNode("on"),
                                                                                          StringConcatenationNode(
                                                                                              SelfVariableNode(True,
                                                                                                               "name"),
                                                                                              VariableNode("date"))))

        type_corpus = [TypeAtributeNode(ParameterNode("name", "String"), StringNode("Unnamed")),
                       FunctionNode("greet", greet_params, greet_body, "String")]
        type_ = TypeNode("Person", type_corpus, [ParameterNode("name", "String")])

        function_call = TypeFunctionCallNode(VariableNode("Juan"), "not_greet", [StringNode("John"), NumberNode(2)])
        expression_block = LetNode([ParameterNode('Juan')],[NewNode("Person", [StringNode("Juan")])], function_call)
        node = ProgramNode([type_], expression_block)
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ["The Person type doesn't have a definition for not_greet"])

    def test_for_node_correct(self):
        scope = Scope()
        for_node = ForNode("i", FunctionCallNode("range", [NumberNode(0), NumberNode(10)]), NumberNode(1))
        node = ProgramNode([], for_node)
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, [])

    def test_for_node_incorrect(self):
        scope = Scope()
        expression_block = ExpressionBlockNode([NewNode("Person", [StringNode("John")]), VariableNode("j")])
        for_node = ForNode("i", FunctionCallNode("range", [NumberNode(0), StringNode(10)]), expression_block)
        node = ProgramNode([], for_node)
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ['Number expression was expected instead of String',
                                  "The Person type doesn't exist in the current context",
                                  "The j variable doesn't exist in the current context"])

    def test_while_node_correct(self):
        scope = Scope()

        destructive_expr = DestructiveExpression("i", ArithmeticExpression("+", VariableNode("i"), NumberNode(1)))
        expr_block_1 = ExpressionBlockNode([FunctionCallNode("print", [VariableNode("i")]), destructive_expr])
        while_ = WhileNode(ComparationExpression("<", VariableNode("i"), NumberNode(10)), expr_block_1)

        expr_block_2 = ExpressionBlockNode([while_])
        let_ = LetNode([ParameterNode("i", "Number")], [NumberNode(0)], expr_block_2)
        node = ProgramNode([], let_)

        result = self.visitor.visit(node, scope)
        self.assertEqual(result, [])

    def test_while_node_incorrect(self):
        scope = Scope()

        destructive_expr = DestructiveExpression("i", ArithmeticExpression("+", VariableNode("i"), NumberNode(1)))
        expr_block_1 = ExpressionBlockNode([FunctionCallNode("printp", [VariableNode("j")]), destructive_expr])
        while_ = WhileNode(ComparationExpression("<", VariableNode("i"), StringNode(10)), expr_block_1)

        expr_block_2 = ExpressionBlockNode([while_])
        let_ = LetNode([ParameterNode("i", "Number")], [NumberNode(0)], expr_block_2)
        node = ProgramNode([], let_)

        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ['Number expression was expected instead of String',
                                  "The printp function doesn't exist in the current context",
                                  "The j variable doesn't exist in the current context"])

    def test_simple_inheritance_polymorphism_correct(self):
        scope = Scope()
        base_type = TypeNode("Human", [], [])
        sub_type = TypeNode("Person", [], [])

        instantiation = NewNode("Person", [])
        let_ = LetNode([ParameterNode("john", "Human")], [instantiation], VariableNode("john"))
        node = ProgramNode([base_type, sub_type], let_)
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, [])

    def test_circular_inheritance(self):
        scope = Scope()
        type_a = TypeNode("TypeA", [], [], "TypeB")
        type_b = TypeNode("TypeB", [], [], "TypeA")

        node = ProgramNode([type_a, type_b], NumberNode(2))
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ["Circular inheritance detected between TypeA and TypeB"])

    def test_non_existing_parent(self):
        scope = Scope()
        type_a = TypeNode("TypeA", [], [], "TypeB")

        node = ProgramNode([type_a], NumberNode(2))
        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ["The TypeB type doesn't exist in the current context"])

    def test_inheritance_with_wrong_parent_params(self):
        scope = Scope()
        type_a = TypeNode("TypeA", [], [ParameterNode("name", "String")])
        type_b = TypeNode("TypeB", [], [ParameterNode("name", "String")], "TypeA",
                          [VariableNode("name"), NumberNode(1)])

        node = ProgramNode([type_a, type_b], NumberNode(2))

        result = self.visitor.visit(node, scope)
        self.assertEqual(result, ["Missmatch of parent constructor parameters on inheritance of TypeB from TypeA"])

    def test_base_call_no_inheritance(self):
        scope = Scope()
        function_body = FunctionCallNode("print", [FunctionCallNode("base", [])])
        function_ = FunctionNode("greet", [ParameterNode("name", "String")], function_body)
        type_a = TypeNode("person", [function_], [ParameterNode("name", "String")])

        node = ProgramNode([type_a], NumberNode(2))
        result = self.visitor.visit(node, scope)

        self.assertEqual(result, ["Parent doesn't have a definition for greet"])

    def test_base_call_no_base_on_parent(self):
        scope = Scope()
        function_body = FunctionCallNode("print", [FunctionCallNode("base", [])])
        function_ = FunctionNode("greet", [ParameterNode("name", "String")], function_body)
        type_b = TypeNode("human", [], [])
        type_a = TypeNode("person", [function_], [ParameterNode("name", "String")], "human", [])

        node = ProgramNode([type_a, type_b], NumberNode(2))
        result = self.visitor.visit(node, scope)

        self.assertEqual(result, ["Parent doesn't have a definition for greet"])

    def test_base_call_correct(self):
        scope = Scope()
        simple_greet = FunctionNode("greet", [ParameterNode("name", "String")], VariableNode("name"))
        greet_body = FunctionCallNode("print", [FunctionCallNode("base", [])])
        greet = FunctionNode("greet", [ParameterNode("name", "String")], greet_body)

        type_b = TypeNode("human", [simple_greet], [])
        type_a = TypeNode("person", [greet], [ParameterNode("name", "String")], "human", [])

        node = ProgramNode([type_a, type_b], NumberNode(2))
        result = self.visitor.visit(node, scope)

        self.assertEqual(result, [])

    def test_inheritance_from_reserved_types(self):
        scope = Scope()

        type_a = TypeNode("A", [], [], "void")
        type_b = TypeNode("B", [], [], "Number")
        type_c = TypeNode("C", [], [], "String")
        type_d = TypeNode("D", [], [], "Boolean")

        node = ProgramNode([type_a, type_b, type_d, type_c], NumberNode(2))
        result = self.visitor.visit(node, scope)

        self.assertEqual(result, [
            "Type A can't inherit from reserved type void",
            "Type B can't inherit from reserved type Number",
            "Type C can't inherit from reserved type String",
            "Type D can't inherit from reserved type Boolean",
        ])

    def test_inheritance_accessing_parent_members(self):
        scope = Scope()

        human = TypeNode("human", [TypeAtributeNode(ParameterNode("a", "Number"), NumberNode(2))], [])

        get_a_func = FunctionNode("get_a", [], SelfVariableNode(True, "a"))
        person = TypeNode("person", [get_a_func], [], "human", [])

        node = ProgramNode([human, person], NumberNode(2))
        result = self.visitor.visit(node, scope)

        self.assertEqual(result, ["The Person type doesn't have a definition for a"])

    def test_type_inherits_from_protocol(self):
        scope = Scope()

        protocol = ProtocolNode("ProtocolA", [])
        type_a = TypeNode("TypeA", [], [], "ProtocolA")

        node = ProgramNode([protocol, type_a], NumberNode(2))
        result = self.visitor.visit(node, scope)

        self.assertEqual(result, ["Type TypeA can't inherit from protocol ProtocolA"])

    def test_protocol_inherits_from_type(self):
        scope = Scope()

        type_a = TypeNode("TypeA", [], [])
        protocol = ProtocolNode("ProtocolA", [], "TypeA")

        node = ProgramNode([type_a, protocol], NumberNode(2))
        result = self.visitor.visit(node, scope)

        self.assertEqual(result, ["Protocol ProtocolA can't inherit from type TypeA"])

    def test_protocol_inherits_from_protocol(self):
        scope = Scope()

        protocol_base = ProtocolNode("ProtocolBase", [])
        protocol = ProtocolNode("ProtocolA", [], "ProtocolBase")

        node = ProgramNode([protocol_base, protocol], NumberNode(2))
        result = self.visitor.visit(node, scope)

        self.assertEqual(result, [])

    def test_protocol_polymorphism_correct(self):
        scope = Scope()

        protocol = ProtocolNode("Flyable", [ProtocolMethodNode("fly", [ParameterNode("distance", "Number")], "void")])

        fly_type_func = FunctionNode("fly", [ParameterNode("distance", "Number")],
                                     FunctionCallNode("print", [StringNode("temp")]), "void")
        type_a = TypeNode("Bird", [fly_type_func], [])

        let_ = LetNode([ParameterNode("rocio", "Flyable")], [NewNode("Bird", [])],
                       TypeFunctionCallNode(VariableNode("rocio"), "fly", [NumberNode(2)]))

        node = ProgramNode([protocol, type_a], let_)
        result = self.visitor.visit(node, scope)

        self.assertEqual(result, [])

    def test_protocol_polymorphism_wrong_method(self):
        scope = Scope()

        protocol = ProtocolNode("Flyable", [ProtocolMethodNode("fly", [ParameterNode("distance", "Number")], "void")])

        fly_type_func = FunctionNode("walk", [ParameterNode("distance", "Number")],
                                     FunctionCallNode("print", [StringNode("temp")]), "void")
        type_a = TypeNode("Bird", [fly_type_func], [])

        let_ = LetNode([ParameterNode("rocio", "Flyable")], [NewNode("Bird", [])],
                       TypeFunctionCallNode(VariableNode("rocio"), "fly", [NumberNode(2)]))

        node = ProgramNode([protocol, type_a], let_)
        result = self.visitor.visit(node, scope)

        self.assertEqual(result, ['Flyable expression was expected instead of Bird'])

    def test_variables_in_different_context(self):
        scope = Scope()

        # Define a LetNode in the 'if' branch
        let_if = LetNode([ParameterNode("a", "Number")], [NumberNode(5)], NumberNode(5))

        # Define a LetNode in the 'else' branch that tries to use 'a' from the 'if' branch
        let_else = LetNode([ParameterNode("b", "Number")], [NumberNode(6)],
                           ArithmeticExpression("+", VariableNode("a"), VariableNode("b")))

        # Define an IfElseExpression with the LetNodes
        if_else_expression = IfElseExpression([BooleanNode(True)], [let_if, let_else])

        # Define a ProgramNode with the IfElseExpression
        node = ProgramNode([], if_else_expression)

        # Visit the node with the SemanticCheckerVisitor
        result = self.visitor.visit(node, scope)

        # Assert that the result is an error message indicating that 'a' doesn't exist in the current context
        self.assertEqual(result, ["The a variable doesn't exist in the current context"])

    def test_is_expression(self):
        scope = Scope()

        is_expression = IsExpression(VariableNode("instance"), "NonExistentType")
        node = ProgramNode([], is_expression)
        result = self.visitor.visit(node, scope)

        self.assertEqual(result, [
            "The instance variable doesn't exist in the current context",
            "The NonExistentType type doesn't exist in the current context"
        ])

    def test_ultimate(self):
        scope = Scope()

        """
        protocol BaseProtocol{
            method(param: Number): void
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
        
        for i in range(0, 10){
            let instance: BaseProtocol = new TypeA() in 
                if i < 2 instance.method(2) 
                elif i >= 4 (instance as TypeA).another() 
                else "Temp";
        }
        """

        base_protocol = ProtocolNode("BaseProtocol",
                                     [ProtocolMethodNode("method", [ParameterNode("param", "Number")], "void")])

        child_protocol = ProtocolNode("ChildProtocol", [], "BaseProtocol")

        method_func = FunctionNode("method", [ParameterNode("param", "Number")],
                                   FunctionCallNode("print", [StringNode("temp")]), "void")

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

        node = ProgramNode([base_protocol, child_protocol, type_a], for_node)
        result = self.visitor.visit(node, scope)

        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
