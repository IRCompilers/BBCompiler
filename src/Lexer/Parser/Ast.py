from pydantic import BaseModel


class Node(BaseModel):
    pass


class UnaryNode(Node):
    child: Node


class BinaryNode(Node):
    left: Node
    right: Node


class LiteralNode(Node):
    value: str


class VocabularyNode(Node):
    pass


class ClosureNode(UnaryNode):
    pass


class NotNode(UnaryNode):
    pass


class PClosureNode(UnaryNode):
    pass


class PossibleNode(UnaryNode):
    pass


class EllipsisNode(BinaryNode):
    pass


class UnionNode(BinaryNode):
    pass


class ConcatNode(BinaryNode):
    pass
