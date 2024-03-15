from Ast import *
from src.Common import Visitor
from src.Common.AutomatonOperations import *


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

    @Visitor.when(ClosureNode)
    def visit(self, node):
        child_auto = self.visit(node.child)
        return automata_closure(child_auto)

    @Visitor.when(PClosureNode)
    def visit(self, node):
        child_auto = self.visit(node.child)
        return automata_pclosure(child_auto)

    @Visitor.when(PossibleNode)
    def visit(self, node):
        child_auto = self.visit(node.child)
        return automata_possible(child_auto)

    @Visitor.when(NotNode)
    def visit(self, node):
        child_auto = self.visit(node.child)
        return automata_not(child_auto)

    @Visitor.when(LiteralNode)
    def visit(self, node):
        lex = node.value
        return automata_symbol(lex)

    @Visitor.when(EllipsisNode)
    def visit(self, node):
        left_lex = node.left.value
        right_lex = node.right.value

        # Get ASCII values of left_lex and right_lex
        left_ascii = ord(left_lex)
        right_ascii = ord(right_lex)

        # Generate all ASCII values in between
        ascii_values_in_between = range(left_ascii + 1, right_ascii)

        # Convert ASCII values back to characters
        characters_in_between = [chr(ascii_value) for ascii_value in ascii_values_in_between]

        # Build the automata
        left = automata_symbol(left_lex)
        right = automata_symbol(right_lex)

        result = automata_union(left, right)

        for c in characters_in_between:
            result = automata_union(result, automata_symbol(c))

        return result
