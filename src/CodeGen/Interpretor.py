from src.CodeGen.CodeContext import CodeContext
from src.Common import Visitor
from src.Common.ASTNodes import *
from src.Common.IContext import Variable
import math
import random

class InterpretVisitor:
    def __init__(self):
        self.last_value_returned=None

    

    @Visitor.on('node')
    def visit(self, node, context):
        pass

    @Visitor.when(ProgramNode)
    def visit(self, node:ProgramNode, context:CodeContext):
        
        context = CodeContext()
        
        built_in_functions = {
        "print": lambda x: print(x[0]),
        "sen": lambda x: math.sin(x[0]),
        "cos": lambda x:math.cos(x[0]),
        "range": lambda x: range(x[0],x[1]),
        "exp": lambda x: math.exp(x[0]),
        "log": lambda x: math.exp(x[0],x[1]),
        "sqrt": lambda x: math.sqrt(x[0]),
        "rand": lambda x: random.random()
        }
        for f in built_in_functions.keys:
            context.def_function(f,built_in_functions[f])
        
        for v in [x for x in node.STATEMENTS if not type(v) is ProtocolNode]:
            self.visit(v, context)
            if type(v) is TypeNode:
                context.def_type(v.NAME,self.last_value_returned)
            if type(v) is FunctionNode:
                context.def_function(v.NAME,self.last_value_returned)
        self.visit(node.EXPRESSION, context)

    @Visitor.when(TypeNode)
    def visit(self, node:TypeNode, context:CodeContext):
        type_context=CodeContext(context)
        visitor=self
        #modificar, añadir clase heredada
        class NewType:
            def __init__(self, parameters):
                constructor_context=CodeContext(context)

                for i in len(node.CONSTRUCTOR):
                    constructor_context.def_variable(node.CONSTRUCTOR[i].NAME,parameters[i])
                
                for x in [x for x in node.CORPUS if type(x) is TypeAtributeNode]:
                    visitor.visit(x.VALUE,constructor_context)
                    type_context.def_variable(x.VAR.NAME,visitor.last_value_returned)
                
                for x in [x for x in node.CORPUS if type(x) is FunctionNode]:
                    visitor.visit(x,type_context)
                    type_context.def_function(x,visitor.last_value_returned)
            
            def call(self,name,parameters):
                return type_context.get_function(name,False)(parameters)
        
        self.last_value_returned=NewType


    @Visitor.when(FunctionNode)
    def visit(self, node:FunctionNode,context):
        function_context=CodeContext(context)
        def new_function(parameters):
            for i in len(node.PARAMETERS):
                function_context.def_variable(node.PARAMETERS[i].NAME,parameters[i])
            self.visit(node.CORPUS,function_context)
            return self.last_value_returned
        self.last_value_returned=new_function

    @Visitor.when(ExpressionBlockNode)
    def visit(self, node:ExpressionBlockNode, context: CodeContext):
        for e in node.EXPRESSIONS:
            self.visit(e)

    @Visitor.when(LetNode)
    def visit(self, node:LetNode, context: CodeContext):
        self.visit(node.VAR_VALUES[0],context)
        child_context = CodeContext(context)
        child_context.def_variable(node.VARS[0].NAME,self.last_value_returned)
        if len(node.VARS)>1:
            rest=LetNode(node.VARS[1:],node.VAR_VALUES[1:],node.EXPRESSION)
            self.visit(rest,child_context)
        else:
            self.visit(node.EXPRESSION,child_context)

    @Visitor.when(IfElseExpression)
    def visit(self, node:IfElseExpression, context: CodeContext):
        for case in len(node.CONDITIONS):
            self.visit(node.CONDITIONS[case],context)
            if self.last_value_returned:
                self.visit(node.CASES[case],context)
                return
        self.visit(node.CASES[-1],context)

    @Visitor.when(DestructiveExpression)
    def visit(self, node:DestructiveExpression, context: CodeContext):
        self.visit(node.EXPRESSION,context)
        context.edit_variable(node.NAME,self.last_value_returned)

    @Visitor.when(SelfDestructiveExpression)
    def visit(self, node:SelfDestructiveExpression, context: CodeContext):
        #modificar, evitar el caso de sobrecarga
        self.visit(node.EXPRESSION,context)
        context.edit_variable(node.VAR.NAME,self.last_value_returned)

    @Visitor.when(WhileNode)
    def visit(self, node:WhileNode, context: CodeContext):
        self.visit(node.CONDITIONS,context)
        while(self.last_value_returned):
            self.visit(node.EXPRESSION,context)
            returnValue=self.last_value_returned
            self.visit(node.CONDITIONS,context)
        self.last_value_returned=returnValue

    @Visitor.when(ForNode)
    def visit(self, node:ForNode, context: CodeContext):
        #modificar: para aquello que sea iterable
        self.visit(node.COLECTION,context)
        collection=self.last_value_returned
        for_context=CodeContext(context)
        for_context.def_variable(node.NAME,None)
        for x in collection:
            for_context.edit_variable(node.NAME,x)
            self.visit(node.EXPRESSION,for_context)
    
    @Visitor.when(NewNode)
    def visit(self, node:NewNode, context: CodeContext):
        self.last_value_returned=context.get_type(node.NAME)(node.ARGS)

    @Visitor.when(OrAndExpression)
    def visit(self, node:OrAndExpression, context: CodeContext):
        self.visit(node.LEFT, context)
        left=self.last_value_returned
        self.visit(node.RIGHT, context)
        right=self.last_value_returned

        if node.OPERATION == "&":
            self.last_value_returned = left and right
        elif node.OPERATION == "|":
            self.last_value_returned = left or right
        else:
            raise Exception("Invalid operator")

    @Visitor.when(ComparationExpression)
    def visit(self, node:ComparationExpression, context: CodeContext):
        #modificar. para aquello que sea comparable
        self.visit(node.LEFT, context)
        left=self.last_value_returned
        self.visit(node.RIGHT, context)
        right=self.last_value_returned

        if node.OPERATION == "==":
            self.last_value_returned = left == right
        elif node.OPERATION == "<":
            self.last_value_returned = left < right
        elif node.OPERATION == ">":
            self.last_value_returned = left > right
        elif node.OPERATION == "!=":
            self.last_value_returned = left != right
        elif node.OPERATION == ">=":
            self.last_value_returned = left >= right
        elif node.OPERATION == "<=":
            self.last_value_returned = left <= right
        else:
            raise Exception("Invalid operator")

    @Visitor.when(StringConcatenationNode)
    def visit(self, node:StringConcatenationNode, context: CodeContext):
        #Modificar, para aquello que sea printable
        self.visit(node.LEFT, context)
        left=self.last_value_returned
        self.visit(node.RIGHT, context)
        right=self.last_value_returned
        if node.DOUBLE:
            self.last_value_returned=left+' '+right
        else:
            self.last_value_returned=left+right

    @Visitor.when(AritmethicExpression)
    def visit(self, node:AritmethicExpression, context: CodeContext):
        self.visit(node.LEFT, context)
        left=self.last_value_returned
        self.visit(node.RIGHT, context)
        right=self.last_value_returned

        if node.OPERATION == "+":
            self.last_value_returned = left + right
        elif node.OPERATION == "-":
            self.last_value_returned = left - right
        elif node.OPERATION == "*":
            self.last_value_returned = left * right
        elif node.OPERATION == "/":
            self.last_value_returned = left / right
        elif node.OPERATION == "**" or node.OPERATION == "^":
            self.last_value_returned = left ** right
        elif node.OPERATION == "%":
            self.last_value_returned = left % right
        else:
            raise Exception("Invalid operator")

    @Visitor.when(NumberNode)
    def visit(self, node:NumberNode, context: CodeContext):
        self.last_value_returned=node.VALUE

    @Visitor.when(StringNode)
    def visit(self, node:StringNode, context: CodeContext):
        self.last_value_returned=node.VALUE

    @Visitor.when(BooleanNode)
    def visit(self, node:BooleanNode, context: CodeContext):
        self.last_value_returned=node.VALUE

    @Visitor.when(VariableNode)
    def visit(self, node:VariableNode, context: CodeContext):
        self.last_value_returned= context.get_variable(node.NAME).value

    @Visitor.when(SelfVariableNode)
    def visit(self, node:SelfVariableNode, context: CodeContext):
        #modificar. buscar donde es
        self.last_value_returned= context.get_variable(node.NAME).value

    @Visitor.when(FunctionCallNode)
    def visit(self, node:FunctionCallNode, context: CodeContext):
        Arguments=[]
        for x in node.ARGS:
            self.visit(x,context)
            Arguments.append(self.last_value_returned)
        self.last_value_returned= context.get_function(node.FUNCT)(Arguments)


    @Visitor.when(TypeFunctionCallNode)
    def visit(self, node:TypeFunctionCallNode, context: CodeContext):
        Arguments=[]
        for x in node.ARGS:
            self.visit(x,context)
            Arguments.append(self.last_value_returned)
        self.last_value_returned= context.get_type(node.CLASS).call(node.FUNCT,Arguments)
    
    @Visitor.when(ListNode)
    def visit(self, node:ListNode, context: CodeContext):
        elements=[]
        for x in node.ELEMENTS:
            self.visit(x,context)
            elements.append(self.last_value_returned)
        self.last_value_returned= elements
    
    @Visitor.when(ImplicitListNode)
    def visit(self, node:ImplicitListNode, context: CodeContext):
        #Editar para iterables
        elements=[]
        self.visit(node.COLLECTION,context)
        collection=self.last_value_returned
        List_context=CodeContext(context)
        List_context.def_variable(node.ITERATION,None)
        
        for x in collection:
            List_context.edit_variable(node.ITERATION,x)
            self.visit(node.OPERATION,List_context)
            elements.append(self.last_value_returned)
        self.last_value_returned= elements
    
    @Visitor.when(InexingNode)
    def visit(self, node:InexingNode, context: CodeContext):
        self.visit(node.INDEX,context)
        i=self.last_value_returned
        self.visit(node.COLLECTION,context)
        self.last_value_returned=self.last_value_returned[i]
    
    @Visitor.when(asNode)#Implementar
    def visit(self,node:asNode,context: CodeContext):
        self.visit(node.EXPRESSION,context)

# Test the above
par_node = ParameterNode("x", "int")
second_par_node = ParameterNode("y", "int")
plus_node = AritmethicExpression("+", Variable("x"), Variable("y"))
let_node = LetNode([par_node, second_par_node], [NumberNode(111), NumberNode(222)], plus_node)
print_node = FunctionCallNode('print',[let_node])
program = ProgramNode([], print_node)

interpreter = InterpretVisitor()
interpreter.visit(program)
