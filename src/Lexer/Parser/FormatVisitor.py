from src.Lexer.Parser.Ast import *
from src.Common import Visitor


class FormatVisitor(object):
    @Visitor.on('node')
    def visit(self, node, tabs):
        pass

    @Visitor.when(ConcatNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> Concat <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @Visitor.when(UnionNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> Union <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @Visitor.when(ClosureNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__ClosureNode: <expr>*'
        expr = self.visit(node.child, tabs + 1)
        return f'{ans}\n{expr}'

    @Visitor.when(PClosureNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__PClosureNode: <expr>+'
        body = self.visit(node.child, tabs + 1)
        return f'{ans}\n{body}'

    @Visitor.when(BinaryNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__<expr> {node.__class__.__name__} <expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @Visitor.when(PossibleNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__PossibleNode: <expr>?'
        body = self.visit(node.child, tabs + 1)
        return f'{ans}\n{body}'

    @Visitor.when(NotNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__NotNode: <expr>?'
        body = self.visit(node.child, tabs + 1)
        return f'{ans}\n{body}'

    @Visitor.when(LiteralNode)
    def visit(self, node, tabs=0):
        return '\t' * tabs + f'\\__LiteralNode: {node.value}'

    @Visitor.when(EllipsisNode)
    def visit(self, node, tabs=0):
        ans = '\t' * tabs + f'\\__EllipsisNode: <expr>...<expr>'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'
