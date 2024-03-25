import itertools as itl
from Common.ASTNodes import *
import Common.Visitor as visitor
from SemanticChecking.Auxiliars import *
from SemanticChecking.Scope import Scope


class SemanticCheckerVisitor(object):
    def __init__(self):
        self.errors = []

    @visitor.on('node')
    def visit(self, node, scope:Scope):
        pass
    
#_______________________________________________________________________________________
    @visitor.when(ProgramNode)
    def visit(self, node:ProgramNode, scope:Scope=None):#✔️
        #--------------------------------------------------------------------
            # CHECKING POSSIBLE ERRORS IN PROGRAM NODE ✔️
        #--------------------------------------------------------------------
        #Avoiding repited Types
        defaultTypes = ['Object','Number','Boolean','String','Vector']
        TypeNames= defaultTypes + [x.NAME for x in node.STATEMENTS if type(x) is TypeNode]
        if EqualObjects(TypeNames):
            self.errors.append('There is two declarations of the same Type')
        
        #Avoiding repited Protocols
        defaultProtocols=['Iterable','Printable','Comparable']
        ProtocolNames= defaultProtocols+[x.NAME for x in node.STATEMENTS if (type(x) is ProtocolNode)]
        if EqualObjects(ProtocolNames):
            self.errors.append('There is two declarations of the same protocol')
        
        #Avoiding repited Functions
        defaultFunctions=['print','sen','cos','rand','sqrt','exp','log']
        FuncNames= defaultFunctions + [x.NAME for x in node.STATEMENTS if type(x) is FunctionNode]
        if EqualObjects(FuncNames):
            self.errors.append('There is two declarations of the same function')
        
        #Avoiding circular inherence
        Inherence=dict([(x.NAME,x.INHERITS) for x in node.STATEMENTS if type(x) is TypeNode])
        Inherence['Object']=''
        Inherence['Number']='Object'
        Inherence['Boolean']='Object'
        Inherence['String']='Object'
        Inherence['Vector']='Object'
        TypeOrder, TreeForm=GetTopologicOrder(Inherence)
        if not TreeForm:
            self.errors.append("There is a circular dependence between protocols")
        
        #Avoiding circular extensions
        Extensions=dict([(x.NAME,x.EXTENDS) for x in node.STATEMENTS if type(x) is ProtocolNode])
        Extensions['Iterable']=''
        Extensions['Printable']=''
        Extensions['Comparable']=''
        _, TreeForm=GetTopologicOrder(Extensions)
        if not TreeForm:
            self.errors.append("There is a circular dependence between protocols")
        
        #-----------------------------------------------------------------------
            #SAVING EVERY PIECE OF INFORMATION NEEDED IN SCOPE✔️
        #-----------------------------------------------------------------------
        
        AddBasicInfo(scope)
        scope.AddTypes(TypeNames)
        scope.AddProtocols(ProtocolNames)
        scope.AddProtocolExtensions(Extensions)
        scope.AddTypeHierarchy(Inherence)
        
        #-----------------------------------------------------------------------
            #VISITING ALL CHILDREN ✔️
        #-----------------------------------------------------------------------
        #visiting the protocols
        for Protocol in [x for x in node.STATEMENTS if type(x) is ProtocolNode]:
            self.visit(Protocol,scope)
        
        #visiting the classes in topologic order 1st time
        TypeQuickAccess=dict([(x.NAME,x) for x in node.STATEMENTS if type(x) is TypeNode])
        for Type in TypeOrder:
            if Type in defaultTypes:
                continue
            self.visit(TypeQuickAccess[Type],scope)

        #visiting the functions 1st time
        for Function in [x for x in node.STATEMENTS if type(x) is FunctionNode]:
            self.visit(Function,scope)
        
        #visiting the classes in topologic order 2nd time
        TypeQuickAccess=dict([(x.NAME,x.INHERITS) for x in node.STATEMENTS if type(x) is TypeNode])
        for Type in TypeOrder:
            if Type in defaultTypes:
                continue
            self.visit(TypeQuickAccess[Type],scope)
        
        #visiting the functions 2nd time
        for Function in [x for x in node.STATEMENTS if type(x) is FunctionNode]:
            self.visit(Function,scope)

        #visiting the expression        
        self.visit(node.EXPRESSION,scope)
        #-----------------------------------------------------------------------
        return self.errors
#_______________________________________________________________________________________        
    
    @visitor.when(ProtocolNode)
    def visit(self, node:ProtocolNode, scope:Scope=None):#✔️✔️
        #--------------------------------------------------------------------
            # CHECKING POSSIBLE ERRORS IN PROTOCOL NODE ✔️
        #--------------------------------------------------------------------
        #Cheking that the protocol doesn't extend itself
        if node.EXTENDS == node.NAME:
            self.errors.append(f"The protocol {node.EXTENDS} doesn't exist in the current context")
        #Cheking that the protocol extend something that exist
        if not scope.IsProtocolDefined(node.EXTENDS) and node.EXTENDS!='':
            self.errors.append(f"The protocol {node.EXTENDS} doesn't exist in the current context")
        #Avoiding repited Functions
        FuncNames= [x.NAME for x in node.CORPUS]
        if EqualObjects(FuncNames):
            self.errors.append('There is two declarations of the same function')
        #-----------------------------------------------------------------------
            #SAVING EVERY PIECE OF INFORMATION NEEDED IN SCOPE✔️
        #-----------------------------------------------------------------------
        scope.AddProtocolFunctions(node.NAME,node.CORPUS)
        #-----------------------------------------------------------------------
            #VISITING ALL CHILDREN ✔️
        #-----------------------------------------------------------------------
        [self.visit(x,scope) for x in node.CORPUS]
        #-----------------------------------------------------------------------
        return self.errors
#_______________________________________________________________________________________        
    
    @visitor.when(ProtocolMethodNode)
    def visit(self, node:ProtocolMethodNode, scope:Scope=None): #✔️✔️
        #--------------------------------------------------------------------
            # CHECKING POSSIBLE ERRORS IN PROTOCOL METHOD NODE ✔️
        #--------------------------------------------------------------------
        #Checking function Type
        if not scope.IsTypeDefined(node.TYPE) and not scope.IsProtocolDefined(node.TYPE):
            self.errors.append(f"The Type {node.TYPE} is not defined in this scope")
        #Checking doble parameters
        ParameterNames=[x.NAME for x in node.PARAMETERS]
        if EqualObjects(ParameterNames):
            self.errors.append(f"A method can't have 2 parameters with the same name")
        #--------------------------------------------------------------------
            #VISITING ALL CHILDREN ✔️
        #--------------------------------------------------------------------
        [self.visit(x,scope) for x in node.PARAMETERS]
        #--------------------------------------------------------------------
        return self.errors

    @visitor.when(ParameterNode)
    def visit(self, node:ParameterNode, scope:Scope=None): # ✔️✔️
        #--------------------------------------------------------------------
        # CHECKING POSSIBLE ERRORS IN PARAMETER NODE ✔️
        #--------------------------------------------------------------------
         #Checking parameter Type
        if not scope.IsTypeDefined(node.TYPE) and not scope.IsProtocolDefined(node.TYPE):
            self.errors.append(f"The Type {node.TYPE} is not defined in this scope")        
        #--------------------------------------------------------------------
        return self.errors
#_______________________________________________________________________________________        

    @visitor.when(TypeNode)
    def visit(self, node:TypeNode, scope:Scope=None): #✔️
        
        firstVisit=scope.AlreadyVisitedType(node.NAME)
        #--------------------------------------------------------------------
            # CHECKING POSSIBLE ERRORS IN TYPE NODE ✔️
        #--------------------------------------------------------------------
        if firstVisit:
            # Avoiding self inherence
            if node.INHERITS == node.NAME:
                self.errors.append(f"The protocol {node.INHERITS} doesn't exist in the current context")
            #Cheking that the type inherits exist
            if not scope.IsTypeDefined(node.INHERITS) and not scope.IsProtocolDefined(node.INHERITS):
                self.errors.append(f"The type {node.INHERITS} doesn't exist in the current context")            
            #Avoiding duplicated constructor parameters
            ParameterNames=[x.NAME for x in node.CONSTRUCTOR]
            if EqualObjects(ParameterNames):
                self.errors.append(f"A method can't have 2 parameters with the same name")
            #Avoiding duplicated Atributes
            AtributeNames=[x.NAME for x in node.CORPUS if type(x) is TypeAtributeNode]
            if EqualObjects(AtributeNames):
                self.errors.append(f"A type can't have 2 atributes with the same name")
            #Avoiding duplicated functions
            AtributeNames=[x for x in node.CORPUS if type(x) is FunctionNode]
            if EqualObjects(AtributeNames):
                self.errors.append(f"A type can't have 2 functions with the same name and the same amount of parameters")
            #checking that the inherit parameters amount match with the Arguments number
            parentParameters=scope.SearchTypeParameters(node.INHERITS)
            if len(parentParameters)!=len(node.ARGUMENTS):
                self.errors.append(f"Expected {len(parentParameters)} arguments instead of {len(node.ARGUMENTS)}")
        
        else:
            #Checking that the argument match with the parameters
            parentParameters=scope.SearchTypeParameters(node.INHERITS)
            for i in len(parentParameters):
                self.visit(node.ARGUMENTS[i])
                if not scope.AreRelated(node.ARGUMENTS[i].VALUE_TYPE,parentParameters[i].TYPE):
                    self.errors.append(f"Expected type {parentParameters[i].TYPE} instead of {node.ARGUMENTS[i].VALUE_TYPE}")
        #--------------------------------------------------------------------
            #SAVING EVERY PIECE OF INFORMATION NEEDED IN SCOPE✔️
        #--------------------------------------------------------------------
        if firstVisit:
            #Scope for parameters and self atribute
            new_scope=scope.CreateChild(node.NAME)
            map(lambda x:new_scope.AddVariable(x.NAME,x.TYPE),node.CONSTRUCTOR)
            if not 'self' in [x.NAME for x in node.CONSTRUCTOR]:
                #scope for atributes and functions
                new_scope.AddVariable('self',node.NAME)
            new_scope=new_scope.CreateChild('self')
            new_scope.ON_TYPE=True #for self.Something
            scope.AddTypeFunctions(node.NAME,[ProtocolMethodNode(x.NAME,x.PARAMETERS,x.TYPE) for x in node.CORPUS if type(x) is FunctionNode])
        #-----------------------------------------------------------------------
            #VISITING ALL CHILDREN ✔️
        #--------------------------------------------------------------------
        #Visiting the parameters
        [self.visit(x,scope) for x in node.CONSTRUCTOR]
        #Visiting the atributes
        [self.visit(x,scope.GetChild(node.NAME).GetChild('self')) 
                    for x in node.CORPUS if type(x) is TypeAtributeNode]
        #Visiting the functions
        [self.visit(x,scope.GetChild(node.NAME).GetChild('self')) 
                    for x in node.CORPUS if type(x) is FunctionNode]
        #--------------------------------------------------------------------    
        return self.errors

    @visitor.when(TypeAtributeNode)
    def visit(self, node:TypeAtributeNode, scope:Scope=None):#✔️     
         #Define the variable on first visit
        if scope.IsVariableDefined(node.NAME):
            scope.AddVariable(node.NAME,'Object')
        #Explore the value on second visit
        else:
            scope.RemoveVariable(node.NAME,'Object')
            self.visit(node.VALUE,scope)
            scope.UpdateVariableValue(node.NAME,node.VALUE.VALUE_TYPE)
        return self.errors
#_______________________________________________________________________________________  
    
    @visitor.when(FunctionNode)
    def visit(self, node:FunctionNode, scope:Scope=None): #✔️   
        #--------------------------------------------------------------------
            # CHECKING POSSIBLE ERRORS IN FUNCTION NODE ON FIRST VISIT✔️
        #--------------------------------------------------------------------
        if not scope.FunctionVisited(node.NAME):
            #Checking function Type
            if not scope.IsTypeDefined(node.TYPE) and not scope.IsProtocolDefined(node.TYPE):
                self.errors.append(f"The Type {node.TYPE} is not defined in this scope")
            #Checking doble parameters
            ParameterNames=[x.NAME for x in node.PARAMETERS]
            if EqualObjects(ParameterNames):
                self.errors.append(f"A method can't have 2 parameters with the same name")
        #--------------------------------------------------------------------
            # VISITING THE CHILDREN ✔️
        #--------------------------------------------------------------------        
            [self.visit(x,scope) for x in node.PARAMETERS]
        #--------------------------------------------------------------------
            #SAVING EVERY PIECE OF INFORMATION NEEDED IN SCOPE 1ST VISIT✔️
        #--------------------------------------------------------------------
            scope.AddFunctions(ProtocolMethodNode(node.NAME,node.PARAMETERS,node.TYPE))
        #--------------------------------------------------------------------
            # VISIT THE EXPRESSION ✔️
        #--------------------------------------------------------------------
        else:
            #Creating the scope for parameters
            new_scope=scope.CreateChild(node.NAME+' ')
            [new_scope.AddVariable(x.NAME,x.TYPE) for x in node.PARAMETERS]
            #visiting the corpus
            self.visit(node.CORPUS,new_scope)
        #--------------------------------------------------------------------
            # CHECKING POSSIBLE ERRORS IN FUNCTION NODE ON SECOND VISIT ✔️
        #--------------------------------------------------------------------    
            node.CORPUS.VALUE_TYPE=node.CORPUS.VALUE_TYPE
            if not scope.AreRelated(node.CORPUS.VALUE_TYPE,node.TYPE):
                self.errors.append(f"A object of type {node.TYPE} was expected, instead of {node.CORPUS.VALUE_TYPE}")
        #--------------------------------------------------------------------
        return self.errors

#_______________________________________________________________________________________
#_______________________________________________________________________________________  
#_______________________________________________________________________________________  
        
    @visitor.when(ExpressionBlockNode)
    def visit(self, node:ExpressionBlockNode, scope:Scope=None): #✔️✔️  
        for Expression in node.EXPRESSIONS:
            self.visit(Expression,scope)
        node.VALUE_TYPE=node.EXPRESSIONS[-1].VALUE_TYPE
        return self.errors
#_______________________________________________________________________________________  
#_______________________________________________________________________________________  
#_______________________________________________________________________________________  

#---------------------------------------------------------------------------------------
    #DEFINING VARIABLES
#---------------------------------------------------------------------------------------

    @visitor.when(LetNode)
    #DEFINING VARIABLE
    def visit(self, node:LetNode, scope:Scope=None): #✔️✔️  
        #Checking the assigned expression
        self.visit(node.VAR_VALUES[0],scope)
        ValueType=node.VAR_VALUES[0].VALUE_TYPE
        #Checking the parameter
        self.visit(node.VARS[0],scope)
        #Checking compatibility
        if not scope.AreRelated(ValueType,node.VARS[0].TYPE):
            self.errors.append(f'The expresion return {ValueType}, but {node.VARS[0].TYPE} was expected')
        #Creating a new scope for let expression
        new_scope=scope.CreateChild('let expression')
        new_scope.AddVariable(node.VARS[0].NAME,ValueType)    
        #Nesting the rest of the let expression
        if len(node.VAR_VALUES)>1:
            Simplest_node=LetNode(node.VARS[1:],node.VAR_VALUES[1:],node.EXPRESSION)
        #Visiting the expression
            self.visit(Simplest_node,new_scope)
        else:
            self.visit(node.EXPRESSION,new_scope)
        node.VALUE_TYPE=node.EXPRESSION.VALUE_TYPE
        return self.errors
    
    @visitor.when(DestructiveExpression)
    #REPLACES A VALUE
    def visit(self, node:DestructiveExpression, scope:Scope=None):#✔️
        if not scope.IsVariableDefined(node.NAME):
            self.errors.append(f"{node.NAME} doesn't exist in the current context")
        #A modificar
        if node.NAME=='self':
            self.errors.append(f"{node.NAME} can't be destroyed")
        self.visit(node.EXPRESSION,scope)    
        node.VALUE_TYPE=node.EXPRESSION.VALUE_TYPE
        return self.errors
    
    @visitor.when(SelfDestructiveExpression)
    #REPLACES A VALUE FOR A TYPE ATTRIBUTE
    def visit(self, node:SelfDestructiveExpression, scope:Scope=None):#✔️✔️
        self.visit(node.VAR,scope)
        #A modificar
        self.visit(node.EXPRESSION,scope)    
        if not scope.AreRelated(node.VAR.VALUE_TYPE, node.EXPRESSION):
            self.errors.append(f"You cannot change the variable type")
        node.VALUE_TYPE=node.EXPRESSION.VALUE_TYPE
        return self.errors
    
    @visitor.when(NewNode)
    #CREATES A NEW OBJECT WITH THE SPECIFIED ATRIBUTES
    def visit(self, node:NewNode, scope:Scope=None): #✔️✔️
        #Checking the type
        if not scope.IsTypeDefined(node.NAME):
            self.errors.append(f"The {node.NAME} type doesn't exist in the current context")
            node.VALUE_TYPE='Object'
            return self.errors
        #Getting the constructors
        Constructor=scope.SearchTypeParameters(node.NAME)
        if len(Constructor)!=len(node.ARGS):
            self.errors.append(f"Expected {len(Constructor)} arguments instead of {len(node.ARGS)}")
        #Visiting the arguments
        for i in len(Constructor):
            self.visit(node.ARGS[i])
            try:
                if not scope.AreRelated(node.ARGS[i].VALUE_TYPE,Constructor[i].TYPE):
                    self.errors.append(f"Expected type {Constructor[i].TYPE} instead of {node.ARGS[i].VALUE_TYPE}")
            except:
                continue
        node.VALUE_TYPE=node.NAME
        return self.errors

#_______________________________________________________________________________________  
#---------------------------------------------------------------------------------------
    #CONDITIONALS AND CYCLES
#---------------------------------------------------------------------------------------

    @visitor.when(IfElseExpression)
    #CONDITIONALS
    def visit(self, node:IfElseExpression, scope:Scope=None): #✔️✔️  
        #First check if the conditions are bool
        for i in range(len(node.CONDITIONS)):
            self.visit(node.CONDITIONS[i],scope)
            if node.CONDITIONS[i].VALUE_TYPE not in ['Boolean','Object']:
                self.errors.append(f'Boolean expression was expected')
        #Getting all possible values
        PossibleValueReturns=[]
        for i in range(len(node.CASES)):
            self.visit(node.CASES[i],scope)
            PossibleValueReturns.append(node.CASES[i].VALUE_TYPE)
        #The type is the last common ancestor
        node.VALUE_TYPE=scope.LastCommonAncestor(PossibleValueReturns)
        return self.errors

    @visitor.when(whileNode)
    #WHILE CYCLE
    def visit(self, node:whileNode, scope:Scope=None): #✔️✔️ 
        #Check if the condition is bool
        self.visit(node.CONDITIONS,scope)        
        if node.CONDITIONS.VALUE_TYPE not in ['Boolean','Object']:
            self.errors.append(f'Boolean expression was expected')
        #Visiting the expression
        self.visit(node.EXPRESSION,scope)
        node.VALUE_TYPE=node.EXPRESSION.VALUE_TYPE
        return self.errors

    @visitor.when(forNode)
    #FOR CYCLE
    def visit(self, node:forNode, scope:Scope=None): #✔️
        #First check if the condition is bool
        self.visit(node.COLECTION,scope)        
        if scope.AreRelated(node.COLECTION.VALUE_TYPE,'Iterable'):
            self.errors.append(f'Collection was expected')
        #Defining the variable
        new_scope=scope.CreateChild('for expression')
        new_scope.AddVariable(node.NAME,'Object')
        #Visiting the expression
        self.visit(node.EXPRESSION,new_scope)
        node.VALUE_TYPE=node.EXPRESSION.VALUE_TYPE
        return self.errors

#_______________________________________________________________________________________  

#---------------------------------------------------------------------------------------
    #OPERATIONS
#---------------------------------------------------------------------------------------

    @visitor.when(OrAndExpression)
    #BOOLEAN OPERATIONS BETWEEN BOOLEANS
    def visit(self, node:OrAndExpression, scope:Scope=None): #✔️✔️
        #Checking the left
        self.visit(node.LEFT,scope)
        if node.VALUE_TYPE not in ['Boolean','Object']:
            self.errors.append(f'Boolean expression was expected')
        #Checking the right
        self.visit(node.RIGHT,scope)
        if node.VALUE_TYPE not in ['Boolean','Object']:
            self.errors.append(f'Boolean expression was expected')
        node.VALUE_TYPE='Boolean'
        return self.errors

    @visitor.when(NotExpression)
    #BOOLEAN OPERATION TO BOOLEAN
    def visit(self, node:NotExpression, scope:Scope=None): #✔️✔️
        self.visit(node.EXPRESSION,scope)
        if node.VALUE_TYPE not in ['Boolean','Object']:
            self.errors.append(f'Boolean expression was expected')
        node.VALUE_TYPE='Boolean'
        return self.errors

    @visitor.when(ComparationExpression)
    #BOOLEAN OPERATION BETWEEN COMPARABLES
    def visit(self, node:ComparationExpression, scope:Scope=None): #✔️✔️
        #Checking the left
        self.visit(node.LEFT,scope)
        if not scope.AreRelated(node.LEFT.VALUE_TYPE,'Comparable'):
            self.errors.append(f'{node.LEFT.VALUE_TYPE} type is not Comparable')
        #Checking the right
        self.visit(node.RIGHT,scope)
        if not scope.AreRelated(node.LEFT.VALUE_TYPE,'Comparable'):
            self.errors.append(f'{node.LEFT.VALUE_TYPE} type is not Comparable')
        node.VALUE_TYPE='Boolean'
        return self.errors

    @visitor.when(AritmethicExpression)
    #ARITMETHIC OPERATION BETWEEN NUMBERS
    def visit(self, node:AritmethicExpression, scope:Scope=None): #✔️✔️
        #Checking the left
        self.visit(node.LEFT,scope)
        if node.LEFT.VALUE_TYPE not in ['Number','Object']:
            self.errors.append(f'Number expression was expected')
        #Checking the right
        self.visit(node.RIGHT,scope)
        if node.RIGHT.VALUE_TYPE not in ['Number','Object']:
            self.errors.append(f'Number expression was expected')
        node.VALUE_TYPE='Number'
        return self.errors

    @visitor.when(StringConcatenationNode)
    #CONCATENATION OF PRINTABLES
    def visit(self, node:StringConcatenationNode, scope:Scope=None): #✔️✔️
        #Checking the left
        self.visit(node.LEFT,scope)
        if not scope.AreRelated(node.LEFT.VALUE_TYPE,'Printable'):
            self.errors.append(f'{node.LEFT.VALUE_TYPE} type is not Printable')
        #Checking the right
        self.visit(node.RIGHT,scope)
        if not scope.AreRelated(node.RIGHT.VALUE_TYPE,'Printable'):
            self.errors.append(f'{node.RIGHT.VALUE_TYPE} type is not Printable')
        node.VALUE_TYPE='String'
        return self.errors

    @visitor.when(IsExpression)
    def visit(self, node:IsExpression, scope:Scope=None): #✔️✔️
        self.visit(node.LEFT,scope)
        if scope.IsTypeDefined(node.NAME):
            self.errors.append(f"The {node.NAME} type doesn't exist in the current context")
        node.VALUE_TYPE='Boolean'    
        return self.errors
#_____________________________________________________________________________________________________________________________  
#-------------------------------------------------------------------------------------------------------------------
    #TYPE NODES
#-------------------------------------------------------------------------------------------------------------------

    @visitor.when(NumberNode)#NUMBER
    def visit(self, node, scope:Scope=None): #✔️✔️
        node.VALUE_TYPE='Number'
        return self.errors
    
    @visitor.when(BooleanNode)#BOOLEAN
    def visit(self, node, scope:Scope=None): #✔️✔️
        node.VALUE_TYPE='Boolean'
        return self.errors
    
    @visitor.when(StringNode)#STRING
    def visit(self, node, scope:Scope=None): #✔️✔️
        node.VALUE_TYPE='String'
        return self.errors

    @visitor.when(Variable)
    def visit(self, node:Variable, scope:Scope=None): #✔️✔️
        #Check if it is defined
        if not scope.IsVariableDefined(node.NAME):
            self.errors.append(f"{node.NAME} doesn't exist in the current context")
        node.VALUE_TYPE=scope.VariableType(node.NAME)
        return self.errors
    
    @visitor.when(asNode)
    def visit(self, node:asNode, scope:Scope=None): #✔️✔️
        #Casting operation
        #Checking if the type exist
        if not scope.IsTypeDefined(node.TYPE):
            self.errors.append(f"{node.TYPE} type doesn't exist in the current context")
        #Checking if it is possible
        self.visit(node.EXPRESSION,scope)
        if not scope.AreRelated(node.TYPE,node.EXPRESSION.VALUE_TYPE):
            self.errors.append(f"The type of the expression doesn't match correctly")
        node.VALUE_TYPE=node.TYPE
        return self.errors
#______________________________________________________________________________
#------------------------------------------------------------------------------
    #FUNCTION CALLS AND CLASS PROPERTY CALLS
#------------------------------------------------------------------------------ 
    
    @visitor.when(FunctionCallNode)
    def visit(self, node:FunctionCallNode, scope:Scope=None): #✔️✔️
        #Searching the function
        function=scope.SearhFunction(node.FUNCT)
        if function==None:
            self.errors.append(f"The function {node.FUNCT} doesn't exist in the current context")
            node.VALUE_TYPE='Object'
            self.visit(node.ARGS[i],scope)
            return self.errors
        #Checking compatibility in number of arguments
        if len(function.PARAMETERS)!=len(node.ARGS):
            self.errors.append(f"Expected {len(function.PARAMETERS)} arguments instead of {len(node.ARGS)}")
        for i in range(min(len(function.PARAMETERS),len(node.ARGS))):
            #Visit the arguments
            self.visit(node.ARGS[i],scope)
            #Checking compatibility between arguments and paramaters
            if not scope.AreRelated(node.ARGS[i].VALUE_TYPE,function.PARAMETERS[i].TYPE):
                self.errors.append(f"Expected type {function.PARAMETERS[i].TYPE} instead of {node.ARGS[i].VALUE_TYPE}")
        node.VALUE_TYPE=function.TYPE
        return self.errors

    @visitor.when(TypeFunctionCallNode)
    def visit(self, node:TypeFunctionCallNode, scope:Scope=None): #✔️
        #visiting the class
        self.visit(node.CLASS,scope)
        #Checking if is possible that the method belongs to the type
        function=scope.SearhFunction(node.FUNCT,node.CLASS.VALUE_TYPE)
        if function==None:
            self.errors.append(f"The function {node.FUNCT} doesn't exist in the current context")
            node.VALUE_TYPE='Object'
        #Checking if the call is compatible
        elif len(function.PARAMETERS)!=len(node.ARGS):
            self.errors.append(f"Expected {len(function.PARAMETERS)} arguments instead of {len(node.ARGS)}")
            for i in range(min(len(function.PARAMETERS),len(node.ARGS))):
                self.visit(node.ARGS[i])
                if not scope.AreRelated(node.ARGS[i].VALUE_TYPE,function.PARAMETERS[i].TYPE):
                    self.errors.append(f"Expected type {function.PARAMETERS[i].TYPE} instead of {node.ARGS[i].VALUE_TYPE}")
            node.VALUE_TYPE=function.TYPE
        return self.errors

    @visitor.when(SelfVariableNode)#✔️✔️
    #THIS NODE IS ONLY FOR THE CASE self.ATRIBUTE
    def visit(self, node:SelfVariableNode, scope:Scope=None):
        Variables=scope.TypeAtributes()
        #If the left expression is not self, Error
        #If this node is not inside a type, Error
        if Variables==None or not node.IS_SELF:
            self.errors.append('Attributes are private')
            node.VALUE_TYPE='Object'
        #If the name is not an attribute, Error
        elif node.NAME not in [x[0] for x in Variables]:
            self.errors.append(f'{node.NAME} is not defined in the current context')
            node.VALUE_TYPE='Object'
        else:
            node.VALUE_TYPE=[x[1] for x in Variables if x[0]==node.NAME][0]
        return self.errors
#______________________________________________________________________________
#------------------------------------------------------------------------------
    #VECTORS. EXPLICIT, IMPLICIT AND INDEXING    
#------------------------------------------------------------------------------

    @visitor.when(ListNode)
    def visit(self, node:ListNode, scope:Scope=None): #✔️
        for element in node.ELEMENTS:
            self.visit(element,scope)
        node.VALUE_TYPE='Vector'
        return self.errors
    
    @visitor.when(ImplicitListNode)
    def visit(self, node:ImplicitListNode, scope:Scope=None): #✔️
        #This must be a collection
        self.visit(node.COLLECTION,scope)
        if node.COLLECTION.VALUE_TYPE!='Object' and not scope.AreRelated(node.COLLECTION.VALUE_TYPE,'Iterable'):
            self.errors.append(f"{node.COLLECTION.VALUE_TYPE} object is not a iterable")
        #Defining the iterator
        new_scope=scope.CreateChild('Implicit List')
        new_scope.AddVariable(node.ITERATION,'Object')
        #Checking the operation
        self.visit(node.OPERATION,new_scope)
        #Returning vector. This could be editable to know the type of the vector
        node.VALUE_TYPE='Vector'
        return self.errors
    
    @visitor.when(InexingNode)
    def visit(self, node:InexingNode, scope:Scope=None): #✔️
        self.visit(node.COLLECTION,scope)
        #The left has to be a collection
        if not scope.AreRelated('Iterable',node.COLLECTION.VALUE_TYPE):
            self.errors.append(f"{node.COLLECTION.VALUE_TYPE} object is not a iterable")
        #The right has to be a number
        self.visit(node.INDEX,scope)
        if not scope.AreRelated('Number',node.INDEX.VALUE_TYPE):
            self.errors.append(f"{node.INDEX.VALUE_TYPE} object is not a number")
        #This sould return the type of the collection
        node.VALUE_TYPE='Object'
        return self.errors
    