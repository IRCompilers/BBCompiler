from src.Common import Visitor


class EvaluateVisitor(object):
    @Visitor.on('node')
    def visit(self, node, tabs):
        pass

    @Visitor.when(ConcatNode)
    def visit(self, node):
        left_auto = self.visit(node.left)
        right_auto = self.visit(node.right)
        return automata_concatenation(left_auto, right_auto)

    @Visitor.when(UnionNode)
    def visit(self, node):
        left_auto = self.visit(node.left)
        right_auto = self.visit(node.right)
        return automata_union(left_auto, right_auto)