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
        self.assertEqual(result, ['Number expression was expected instead of void'])

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
                         [TypeAtributeNode(ParameterNode("age", "Number"), StringNode(-1)),
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

        function_call = TypeFunctionCallNode(StringNode("person"), "greet", [StringNode("John"), NumberNode(2)])
        expression_block = ExpressionBlockNode([NewNode("Person", [StringNode("John")]), function_call])
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

        function_call = TypeFunctionCallNode(StringNode("person"), "not_greet", [StringNode("John"), NumberNode(2)])
        expression_block = ExpressionBlockNode([NewNode("Person", [StringNode("John")]), function_call])
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




if __name__ == '__main__':
    unittest.main()
