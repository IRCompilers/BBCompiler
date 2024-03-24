from src.CodeGen.CodeContext import CodeContext
from src.Common import Visitor
from src.Common.ASTNodes import *
from src.Common.IContext import Variable


class InterpretVisitor:

    built_in_functions = {
        "print": lambda x: print(x),
    }

    @Visitor.on('node')
    def visit(self, node, tabs):
        pass

    @Visitor.when(ProgramNode)
    def visit(self, node):
        context = CodeContext()

        for v in node.Statements:
            self.visit(v, context)

        self.visit(node.Expression, context)

    @Visitor.when(ParameterNode)
    def visit(self, node, context: CodeContext):
        return node.Name, node.Type

    @Visitor.when(LetNode)
    def visit(self, node, context: CodeContext):
        child_context = CodeContext(context)
        for par, value in zip(node.variables, node.variables_values):
            variable = Variable(par.Name, par.Type[0], self.visit(value, context))
            child_context.variables[par.Name] = variable

        return self.visit(node.Expression, child_context)

    @Visitor.when(FunctionCallNode)
    def visit(self, node, context: CodeContext):


    @Visitor.when(AritmethicExpression)
    def visit(self, node, context: CodeContext):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)

        if node.operation == "+":
            return left + right
        elif node.operation == "-":
            return left - right
        elif node.operation == "*":
            return left * right
        elif node.operation == "/":
            return left / right
        elif node.operation == "**" or node.operation == "^":
            return left ** right
        elif node.operation == "%":
            return left % right
        else:
            raise Exception("Invalid operator")

    @Visitor.when(NumberNode)
    def visit(self, node, context: CodeContext):
        return node.value

    @Visitor.when(StringNode)
    def visit(self, node, context: CodeContext):
        return node.value

    @Visitor.when(BooleanNode)
    def visit(self, node, context: CodeContext):
        return node.value

    @Visitor.when(VariableNode)
    def visit(self, node, context: CodeContext):
        return context.get_variable(node.name).value


# Test the above
par_node = ParameterNode("x", "int")
second_par_node = ParameterNode("y", "int")
plus_node = AritmethicExpression("+", VariableNode("x"), VariableNode("y"))
let_node = LetNode([par_node, second_par_node], [NumberNode(111), NumberNode(222)], plus_node)
print_node = PrintNode(let_node)
program = ProgramNode([], print_node)

interpreter = InterpretVisitor()
interpreter.visit(program)
