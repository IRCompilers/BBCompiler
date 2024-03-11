from typing import Any

from pydantic import BaseModel, validator

from src.Common.Automaton import NFA
from src.Common.AutomatonOperations import automata_closure, automata_concatenation, automata_union
from src.Common.AutomatonUtils import nfa_to_dfa


class Node(BaseModel):
    def evaluate(self) -> NFA:
        raise NotImplementedError()


class AtomicNode(Node):
    lex: str


class UnaryNode(Node):
    node: Node

    def evaluate(self) -> NFA:
        value = self.node.evaluate()
        return self.operate(value)

    @staticmethod
    def operate(value: Any) -> NFA:
        raise NotImplementedError()


class BinaryNode(Node):
    left: Node
    right: Node

    def evaluate(self) -> NFA:
        lvalue = self.left.evaluate()
        rvalue = self.right.evaluate()
        return self.operate(lvalue, rvalue)

    @staticmethod
    def operate(lvalue: Any, rvalue: Any) -> Any:
        raise NotImplementedError()


class EpsilonNode(AtomicNode):
    def evaluate(self) -> NFA:
        return NFA(states=1, finals=[0], transitions={})


class SymbolNode(AtomicNode):
    def evaluate(self) -> NFA:
        return NFA(states=2, finals=[1], transitions={(0, self.lex): [1]})


class ClosureNode(UnaryNode):
    @staticmethod
    def operate(value: Any) -> NFA:
        return automata_closure(value)


class PClosureNode(UnaryNode):
    @staticmethod
    def operate(value: Any) -> NFA:
        return automata_concatenation(value, automata_closure(value))


class UnionNode(BinaryNode):
    @staticmethod
    def operate(lvalue: Any, rvalue: Any) -> Any:
        return automata_union(lvalue, rvalue)


class ConcatNode(BinaryNode):
    @staticmethod
    def operate(lvalue: Any, rvalue: Any) -> Any:
        return automata_concatenation(lvalue, rvalue)


class EllipsisNode(BinaryNode):
    left: SymbolNode
    right: SymbolNode

    @validator('left', 'right')
    def check_nodes(cls, v):
        if not isinstance(v, SymbolNode):
            raise ValueError('left and right nodes must be of type SymbolNode')
        return v

    def evaluate(self) -> NFA:
        l_lex = self.left.lex
        r_lex = self.right.lex

        # Get the ascii codes for the symbols
        l_ascii = ord(l_lex)
        r_ascii = ord(r_lex)

        if l_ascii > r_ascii:
            l_ascii, r_ascii = r_ascii, l_ascii

        # Generate the list of symbols
        symbols_nodes = [SymbolNode(lex=chr(i)) for i in range(l_ascii + 1, r_ascii)]
        result = automata_union(self.left.evaluate(), self.right.evaluate())

        for v in symbols_nodes:
            result = automata_union(result, v.evaluate())

        return result


closure = PClosureNode(node=SymbolNode(lex="b"))
union = UnionNode(left=SymbolNode(lex="c"), right=SymbolNode(lex="d"))
union2 = UnionNode(left=SymbolNode(lex="a"), right=closure)
concat = ConcatNode(left=union, right=union2)

dfa = nfa_to_dfa(concat.evaluate())

print(dfa.transitions)
print(dfa.finals)
