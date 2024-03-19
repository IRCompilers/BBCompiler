from typing import List,Union

class Node:
    pass

class StatementNode(Node):
    pass

class ExpressionNode(StatementNode):
    def valueType(self)->List[str]:
        pass

class ProgramNode(Node):
    def __init__(self,Statements:list[StatementNode]):
        self.Statements=Statements

class ParameterNode(Node):
    def __init__(self,Name:str,Type:str=''):
        self.name=Name
        self.Type=[] if Type=='' else [Type]

class FunctionNode(StatementNode):
    def __init__(self,name:str,Parameters:list[ParameterNode],
                 Corpus:List[ExpressionNode],Type=''):
        self.name=name
        self.Parameters=Parameters
        self.Corpus=Corpus
        self.type=[] if Type=='' else [Type]

class ClassAtributeNode(Node):
    def __init__(self,name:str,value:ExpressionNode):
        self.name=name
        self.value=value
        self.type=value.valueType()

class TypeNode(StatementNode):
    def __init__(self,name:str,Corpus:list[Union[FunctionNode,ClassAtributeNode]],Parameters:list[ParameterNode]=[]
                 ,inherits:str="",Arguments=[]):
        self.name=name
        self.Corpus=Corpus
        self.ConstructorParameters=Parameters
        self.inherits=inherits
        self.Arguments=Arguments

class ProtocolMethodNode(Node):
    def __init__(self,name:str,Parameters:List[ParameterNode],type:str):
        self.name=name
        self.Parameters=Parameters
        self.type=type

class ProtocolNode(StatementNode):
    def __init__(self,name:str,Corpus,extends:str=''):
        self.name=name
        self.Corpus=Corpus
        self.extends=extends

class ExpressionBlockNode(ExpressionNode):
    def __init__(self,Expressions:List[ExpressionNode]):
        self.Expressions=Expressions
    def valueType(self):
        return self.Expressions[-1].valueType()

class SimpleExpressionNode(ExpressionNode):
    pass

class LetNode(SimpleExpressionNode):
    def __init__(self,variableNames:List[ParameterNode],variableValues:List[SimpleExpressionNode]
                 ,Expression:ExpressionNode):
        self.variables=variableNames
        self.variables_values=variableValues
        self.Expression=Expression
    def valueType(self)->List[str]:
        return self.Expression.valueType()
    
class IfElseExpression(SimpleExpressionNode):
    def __init__(self,Conditions:List[SimpleExpressionNode],Expressions:List[ExpressionNode]):
        self.Conditions=Conditions
        self.cases=Expressions
    def valueType(self)->List[str]:
        PossibleValues=set()
        for Expression in self.cases:
            PossibleValues=PossibleValues.union(Expression.valueType)
        return PossibleValues

class DestructiveExpression(SimpleExpressionNode):
    def __init__(self,name:str,Expression:SimpleExpressionNode):
        self.name=name
        self.Expression=Expression
    def valueType(self) -> List[str]:
        return self.Expression.valueType()
    
class whileNode(SimpleExpressionNode):
    def __init__(self,Condition:SimpleExpressionNode,Expression:ExpressionNode):
        self.Condition=Condition
        self.Expression=Expression
    def valueType(self) -> List[str]:
        return self.Expression.valueType()
    
class whileNode(SimpleExpressionNode):
    def __init__(self,name:str,Condition:SimpleExpressionNode,Expression:ExpressionNode):
        self.name=name
        self.Condition=Condition
        self.Expression=Expression
    def valueType(self) -> List[str]:
        return self.Expression.valueType()

class ClassDeclarationNode(SimpleExpressionNode):
    def __init__(self,name:str,Arguments:List[SimpleExpressionNode]):
        self.name=name
        self.arguments=Arguments
    def valueType(self) -> List[str]:
        return [self.name]

class BooleanNode(SimpleExpressionNode):
    def __init__(self, value):
        self.value=value
    def valueType(self) -> List[str]:
        return ['bool']

class BooleanExpression(SimpleExpressionNode):
    def __init__(self,operation:str,left:SimpleExpressionNode,right:SimpleExpressionNode=None):
        self.left=left
        self.right=right
        self.operation=operation
    def valueType(self) -> List[str]:
        return ['bool']
    
class StringNode(SimpleExpressionNode):
    def __init__(self,value):
        self.value=value
    def valueType(self) -> List[str]:
        return ['string']
    
class StringConcatenationNode(SimpleExpressionNode):
    def __init__(self,left:SimpleExpressionNode
                 ,right:SimpleExpressionNode,double:bool=False):
        self.Left=left
        self.right=right
        self.double=double
    def valueType(self) -> List[str]:
        return ['string']

class NumberNode(SimpleExpressionNode):
    def __init__(self,value):
        self.value=value
    def valueType(self) -> List[str]:
        return ['Number']

class AritmethicExpression(SimpleExpressionNode):
    def __init__(self,operation:str,left:SimpleExpressionNode
                 ,right:SimpleExpressionNode=None):
        self.left=left
        self.right=right
        self.operation=operation
    def valueType(self) -> List[str]:
        return ['Number']
    
class Variable(SimpleExpressionNode):
    def __init__(self,name:str):
        self.name=name
    def valueType(self) -> List[str]:
        return []

class FunctionCallNode(SimpleExpressionNode):
    def __init__(self,name:str,arguments:List[SimpleExpressionNode]):
        self.function=name
        self.Arguments=arguments
    def valueType(self) -> List[str]:
        return []

class ClassAtributeCallNode(SimpleExpressionNode):
    def __init__(self,classCalling:SimpleExpressionNode,Atribute:str):
        self.classCalling=classCalling
        self.Atribute=Atribute
    def valueType(self) -> List[str]:
        return []

class ClassFunctionCallNode(SimpleExpressionNode):
    def __init__(self,classCalling:SimpleExpressionNode,name:str,arguments:List[SimpleExpressionNode]):
        self.classCalling=classCalling
        self.function=name
        self.Arguments=arguments
    def valueType(self) -> List[str]:
        return []
    
class ListNode(SimpleExpressionNode):
    def __init__(self,Expressions:List[SimpleExpressionNode]):
        self.Elements=ExpressionNode()
    def valueType(self) -> List[str]:
        return [List]

class ImplicitListNode(SimpleExpressionNode):
    def __init__(self,operator:SimpleExpressionNode,iterator:str,collection:SimpleExpressionNode):
        self.operator=ExpressionNode()
        self.iterator=iterator
        self.collection=collection
    def valueType(self) -> List[str]:
        return [List]

class InexingNode(SimpleExpressionNode):
    def __init__(self,collection:SimpleExpressionNode,index:SimpleExpressionNode):
        self.collection=collection
        self.index=index
    def valueType(self) -> List[str]:
        return []

class asNode(SimpleExpressionNode):
    def __init__(self,left:SimpleExpressionNode,right:str):
        self.Expression=left
        self.type=right
    def valueType(self) -> List[str]:
        return [self.right]
