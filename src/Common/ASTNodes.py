from typing import List,Union

'''
-Node
    -ProgramNode
    -ParameterNode
    -TypeAtributeNode
    -ProtocolMethodNode
    -StatementNode
        -FunctionNode
        -TypeNode
        -ProtocolNode
    -ExpressionNode
        -ExpressionBlockNode
        -SimpleExpressionNode
            
            ___(Less Priority)___
            -LetNode
            -IfElseExpression
            -DestructiveExpression
            -whileNode
            -forNode
            -newNode
            
            ___(Operations)___
            -OrAndExpression
            -NotExpression
            -ComparationExpression
            -IsExpression
            -StringConcatenationNode
            -AritmethicExpression
            
            __(High Priority)__
            -NumberNode
            -StringNode
            -BooleanNode
            -Variable
            -FunctionCallNode
            -TypeFunctionCallNode
            -ListNode
            -ImplicitListNode
            -InexingNode
            -asNode
'''


class Node:
    """
        Basic node class. The building block of the AST
    """
    pass

class StatementNode(Node):
    """
        A statement can be a Type definition, a method declaration, a expression or a protocol
    """
    pass

class ExpressionNode(StatementNode):
    '''
        An expression in HULK is anything that has a value
    '''
    pass

class ProgramNode(Node):
    '''
        A program in HULK is a collection of statements
    '''
    def __init__(self,Statements:list[StatementNode],Expression:ExpressionNode):
        self.Statements=Statements
        self.Expression=Expression

class ParameterNode(Node):
    '''
        Represents a parameter for a function/method, a constructor for a Type or a let expression
        A parameter must have a name, and the Type can be specified
    '''
    def __init__(self,Name:str,Type:str='Object'):
        self.name=Name
        self.Type=Type

class FunctionNode(StatementNode):
    '''
        This contains a declaration of a function.
        A function needs a name and and a expression.
        And it may contains parameters and a return Type
    '''
    def __init__(self,name:str,Parameters:list[ParameterNode],
                 Corpus:List[ExpressionNode],Type:str='Object'):
        self.name=name
        self.Parameters=Parameters
        self.Corpus=Corpus
        self.Type=Type

class TypeAtributeNode(Node):
    '''
        This is an atribute of a class. It has a name and a value from a expression
    '''
    def __init__(self,name:str,value:ExpressionNode):
        self.name=name
        self.value=value

class TypeNode(StatementNode):
    '''
        This contains a class declaration.
        Contains a name and a corpus.
        It may have a constructor an a parent in hierarchy
        In case of hierarchy, you can call arguments for the parent
    '''
    def __init__(self,name:str,Corpus:list[Union[FunctionNode,TypeAtributeNode]]
                 ,Parameters:list[ParameterNode]=[],inherits:str="Object",Arguments:list[ExpressionNode]=[]):
        self.name=name
        self.Corpus=Corpus
        self.ConstructorParameters=Parameters
        self.inherits=inherits
        self.Arguments=Arguments

class ProtocolMethodNode(Node):
    '''
        This is a abstract method inside of a protocol.
        Needs to have a name, a Type and a Typed Parameter List
    '''
    def __init__(self,name:str,Parameters:List[ParameterNode],Type:str):
        self.name=name
        self.Parameters=Parameters
        self.Type=Type

class ProtocolNode(StatementNode):
    '''
        This is a protocol. It has a name and and a list of fully-Typed methods.
        A protocol may extend another protocol
    '''
    def __init__(self,name:str,Corpus:List[ProtocolMethodNode],extends:str=''):
        self.name=name
        self.Corpus=Corpus
        self.extends=extends

class ExpressionBlockNode(ExpressionNode):
    '''
        This node represents a list of Expressions joined together.
    '''
    def __init__(self,Expressions:List[ExpressionNode]):
        self.Expressions=Expressions

class SimpleExpressionNode(ExpressionNode):
    '''
        This class is only a distinction of a ExpressionBlock
    '''
    pass

class LetNode(SimpleExpressionNode):
    '''
        Contains a Let expression. Contains a list of variables,
        his corresponding expressions for his values and the expression to aplied
    '''
    def __init__(self,variableNames:List[ParameterNode],
                 variableValues:List[SimpleExpressionNode], 
                 Expression:ExpressionNode):
        self.variables=variableNames
        self.variables_values=variableValues
        self.Expression=Expression

class IfElseExpression(SimpleExpressionNode):
    '''
        Contains the semantic of the conditionals.
        It has a list of conditions (the condition of the if, 
            then the condition of the first elif...)
        And a list of expression (the if case, the first elif case... and the else case)
    '''
    def __init__(self,Conditions:List[SimpleExpressionNode],Expressions:List[ExpressionNode]):
        self.Conditions=Conditions
        self.cases=Expressions

class DestructiveExpression(SimpleExpressionNode):
    '''
        This is contains the semantic for := operator.
        It has the varible name and the Expression.
    '''
    def __init__(self,name:str,Expression:SimpleExpressionNode):
        self.name=name
        self.Expression=Expression
    
class whileNode(SimpleExpressionNode):
    '''
        Has the semantic for a while cicle. Contains the condition and the expressions
    '''
    def __init__(self,Condition:SimpleExpressionNode,Expression:ExpressionNode):
        self.Condition=Condition
        self.Expression=Expression
    
class forNode(SimpleExpressionNode):
    '''
        Has the semantic for a for cicle. Contains the colection, the iterator and the expressions
    '''
    def __init__(self,name:str,Colection:SimpleExpressionNode,Expression:ExpressionNode):
        self.name=name
        self.Colection=Colection
        self.Expression=Expression
    
class NewNode(SimpleExpressionNode):
    '''
        Contains the new operator. Contains the name of a Type and the constructor arguments
    '''
    def __init__(self,name:str,Arguments:List[SimpleExpressionNode]):
        self.name=name
        self.arguments=Arguments    

class OrAndExpression(SimpleExpressionNode):
    '''
        Contains the operators &, |.
    '''
    def __init__(self,operation:str,left:SimpleExpressionNode,right:SimpleExpressionNode):
        self.left=left
        self.right=right
        self.operation=operation
    
class NotExpression(SimpleExpressionNode):
    '''
        Contains the operator !.
    '''
    def __init__(self,left:SimpleExpressionNode):
        self.left=left
    
class ComparationExpression(SimpleExpressionNode):
    '''
        Contains the operators >, <, <=, >=, ==. Recive 2 expressions and compares them
    '''
    def __init__(self,operation:str,left:SimpleExpressionNode,right:SimpleExpressionNode=None):
        self.left=left
        self.right=right
        self.operation=operation
    
class IsExpression(SimpleExpressionNode):
    '''
        Contains the operator is
    '''
    def __init__(self,left:SimpleExpressionNode,name:str):
        self.left=left
        self.name=name

    
class StringConcatenationNode(SimpleExpressionNode):
    '''
        Contains the @ and @@ operators
    '''
    def __init__(self,left:SimpleExpressionNode
                 ,right:SimpleExpressionNode,double:bool=False):
        self.Left=left
        self.right=right
        self.double=double
    
class AritmethicExpression(SimpleExpressionNode):
    '''
        Contains all the aritmethic expressions:
        + - * ** ^ / // %
        The unary expression -Expression is included has 0-Expression
    '''
    def __init__(self,operation:str,left:SimpleExpressionNode
                 ,right:SimpleExpressionNode):
        self.left=left
        self.right=right
        self.operation=operation

class asNode(SimpleExpressionNode):
    '''
        as operator
    '''
    def __init__(self,left:SimpleExpressionNode,right:str):
        self.Expression=left
        self.Type=right

class NumberNode(SimpleExpressionNode):
    '''
        Contains a number value
    '''
    def __init__(self,value):
        self.value=value
    
class StringNode(SimpleExpressionNode):
    '''
        Contains a string value
    '''
    def __init__(self,value):
        self.value=value
class BooleanNode(SimpleExpressionNode):
    '''
        True or False
    '''
    def __init__(self, value):
        self.value=value
class Variable(SimpleExpressionNode):
    '''
        A variable
    '''
    def __init__(self,name:str):
        self.name=name

class FunctionCallNode(SimpleExpressionNode):
    '''
        A function call. Recieves a name and arguments
    '''
    def __init__(self,name:str,arguments:List[SimpleExpressionNode]):
        self.function=name
        self.Arguments=arguments

class TypeFunctionCallNode(SimpleExpressionNode):
    '''
        The combination of the last two
    '''
    def __init__(self,classCalling:SimpleExpressionNode,name:str,arguments:List[SimpleExpressionNode]):
        self.classCalling=classCalling
        self.function=name
        self.Arguments=arguments
    
class ListNode(SimpleExpressionNode):
    '''
        Represents a list in code. It receives an array with its elements
    '''
    def __init__(self,Expressions:List[SimpleExpressionNode]):
        self.Elements=Expressions

class ImplicitListNode(SimpleExpressionNode):
    '''
        This is for a implicit list.
        The operator is an operation to do to each element of a collection
        The iterator is the name of a element from the collection in the operator
    '''
    def __init__(self,operator:SimpleExpressionNode,iterator:str,collection:SimpleExpressionNode):
        self.operator=operator
        self.iterator=iterator
        self.collection=collection

class InexingNode(SimpleExpressionNode):
    '''
        This  node represents an indexing on a object
    '''
    def __init__(self,collection:SimpleExpressionNode,index:SimpleExpressionNode):
        self.collection=collection
        self.index=index