import itertools as itl
from src.Common.ASTNodes import *
import src.Common.Visitor as visitor
from src.SemanticChecking.Auxiliars import *
from src.SemanticChecking.Scope import Scope

class SemanticCheckerVisitor(object):
    def __init__(self):
        self.errors = []

    @visitor.on('node')
    def visit(self, node, scope: Scope):
        pass

    # _______________________________________________________________________________________
    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, scope: Scope = None):  # ✔️
        # --------------------------------------------------------------------
        # CHECKING POSSIBLE ERRORS IN PROGRAM NODE ✔️
        # --------------------------------------------------------------------
        # Avoiding repited Types
        if scope is None:
            scope = Scope()

        defaultTypes = ['Object', 'Number', 'Boolean', 'String', 'Vector']
        TypeNames = defaultTypes + [x.NAME for x in node.STATEMENTS if type(x) is TypeNode]
        if EqualObjects(TypeNames):
            self.errors.append('There is two declarations of the same Type')

        # Avoiding repited Protocols
        defaultProtocols = ['Iterable', 'Printable', 'Comparable']
        ProtocolNames = defaultProtocols + [x.NAME for x in node.STATEMENTS if (type(x) is ProtocolNode)]
        if EqualObjects(ProtocolNames):
            self.errors.append('There is two declarations of the same protocol')

        # Avoiding repited Functions
        defaultFunctions = ['print', 'sen', 'cos', 'rand', 'sqrt', 'exp', 'log']
        FuncNames = defaultFunctions + [x.NAME for x in node.STATEMENTS if type(x) is FunctionNode]
        if EqualObjects(FuncNames):
            self.errors.append('There is two declarations of the same function')

        # Avoiding circular inherence
        Inherence = dict([(x.NAME, x.INHERITS) for x in node.STATEMENTS if type(x) is TypeNode])
        Inherence['Object'] = ''
        Inherence['Number'] = 'Object'
        Inherence['Boolean'] = 'Object'
        Inherence['String'] = 'Object'
        Inherence['Vector'] = 'Object'
        TypeOrder, TreeForm = GetTopologicOrder(Inherence)
        if not TreeForm:
            self.errors.append("There is a circular dependence between protocols")

        # Avoiding circular extensions
        Extensions = dict([(x.NAME, x.EXTENDS) for x in node.STATEMENTS if type(x) is ProtocolNode])
        Extensions['Iterable'] = ''
        Extensions['Printable'] = ''
        Extensions['Comparable'] = ''
        _, TreeForm = GetTopologicOrder(Extensions)
        if not TreeForm:
            self.errors.append("There is a circular dependence between protocols")

        # -----------------------------------------------------------------------
        # SAVING EVERY PIECE OF INFORMATION NEEDED IN SCOPE✔️
        # -----------------------------------------------------------------------

        AddBasicInfo(scope)
        scope.AddTypes(TypeNames)
        scope.AddProtocols(ProtocolNames)
        scope.AddProtocolExtensions(Extensions)
        scope.AddTypeHierarchy(Inherence)

        # -----------------------------------------------------------------------
        # VISITING ALL CHILDREN ✔️
        # -----------------------------------------------------------------------
        # visiting the protocols
        for Protocol in [x for x in node.STATEMENTS if type(x) is ProtocolNode]:
            self.visit(Protocol, scope)

        # visiting the classes in topologic order 1st time
        TypeQuickAccess = dict([(x.NAME, x) for x in node.STATEMENTS if type(x) is TypeNode])
        for Type in TypeOrder:
            if Type in defaultTypes:
                continue
            self.visit(TypeQuickAccess[Type], scope)

        # visiting the functions 1st time
        for Function in [x for x in node.STATEMENTS if type(x) is FunctionNode]:
            self.visit(Function, scope)

        # visiting the classes in topologic order 2nd time
        TypeQuickAccess = dict([(x.NAME, x) for x in node.STATEMENTS if type(x) is TypeNode])
        for Type in TypeOrder:
            if Type in defaultTypes:
                continue
            self.visit(TypeQuickAccess[Type], scope)

        # visiting the functions 2nd time
        for Function in [x for x in node.STATEMENTS if type(x) is FunctionNode]:
            self.visit(Function, scope)

        # visiting the expression
        self.visit(node.EXPRESSION, scope)
        # -----------------------------------------------------------------------
        return self.errors

    # _______________________________________________________________________________________

    @visitor.when(ProtocolNode)
    def visit(self, node: ProtocolNode, scope: Scope = None):  # ✔️✔️
        # --------------------------------------------------------------------
        # CHECKING POSSIBLE ERRORS IN PROTOCOL NODE ✔️
        # --------------------------------------------------------------------
        # Cheking that the protocol doesn't extend itself
        if node.EXTENDS == node.NAME:
            self.errors.append(f"The protocol {node.EXTENDS} doesn't exist in the current context")
        # Cheking that the protocol extend something that exist
        if not scope.IsProtocolDefined(node.EXTENDS) and node.EXTENDS != '':
            self.errors.append(f"The protocol {node.EXTENDS} doesn't exist in the current context")
        # Avoiding repited Functions
        FuncNames = [x.NAME for x in node.CORPUS]
        if EqualObjects(FuncNames):
            self.errors.append('There is two declarations of the same function')
        # -----------------------------------------------------------------------
        # SAVING EVERY PIECE OF INFORMATION NEEDED IN SCOPE✔️
        # -----------------------------------------------------------------------
        scope.AddProtocolFunctions(node.NAME, node.CORPUS)
        # -----------------------------------------------------------------------
        # VISITING ALL CHILDREN ✔️
        # -----------------------------------------------------------------------
        [self.visit(x, scope) for x in node.CORPUS]
        # -----------------------------------------------------------------------
        return self.errors

    # _______________________________________________________________________________________

    @visitor.when(ProtocolMethodNode)
    def visit(self, node: ProtocolMethodNode, scope: Scope = None):  # ✔️✔️
        # --------------------------------------------------------------------
        # CHECKING POSSIBLE ERRORS IN PROTOCOL METHOD NODE ✔️
        # --------------------------------------------------------------------
        # Checking function Type
        if not scope.IsTypeDefined(node.TYPE) and not scope.IsProtocolDefined(node.TYPE):
            self.errors.append(f"The Type {node.TYPE} is not defined in this scope")
        # Checking doble parameters
        ParameterNames = [x.NAME for x in node.PARAMETERS]
        if EqualObjects(ParameterNames):
            self.errors.append(f"A method can't have 2 parameters with the same name")
        # --------------------------------------------------------------------
        # VISITING ALL CHILDREN ✔️
        # --------------------------------------------------------------------
        [self.visit(x, scope) for x in node.PARAMETERS]
        # --------------------------------------------------------------------
        return self.errors

    @visitor.when(ParameterNode)
    def visit(self, node: ParameterNode, scope: Scope = None):  # ✔️✔️
        # --------------------------------------------------------------------
        # CHECKING POSSIBLE ERRORS IN PARAMETER NODE ✔️
        # --------------------------------------------------------------------
        # Checking parameter Type
        if not scope.IsTypeDefined(node.TYPE) and not scope.IsProtocolDefined(node.TYPE):
            self.errors.append(f"The Type {node.TYPE} is not defined in this scope")
            # --------------------------------------------------------------------
        return self.errors

    # _______________________________________________________________________________________

    @visitor.when(TypeNode)
    def visit(self, node: TypeNode, scope: Scope = None):  # ✔️

        firstVisit = not scope.TypeVisited(node.NAME)
        # --------------------------------------------------------------------
        # CHECKING POSSIBLE ERRORS IN TYPE NODE ✔️
        # --------------------------------------------------------------------
        if firstVisit:
            # Avoiding self inherence
            if node.INHERITS == node.NAME:
                self.errors.append(f"The protocol {node.INHERITS} doesn't exist in the current context")
            # Cheking that the type inherits exist
            if not scope.IsTypeDefined(node.INHERITS) and not scope.IsProtocolDefined(node.INHERITS):
                self.errors.append(f"The type {node.INHERITS} doesn't exist in the current context")
                # Avoid inherints from basic types
            for x in ['Number', 'Boolean', 'String', 'Vector']:
                if x == node.INHERITS:
                    self.errors.append(f"The type {x} cannot have any descendents")
                    # Avoiding duplicated constructor parameters
            ParameterNames = [x.NAME for x in node.CONSTRUCTOR]
            if EqualObjects(ParameterNames):
                self.errors.append(f"A method can't have 2 parameters with the same name")
            # Avoiding duplicated Atributes
            AtributeNames = [x.VAR.NAME for x in node.CORPUS if type(x) is TypeAtributeNode]
            if EqualObjects(AtributeNames):
                self.errors.append(f"A type can't have 2 atributes with the same name")
            # Avoiding duplicated functions
            AtributeNames = [x.NAME for x in node.CORPUS if type(x) is FunctionNode]
            if EqualObjects(AtributeNames):
                self.errors.append(f"A type can't have 2 functions with the same name")

        else:
            # checking that the inherit parameters amount match with the Arguments number
            parentParameters = scope.SearchTypeParameters(node.INHERITS)
            if len(parentParameters) != len(node.ARGUMENTS):
                self.errors.append(f"Expected {len(parentParameters)} arguments instead of {len(node.ARGUMENTS)}")
            # Checking that the argument match with the parameters
            for i in range(len(parentParameters)):
                self.visit(node.ARGUMENTS[i])
                if not scope.AreRelated(node.ARGUMENTS[i].VALUE_TYPE, parentParameters[i].TYPE):
                    self.errors.append(
                        f"{parentParameters[i].TYPE} expression was expected instead of {node.ARGUMENTS[i].VALUE_TYPE}")
        # --------------------------------------------------------------------
        # SAVING EVERY PIECE OF INFORMATION NEEDED IN SCOPE✔️
        # --------------------------------------------------------------------
        if firstVisit:
            # Scope for parameters and self atribute
            scope.AddTypeParameters(node.NAME,node.CONSTRUCTOR)
            new_scope = scope.CreateChild(node.NAME)
            [new_scope.AddVariable(x.NAME, x.TYPE) for x in node.CONSTRUCTOR]
            new_scope.ON_TYPE = True  # for self.Something
            scope.AddTypeFunctions(node.NAME, [x for x in node.CORPUS
                                               if type(x) is FunctionNode])
        # -----------------------------------------------------------------------
        # VISITING ALL CHILDREN ✔️
        # --------------------------------------------------------------------
        # CONSTRUCTOR PARAMETERS
        [self.visit(x, scope) for x in node.CONSTRUCTOR]

        # CLASS ATTRIBUTES(only on second visit)
        if not firstVisit:
            # here, the functions from the type must be hide
            scope.AddTypeFunctions(node.NAME, [])
            # Creates a new scope with the attributes, self and base method
            special_scope = scope.GetChild(node.NAME)
            [self.visit(x, special_scope) for x in node.CORPUS if type(x) is TypeAtributeNode]
            # Unlocking the functions
            scope.AddTypeFunctions(node.NAME, [x for x in node.CORPUS if type(x) is FunctionNode])
            # Unlocking the variables
            special_scope.UnlockVariables()

        # TYPE FUNCTIONS
        if firstVisit:
            special_scope = scope.GetChild(node.NAME)
            [self.visit(x, special_scope) for x in node.CORPUS if type(x) is FunctionNode]
        else:
            special_scope.AddVariable('self', node.NAME)
            special_scope.SELF_ACTIVE = True
            for function in [x for x in node.CORPUS if type(x) is FunctionNode]:
                parent_method = scope.SearhFunction(function.NAME, scope.TYPE_HIERARCHY[node.NAME])
                if parent_method != None:
                    special_scope.AddFunctions(ProtocolMethodNode('base', parent_method.PARAMETERS, parent_method.TYPE))
                    self.visit(x, special_scope)
                    special_scope.RemoveFunction('base')
        # --------------------------------------------------------------------
        return self.errors

    @visitor.when(TypeAtributeNode)
    def visit(self, node: TypeAtributeNode, scope: Scope = None):  # ✔️
        # Define the variable on first visit
        self.visit(node.VAR, scope)
        self.visit(node.VALUE, scope)
        if not scope.AreRelated(node.VALUE.VALUE_TYPE, node.VAR.TYPE):
            self.errors.append(f'{node.VAR.TYPE} expression was expected instead of {node.VALUE.VALUE_TYPE}')
        # The extra space is to lock the variable. To make it impossible to reference them
        scope.AddVariable(' self.' + node.VAR.NAME, node.VALUE.VALUE_TYPE)
        return self.errors

    # _______________________________________________________________________________________

    @visitor.when(FunctionNode)
    def visit(self, node: FunctionNode, scope: Scope = None):  # ✔️
        # --------------------------------------------------------------------
        # CHECKING POSSIBLE ERRORS IN FUNCTION NODE ON FIRST VISIT✔️
        # --------------------------------------------------------------------
        if not scope.FunctionVisited(node.NAME):
            # Checking function Type
            if not scope.IsTypeDefined(node.TYPE) and not scope.IsProtocolDefined(node.TYPE):
                self.errors.append(f"The Type {node.TYPE} is not defined in this scope")
            # Checking doble parameters
            ParameterNames = [x.NAME for x in node.PARAMETERS]
            if EqualObjects(ParameterNames):
                self.errors.append(f"A method can't have 2 parameters with the same name")
            # --------------------------------------------------------------------
            # VISITING THE CHILDREN ✔️
            # --------------------------------------------------------------------
            [self.visit(x, scope) for x in node.PARAMETERS]
            # --------------------------------------------------------------------
            # SAVING EVERY PIECE OF INFORMATION NEEDED IN SCOPE 1ST VISIT✔️
            # --------------------------------------------------------------------
            scope.AddFunctions(ProtocolMethodNode(node.NAME, node.PARAMETERS, node.TYPE))
        # --------------------------------------------------------------------
        # VISIT THE EXPRESSION ✔️
        # --------------------------------------------------------------------
        else:
            # Creating the scope for parameters
            new_scope = scope.CreateChild(node.NAME + ' ')
            [new_scope.AddVariable(x.NAME, x.TYPE) for x in node.PARAMETERS]
            # visiting the corpus
            self.visit(node.CORPUS, new_scope)
            # --------------------------------------------------------------------
            # CHECKING POSSIBLE ERRORS IN FUNCTION NODE ON SECOND VISIT ✔️
            # --------------------------------------------------------------------
            node.CORPUS.VALUE_TYPE = node.CORPUS.VALUE_TYPE
            if not scope.AreRelated(node.CORPUS.VALUE_TYPE, node.TYPE):
                self.errors.append(f"{node.TYPE} expression was expected instead of {node.CORPUS.VALUE_TYPE}")
        # --------------------------------------------------------------------
        return self.errors

    # _______________________________________________________________________________________
    # _______________________________________________________________________________________
    # _______________________________________________________________________________________

    @visitor.when(ExpressionBlockNode)
    def visit(self, node: ExpressionBlockNode, scope: Scope = None):  # ✔️✔️
        for Expression in node.EXPRESSIONS:
            self.visit(Expression, scope)
        node.VALUE_TYPE = node.EXPRESSIONS[-1].VALUE_TYPE
        return self.errors

    # _______________________________________________________________________________________
    # _______________________________________________________________________________________
    # _______________________________________________________________________________________

    # ---------------------------------------------------------------------------------------
    # DEFINING VARIABLES
    # ---------------------------------------------------------------------------------------

    @visitor.when(LetNode)
    # DEFINING VARIABLE
    def visit(self, node: LetNode, scope: Scope = None):  # ✔️✔️
        # Checking the assigned expression
        self.visit(node.VAR_VALUES[0], scope)
        ValueType = node.VAR_VALUES[0].VALUE_TYPE
        # Checking the parameter
        self.visit(node.VARS[0], scope)
        # Checking compatibility
        if not scope.AreRelated(ValueType, node.VARS[0].TYPE):
            self.errors.append(f'The expresion return {ValueType}, but {node.VARS[0].TYPE} was expected')
        # Creating a new scope for let expression
        new_scope = scope.CreateChild('let expression')
        new_scope.AddVariable(node.VARS[0].NAME, ValueType)
        # Nesting the rest of the let expression
        if len(node.VAR_VALUES) > 1:
            Simplest_node = LetNode(node.VARS[1:], node.VAR_VALUES[1:], node.EXPRESSION)
            # Visiting the expression
            self.visit(Simplest_node, new_scope)
        else:
            self.visit(node.EXPRESSION, new_scope)
        node.VALUE_TYPE = node.EXPRESSION.VALUE_TYPE
        return self.errors

    @visitor.when(DestructiveExpression)
    # REPLACES A VALUE
    def visit(self, node: DestructiveExpression, scope: Scope = None):  # ✔️
        if not scope.IsVariableDefined(node.NAME):
            self.errors.append(f"{node.NAME} doesn't exist in the current context")
        # Case self:=....
        if node.NAME == 'self' and scope.SELF_ACTIVE:
            self.errors.append(f"{node.NAME} can't be destroyed")
        self.visit(node.EXPRESSION, scope)
        node.VALUE_TYPE = node.EXPRESSION.VALUE_TYPE
        return self.errors

    @visitor.when(SelfDestructiveExpression)
    # REPLACES A VALUE FOR A TYPE ATTRIBUTE
    def visit(self, node: SelfDestructiveExpression, scope: Scope = None):  # ✔️✔️
        self.visit(node.VAR, scope)
        self.visit(node.EXPRESSION, scope)
        if not scope.AreRelated(node.VAR.VALUE_TYPE, node.EXPRESSION):
            self.errors.append(f"You cannot change the variable type")
        node.VALUE_TYPE = node.EXPRESSION.VALUE_TYPE
        return self.errors

    @visitor.when(NewNode)
    # CREATES A NEW OBJECT WITH THE SPECIFIED ATRIBUTES
    def visit(self, node: NewNode, scope: Scope = None):  # ✔️✔️
        # Checking the type
        if not scope.IsTypeDefined(node.NAME):
            self.errors.append(f"The {node.NAME} type doesn't exist in the current context")
            node.VALUE_TYPE = 'Object'
            return self.errors
        # Getting the constructors
        Constructor = scope.SearchTypeParameters(node.NAME)
        if len(Constructor) != len(node.ARGS):
            self.errors.append(f"Expected {len(Constructor)} arguments instead of {len(node.ARGS)}")
        # Visiting the arguments
        for i in range(len(Constructor)):
            self.visit(node.ARGS[i])
            try:
                if not scope.AreRelated(node.ARGS[i].VALUE_TYPE, Constructor[i].TYPE):
                    self.errors.append(f"{Constructor[i].TYPE} expression was expected instead of {node.ARGS[i].VALUE_TYPE}")
            except:
                continue
        node.VALUE_TYPE = node.NAME
        return self.errors

    # _______________________________________________________________________________________
    # ---------------------------------------------------------------------------------------
    # CONDITIONALS AND CYCLES
    # ---------------------------------------------------------------------------------------

    @visitor.when(IfElseExpression)
    # CONDITIONALS
    def visit(self, node: IfElseExpression, scope: Scope = None):  # ✔️✔️
        # First check if the conditions are bool
        for i in range(len(node.CONDITIONS)):
            self.visit(node.CONDITIONS[i], scope)
            if node.CONDITIONS[i].VALUE_TYPE not in ['Boolean', 'Object']:
                self.errors.append(f'Boolean expression was expected instead of {node.CONDITIONS[i].VALUE_TYPE}')
        # Getting all possible values
        PossibleValueReturns = []
        for i in range(len(node.CASES)):
            self.visit(node.CASES[i], scope)
            PossibleValueReturns.append(node.CASES[i].VALUE_TYPE)
        # The type is the last common ancestor
        node.VALUE_TYPE = scope.LastCommonAncestor(PossibleValueReturns)
        return self.errors

    @visitor.when(WhileNode)
    # WHILE CYCLE
    def visit(self, node: WhileNode, scope: Scope = None):  # ✔️✔️
        # Check if the condition is bool
        self.visit(node.CONDITIONS, scope)
        if node.CONDITIONS.VALUE_TYPE not in ['Boolean', 'Object']:
            self.errors.append(f'Boolean expression was expected')
        # Visiting the expression
        self.visit(node.EXPRESSION, scope)
        node.VALUE_TYPE = node.EXPRESSION.VALUE_TYPE
        return self.errors

    @visitor.when(ForNode)
    # FOR CYCLE
    def visit(self, node: ForNode, scope: Scope = None):  # ✔️
        # First check if the condition is bool
        self.visit(node.COLLECTION, scope)
        if scope.AreRelated(node.COLLECTION.VALUE_TYPE, 'Iterable'):
            self.errors.append(f'Collection was expected')
        # Defining the variable
        new_scope = scope.CreateChild('for expression')
        new_scope.AddVariable(node.NAME, 'Object')
        # Visiting the expression
        self.visit(node.EXPRESSION, new_scope)
        node.VALUE_TYPE = node.EXPRESSION.VALUE_TYPE
        return self.errors

    # _______________________________________________________________________________________

    # ---------------------------------------------------------------------------------------
    # OPERATIONS
    # ---------------------------------------------------------------------------------------

    @visitor.when(OrAndExpression)
    # BOOLEAN OPERATIONS BETWEEN BOOLEANS
    def visit(self, node: OrAndExpression, scope: Scope = None):  # ✔️✔️
        # Checking the left
        self.visit(node.LEFT, scope)
        if node.VALUE_TYPE not in ['Boolean', 'Object']:
            self.errors.append(f'Boolean expression was expected')
        # Checking the right
        self.visit(node.RIGHT, scope)
        if node.VALUE_TYPE not in ['Boolean', 'Object']:
            self.errors.append(f'Boolean expression was expected')
        node.VALUE_TYPE = 'Boolean'
        return self.errors

    @visitor.when(NotExpression)
    # BOOLEAN OPERATION TO BOOLEAN
    def visit(self, node: NotExpression, scope: Scope = None):  # ✔️✔️
        self.visit(node.EXPRESSION, scope)
        if node.VALUE_TYPE not in ['Boolean', 'Object']:
            self.errors.append(f'Boolean expression was expected')
        node.VALUE_TYPE = 'Boolean'
        return self.errors

    @visitor.when(ComparationExpression)
    # BOOLEAN OPERATION BETWEEN COMPARABLES
    def visit(self, node: ComparationExpression, scope: Scope = None):  # ✔️✔️
        # Checking the left
        self.visit(node.LEFT, scope)
        if not scope.AreRelated(node.LEFT.VALUE_TYPE, 'Comparable'):
            self.errors.append(f'{node.LEFT.VALUE_TYPE} type is not Comparable')
        # Checking the right
        self.visit(node.RIGHT, scope)
        if not scope.AreRelated(node.LEFT.VALUE_TYPE, 'Comparable'):
            self.errors.append(f'{node.LEFT.VALUE_TYPE} type is not Comparable')
        node.VALUE_TYPE = 'Boolean'
        return self.errors

    @visitor.when(ArithmeticExpression)
    # ARITMETHIC OPERATION BETWEEN NUMBERS
    def visit(self, node: ArithmeticExpression, scope: Scope = None):  # ✔️✔️
        # Checking the left
        self.visit(node.LEFT, scope)
        if node.LEFT.VALUE_TYPE not in ['Number', 'Object']:
            self.errors.append(f'Number expression was expected instead of {node.LEFT.VALUE_TYPE}')
        # Checking the right
        self.visit(node.RIGHT, scope)
        if node.RIGHT.VALUE_TYPE not in ['Number', 'Object']:
            self.errors.append(f'Number expression was expected instead of {node.RIGHT.VALUE_TYPE}')
        node.VALUE_TYPE = 'Number'
        return self.errors

    @visitor.when(StringConcatenationNode)
    # CONCATENATION OF PRINTABLES
    def visit(self, node: StringConcatenationNode, scope: Scope = None):  # ✔️✔️
        # Checking the left
        self.visit(node.LEFT, scope)
        if not scope.AreRelated(node.LEFT.VALUE_TYPE, 'Printable'):
            self.errors.append(f'{node.LEFT.VALUE_TYPE} type is not Printable')
        # Checking the right
        self.visit(node.RIGHT, scope)
        if not scope.AreRelated(node.RIGHT.VALUE_TYPE, 'Printable'):
            self.errors.append(f'{node.RIGHT.VALUE_TYPE} type is not Printable')
        node.VALUE_TYPE = 'String'
        return self.errors

    @visitor.when(IsExpression)
    def visit(self, node: IsExpression, scope: Scope = None):  # ✔️✔️
        self.visit(node.LEFT, scope)
        if scope.IsTypeDefined(node.NAME):
            self.errors.append(f"The {node.NAME} type doesn't exist in the current context")
        node.VALUE_TYPE = 'Boolean'
        return self.errors

    # _____________________________________________________________________________________________________________________________
    # -------------------------------------------------------------------------------------------------------------------
    # TYPE NODES
    # -------------------------------------------------------------------------------------------------------------------

    @visitor.when(NumberNode)  # NUMBER
    def visit(self, node, scope: Scope = None):  # ✔️✔️
        node.VALUE_TYPE = 'Number'
        return self.errors

    @visitor.when(BooleanNode)  # BOOLEAN
    def visit(self, node, scope: Scope = None):  # ✔️✔️
        node.VALUE_TYPE = 'Boolean'
        return self.errors

    @visitor.when(StringNode)  # STRING
    def visit(self, node, scope: Scope = None):  # ✔️✔️
        node.VALUE_TYPE = 'String'
        return self.errors

    @visitor.when(VariableNode)
    def visit(self, node: VariableNode, scope: Scope = None):  # ✔️✔️
        # Check if it is defined
        if not scope.IsVariableDefined(node.NAME):
            self.errors.append(f"{node.NAME} doesn't exist in the current context")
        node.VALUE_TYPE = scope.VariableType(node.NAME)
        return self.errors

    @visitor.when(AsNode)
    def visit(self, node: AsNode, scope: Scope = None):  # ✔️✔️
        # Casting operation
        # Checking if the type exist
        if not scope.IsTypeDefined(node.TYPE):
            self.errors.append(f"{node.TYPE} type doesn't exist in the current context")
        # Checking if it is possible
        self.visit(node.EXPRESSION, scope)
        if not scope.AreRelated(node.TYPE, node.EXPRESSION.VALUE_TYPE):
            self.errors.append(f"The type of the expression doesn't match correctly")
        node.VALUE_TYPE = node.TYPE
        return self.errors

    # ______________________________________________________________________________
    # ------------------------------------------------------------------------------
    # FUNCTION CALLS AND CLASS PROPERTY CALLS
    # ------------------------------------------------------------------------------

    @visitor.when(FunctionCallNode)
    def visit(self, node: FunctionCallNode, scope: Scope = None):  # ✔️✔️
        # Searching the function
        function = scope.SearhFunction(node.FUNCT)
        if function == None:
            self.errors.append(f"The {node.FUNCT} function doesn't exist in the current context")
            node.VALUE_TYPE = 'Object'
            for arg in node.ARGS:
                self.visit(arg, scope)
            return self.errors
        # Checking compatibility in number of arguments
        if len(function.PARAMETERS) != len(node.ARGS):
            self.errors.append(f"Expected {len(function.PARAMETERS)} arguments instead of {len(node.ARGS)}")
        for i in range(min(len(function.PARAMETERS), len(node.ARGS))):
            # Visit the arguments
            self.visit(node.ARGS[i], scope)
            # Checking compatibility between arguments and paramaters
            if not scope.AreRelated(node.ARGS[i].VALUE_TYPE, function.PARAMETERS[i].TYPE):
                self.errors.append(f"{function.PARAMETERS[i].TYPE} expression was expected instead of {node.ARGS[i].VALUE_TYPE}")
        node.VALUE_TYPE = function.TYPE
        return self.errors

    @visitor.when(TypeFunctionCallNode)
    def visit(self, node: TypeFunctionCallNode, scope: Scope = None):  # ✔️✔️
        # visiting the class
        self.visit(node.CLASS, scope)
        # Checking if is possible that the method belongs to the type
        function = scope.SearhFunction(node.FUNCT, node.CLASS.VALUE_TYPE)
        if function == None:
            self.errors.append(f"The {node.FUNCT} function doesn't exist in the current context")
            node.VALUE_TYPE = 'Object'
        # Checking if the call is compatible
        elif len(function.PARAMETERS) != len(node.ARGS):
            self.errors.append(f"Expected {len(function.PARAMETERS)} arguments instead of {len(node.ARGS)}")
            for i in range(min(len(function.PARAMETERS), len(node.ARGS))):
                self.visit(node.ARGS[i])
                if not scope.AreRelated(node.ARGS[i].VALUE_TYPE, function.PARAMETERS[i].TYPE):
                    self.errors.append(
                        f"Expected type {function.PARAMETERS[i].TYPE} instead of {node.ARGS[i].VALUE_TYPE}")
            node.VALUE_TYPE = function.TYPE
        return self.errors

    @visitor.when(SelfVariableNode)
    # THIS NODE IS ONLY FOR THE CASE self.ATRIBUTE
    def visit(self, node: SelfVariableNode, scope: Scope = None):  # ✔️✔️
        if not node.IS_SELF:
            self.errors.append(f'{node.NAME} is not defined in the current context')
            node.VALUE_TYPE = 'Object'
        if not scope.IsVariableDefined('self.' + node.NAME):
            self.errors.append(f'{node.NAME} is not defined in the current context')
            node.VALUE_TYPE = 'Object'
        else:
            node.VALUE_TYPE = scope.VariableType('self.' + node.NAME)
        return self.errors

    # ______________________________________________________________________________
    # ------------------------------------------------------------------------------
    # VECTORS. EXPLICIT, IMPLICIT AND INDEXING
    # ------------------------------------------------------------------------------

    @visitor.when(ListNode)
    def visit(self, node: ListNode, scope: Scope = None):  # ✔️✔️
        for element in node.ELEMENTS:
            self.visit(element, scope)
        node.VALUE_TYPE = 'Vector'
        return self.errors

    @visitor.when(ImplicitListNode)
    def visit(self, node: ImplicitListNode, scope: Scope = None):  # ✔️✔️
        # This must be a collection
        self.visit(node.COLLECTION, scope)
        if node.COLLECTION.VALUE_TYPE != 'Object' and not scope.AreRelated(node.COLLECTION.VALUE_TYPE, 'Iterable'):
            self.errors.append(f"{node.COLLECTION.VALUE_TYPE} object is not a iterable")
        # Defining the iterator
        new_scope = scope.CreateChild('Implicit List')
        new_scope.AddVariable(node.ITERATION, 'Object')
        # Checking the operation
        self.visit(node.OPERATION, new_scope)
        # Returning vector. This could be editable to know the type of the vector
        node.VALUE_TYPE = 'Vector'
        return self.errors

    @visitor.when(IndexingNode)
    def visit(self, node: IndexingNode, scope: Scope = None):  # ✔️✔️
        self.visit(node.COLLECTION, scope)
        # The left has to be a collection
        if not scope.AreRelated('Iterable', node.COLLECTION.VALUE_TYPE):
            self.errors.append(f"{node.COLLECTION.VALUE_TYPE} object is not a iterable")
        # The right has to be a number
        self.visit(node.INDEX, scope)
        if not scope.AreRelated('Number', node.INDEX.VALUE_TYPE):
            self.errors.append(f"{node.INDEX.VALUE_TYPE} object is not a number")
        # This sould return the type of the collection
        node.VALUE_TYPE = 'Object'
        return self.errors
