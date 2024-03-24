from src.Common import Visitor
from src.Common.ASTNodes import *


class EvaluateVisitor:
    @Visitor.on('node')
    def visit(self, node, tabs):
        pass

    @Visitor.when(ProgramNode)
    def visit(self, node):
        code = "#include <stdio.h>\n"

        for v in node.Statements:
            code += self.visit(v)

        expressionCode = self.visit(node.Expression)
        code += "int main() {\n"
        code += expressionCode
        code += "return 0;\n}"

        return code

    @Visitor.when(PrintNode)
    def visit(self, node):
        expression = self.visit(node.expression)
        expression = expression.replace('%', '%%')
        return "printf(" + expression + ");\n"

    @Visitor.when(NumberNode)
    def visit(self, node):
        return str(node.value)

    @Visitor.when(StringNode)
    def visit(self, node):
        return "\"" + node.value + "\""

    @Visitor.when(BooleanNode)
    def visit(self, node):
        return str(node.value).lower()

    @staticmethod
    def write_to_file(code, file_name):
        with open(file_name, 'w') as file:
            file.write(code)


# Test the above
number = NumberNode("10")
print_node = PrintNode(number)
program = ProgramNode([], print_node)

code_generator = EvaluateVisitor()
code = code_generator.visit(program)
code_generator.write_to_file(code, "test.c")
