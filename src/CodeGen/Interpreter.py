from src.CodeGen.CodeContext import CodeContext
from src.Common import Visitor
from src.Common.ASTNodes import *
from src.Common.IContext import Variable
import math
import random


class InterpretVisitor(object):
    def __init__(self):
        self.last_value_returned = None

    @Visitor.on('node')
    def visit(self, node, context):
        pass

    @Visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):

        context = CodeContext()

        built_in_functions = {
            "print": lambda x: print(x[0]),
            "sen": lambda x: math.sin(x[0]),
            "cos": lambda x: math.cos(x[0]),
            "range": lambda x: list(range(int(x[0]), int(x[1]))),
            "exp": lambda x: math.exp(x[0]),
            "log": lambda x: math.exp(x[0], x[1]),
            "sqrt": lambda x: math.sqrt(x[0]),
            "rand": lambda x: random.random()
        }
        for f in built_in_functions.keys():
            context.def_function(f, built_in_functions[f])

        for v in [x for x in node.STATEMENTS if not type(x) is ProtocolNode]:
            self.visit(v, context)
            if type(v) is TypeNode:
                context.def_type(v.NAME, self.last_value_returned)
            if type(v) is FunctionNode:
                context.def_function(v.NAME, self.last_value_returned)
        self.visit(node.EXPRESSION, context)

    @Visitor.when(TypeNode)
    def visit(self, node: TypeNode, context: CodeContext):

        type_context = CodeContext(context)
        visitor = self

        class NewType:
            def __init__(self, parameters):
                constructor_context = CodeContext(context)

                for i in range(len(node.CONSTRUCTOR)):
                    constructor_context.def_variable(node.CONSTRUCTOR[i].NAME, parameters[i])

                args = []
                for arg in node.ARGUMENTS:
                    visitor.visit(arg, constructor_context)
                    args.append(visitor.last_value_returned)

                self.Parent = context.get_type(node.INHERITS)
                if self.Parent!=None:
                    self.Parent=self.Parent(args)
                for x in [x for x in node.CORPUS if type(x) is TypeAtributeNode]:
                    visitor.visit(x.VALUE, constructor_context)
                    type_context.def_variable(x.VAR.NAME, visitor.last_value_returned)

                for x in [x for x in node.CORPUS if type(x) is FunctionNode]:
                    visitor.visit(x, type_context)
                    type_context.def_function(x.NAME, visitor.last_value_returned)

            def call(self, name, parameters):
                if not self.has_function(name):
                    return self.Parent.call(name, parameters)
                override = self.Parent.has_function(name) if self.Parent!=None else False
                if override:
                    type_context.def_function('base', lambda x: self.Parent.call(name, parameters))
                returnValue = type_context.get_function(name, False)(parameters)
                if override:
                    type_context.remove_function('base')
                return returnValue

            def has_function(self, name):
                return type_context.has_function(name, False)

        self.last_value_returned = NewType

    @Visitor.when(FunctionNode)
    def visit(self, node: FunctionNode, context):
        function_context = CodeContext(context)

        def new_function(parameters):
            for i in range(len(node.PARAMETERS)):
                function_context.def_variable(node.PARAMETERS[i].NAME, parameters[i])
            self.visit(node.CORPUS, function_context)
            return self.last_value_returned

        self.last_value_returned = new_function

    @Visitor.when(ExpressionBlockNode)
    def visit(self, node: ExpressionBlockNode, context: CodeContext):
        for e in node.EXPRESSIONS:
            self.visit(e, context)

    @Visitor.when(LetNode)
    def visit(self, node: LetNode, context: CodeContext):
        self.visit(node.VAR_VALUES[0], context)
        child_context = CodeContext(context)
        child_context.def_variable(node.VARS[0].NAME, self.last_value_returned)
        if len(node.VARS) > 1:
            rest = LetNode(node.VARS[1:], node.VAR_VALUES[1:], node.EXPRESSION)
            self.visit(rest, child_context)
        else:
            self.visit(node.EXPRESSION, child_context)

    @Visitor.when(IfElseExpression)
    def visit(self, node: IfElseExpression, context: CodeContext):
        for case in range(len(node.CONDITIONS)):
            self.visit(node.CONDITIONS[case], context)
            if self.last_value_returned:
                self.visit(node.CASES[case], context)
                return
        self.visit(node.CASES[-1], context)

    @Visitor.when(DestructiveExpression)
    def visit(self, node: DestructiveExpression, context: CodeContext):
        self.visit(node.EXPRESSION, context)
        context.edit_variable(node.NAME, self.last_value_returned)

    @Visitor.when(SelfDestructiveExpression)
    def visit(self, node: SelfDestructiveExpression, context: CodeContext):
        self.visit(node.EXPRESSION, context)
        correct_context = context
        while correct_context.parent.parent != None:
            correct_context = correct_context.parent
        correct_context.edit_variable(node.VAR.NAME, self.last_value_returned)

    @Visitor.when(WhileNode)
    def visit(self, node: WhileNode, context: CodeContext):
        self.visit(node.CONDITIONS, context)
        while (self.last_value_returned):
            self.visit(node.EXPRESSION, context)
            returnValue = self.last_value_returned
            self.visit(node.CONDITIONS, context)
        self.last_value_returned = returnValue

    @Visitor.when(ForNode)
    def visit(self, node: ForNode, context: CodeContext):
        self.visit(node.COLLECTION, context)
        collection = self.last_value_returned
        for_context = CodeContext(context)
        for_context.def_variable(node.NAME, None)
        if type(collection) is list:
            for x in collection:
                for_context.edit_variable(node.NAME, x)
                self.visit(node.EXPRESSION, for_context)
        else:
            x=collection.call('current',[])
            while collection.call('next',[]):
                for_context.edit_variable(node.NAME, x)
                self.visit(node.OPERATION, for_context)
                x=collection.call('current',[])

    @Visitor.when(NewNode)
    def visit(self, node: NewNode, context: CodeContext):
        args = []
        for arg in node.ARGS:
            self.visit(arg, context)
            args.append(self.last_value_returned)
        self.last_value_returned = context.get_type(node.NAME)(args)

    @Visitor.when(OrAndExpression)
    def visit(self, node: OrAndExpression, context: CodeContext):
        self.visit(node.LEFT, context)
        left = self.last_value_returned
        self.visit(node.RIGHT, context)
        right = self.last_value_returned

        if node.OPERATION == "&":
            self.last_value_returned = left and right
        elif node.OPERATION == "|":
            self.last_value_returned = left or right
        else:
            raise Exception("Invalid operator")

    @Visitor.when(ComparationExpression)
    def visit(self, node: ComparationExpression, context: CodeContext):
        # modificar. para aquello que sea comparable
        self.visit(node.LEFT, context)
        left = self.last_value_returned
        self.visit(node.RIGHT, context)
        right = self.last_value_returned

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
    def visit(self, node: StringConcatenationNode, context: CodeContext):
        # Modificar, para aquello que sea printable
        self.visit(node.LEFT, context)
        left = self.last_value_returned
        self.visit(node.RIGHT, context)
        right = self.last_value_returned
        if node.DOUBLE:
            self.last_value_returned = str(left) + ' ' + str(right)
        else:
            self.last_value_returned = str(left) + str(right)

    @Visitor.when(ArithmeticExpression)
    def visit(self, node: ArithmeticExpression, context: CodeContext):
        self.visit(node.LEFT, context)
        left = self.last_value_returned
        self.visit(node.RIGHT, context)
        right = self.last_value_returned

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
    def visit(self, node: NumberNode, context: CodeContext):
        self.last_value_returned = node.VALUE

    @Visitor.when(StringNode)
    def visit(self, node: StringNode, context: CodeContext):
        self.last_value_returned = node.VALUE

    @Visitor.when(BooleanNode)
    def visit(self, node: BooleanNode, context: CodeContext):
        self.last_value_returned = node.VALUE

    @Visitor.when(VariableNode)
    def visit(self, node: VariableNode, context: CodeContext):
        self.last_value_returned = context.get_variable(node.NAME)

    @Visitor.when(SelfVariableNode)
    def visit(self, node: SelfVariableNode, context: CodeContext):
        correct_context = context
        while correct_context.parent.parent != None:
            correct_context = correct_context.parent
        self.last_value_returned = correct_context.get_variable(node.NAME)

    @Visitor.when(FunctionCallNode)
    def visit(self, node: FunctionCallNode, context: CodeContext):
        Arguments = []
        for x in node.ARGS:
            self.visit(x, context)
            Arguments.append(self.last_value_returned)
        self.last_value_returned = context.get_function(node.FUNCT)(Arguments)

    @Visitor.when(TypeFunctionCallNode)
    def visit(self, node: TypeFunctionCallNode, context: CodeContext):
        Arguments = []
        for x in node.ARGS:
            self.visit(x, context)
            Arguments.append(self.last_value_returned)
        self.visit(node.CLASS, context)
        if type(self.last_value_returned) is list:
            self.last_value_returned=context.Puppet(self.last_value_returned,node.FUNCT)
            return
        self.last_value_returned = self.last_value_returned.call(node.FUNCT, Arguments)

    @Visitor.when(ListNode)
    def visit(self, node: ListNode, context: CodeContext):
        elements = []
        for x in node.ELEMENTS:
            self.visit(x, context)
            elements.append(self.last_value_returned)
        self.last_value_returned = elements

    @Visitor.when(ImplicitListNode)
    def visit(self, node: ImplicitListNode, context: CodeContext):
        # Editar para iterables
        elements = []
        self.visit(node.COLLECTION, context)
        collection = self.last_value_returned
        List_context = CodeContext(context)
        List_context.def_variable(node.ITERATION, None)
        if type(collection) is list:
            for x in collection:
                List_context.edit_variable(node.ITERATION, x)
                self.visit(node.OPERATION, List_context)
                elements.append(self.last_value_returned)
        else:
            x=collection.call('current',[])
            while collection.call('next',[]):
                List_context.edit_variable(node.ITERATION, x)
                self.visit(node.OPERATION, List_context)
                elements.append(self.last_value_returned)
                x=collection.call('current',[])
                
        self.last_value_returned = elements

    @Visitor.when(IndexingNode)
    def visit(self, node: IndexingNode, context: CodeContext):
        self.visit(node.INDEX, context)
        i = self.last_value_returned
        self.visit(node.COLLECTION, context)
        self.last_value_returned = self.last_value_returned[i]

    @Visitor.when(AsNode)
    def visit(self, node: AsNode, context: CodeContext):
        self.visit(node.EXPRESSION, context)
