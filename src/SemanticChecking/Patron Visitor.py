import itertools as itl
from Common.ASTNodes import *
import Common.Visitor as visitor
from SemanticChecking.Auxiliars import *
from SemanticChecking.Scope import Scope


class SemanticCheckerVisitor(object):
    def __init__(self):
        self.errors = []
        self.LastValueType=None

    @visitor.on('Node')
    def visit(self, node, scope:Scope):
        pass
    
#_______________________________________________________________________________________
    @visitor.when(ProgramNode)
    def visit(self, node, scope:Scope=None):#✔️
        #--------------------------------------------------------------------
            # CHECKING POSSIBLE ERRORS IN PROGRAM NODE ✔️
        #--------------------------------------------------------------------
        #Avoiding repited Types
        defaultTypes = ['Object','Number','Boolean','String','Vector']
        TypeNames= defaultTypes + [x.name for x in node.Statements if x is TypeNode]
        if not NotEqualObjects(TypeNames):
            self.errors.append('There is two declarations of the same Type')
        
        #Avoiding repited Protocols
        defaultProtocols=['Iterable']
        ProtocolNames= defaultProtocols+[x.name for x in node.Statements if x is ProtocolNode]
        if not NotEqualObjects(ProtocolNames):
            self.errors.append('There is two declarations of the same protocol')
        
        #Avoiding repited Functions
        defaultFunctions=['print','sen','cos','rand','sqrt','exp','log']
        FuncNames= defaultFunctions + [x.name for x in node.Statements if x is FunctionNode]
        if not NotEqualObjects(FuncNames):
            self.errors.append('There is two declarations of the same function')
        
        #Avoiding circular inherence
        Inherence=dict([(x.name,x.inherits) for x in node.Statements if x is TypeNode])
        Inherence['Object']=''
        Inherence['Number']='Object'
        Inherence['Boolean']='Object'
        Inherence['String']='Object'
        Inherence['Vector']='Object'
        TypeOrder, TreeForm=GetTopologicOrder(Inherence)
        if not TreeForm:
            self.errors.append("There is a circular dependence between protocols")
        
        #Avoiding circular extensions
        Extensions=dict([(x.name,x.extends) for x in node.Statements if x is ProtocolNode])
        Extensions['Iterable']=''
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
        for Protocol in [x for x in node.Statements if node is ProtocolNode]:
            self.visit(Protocol,scope)
        
        #visiting the classes in topologic order 1st time
        TypeQuickAccess=dict([(x.name,x) for x in node.Statements if node is TypeNode])
        for Type in TypeOrder:
            if Type in defaultTypes:
                continue
            self.visit(TypeQuickAccess[Type],scope)

        #visiting the functions 1st time
        for Function in [x for x in node.Statements if x is FunctionNode]:
            self.visit(Function,scope)
        
        #visiting the classes in topologic order 2nd time
        TypeQuickAccess=dict([(x.name,x) for x in node.Statements if node is TypeNode])
        for Type in TypeOrder:
            if Type in defaultTypes:
                continue
            self.visit(TypeQuickAccess[Type],scope)
        
        #visiting the functions 2nd time
        for Function in [x for x in node.Statements if x is FunctionNode]:
            self.visit(Function,scope)

        #visiting the expression        
        self.visit(node.Expression,scope)
        #-----------------------------------------------------------------------
#_______________________________________________________________________________________        
    
    @visitor.when(ProtocolNode)
    def visit(self, node, scope:Scope=None):#✔️
        #--------------------------------------------------------------------
            # CHECKING POSSIBLE ERRORS IN PROTOCOL NODE ✔️
        #--------------------------------------------------------------------
        #Cheking that the protocol doesn't extend itself
        if node.extends == node.name:
            self.errors.append(f"The protocol {node.extends} doesn't exist in the current context")
        #Cheking that the protocol extend something that exist
        if not scope.IsProtocolDefined(node.extends):
            self.errors.append(f"The protocol {node.extends} doesn't exist in the current context")
        #Avoiding repited Functions
        FuncNames= [x.name for x in node.Corpus]
        if not NotEqualObjects(FuncNames):
            self.errors.append('There is two declarations of the same function')
        #-----------------------------------------------------------------------
            #SAVING EVERY PIECE OF INFORMATION NEEDED IN SCOPE✔️
        #-----------------------------------------------------------------------
        scope.AddProtocolFunctions(node.name,node.Corpus)
        #-----------------------------------------------------------------------
            #VISITING ALL CHILDREN ✔️
        #-----------------------------------------------------------------------
        [self.visit(x,scope) for x in node.Corpus]
        #-----------------------------------------------------------------------
#_______________________________________________________________________________________        
    
    @visitor.when(ProtocolMethodNode)
    def visit(self, node, scope:Scope=None): #✔️
        #--------------------------------------------------------------------
            # CHECKING POSSIBLE ERRORS IN PROTOCOL METHOD NODE ✔️
        #--------------------------------------------------------------------
        #Checking function Type
        if not scope.IsTypeDefined(node.Type) and not scope.IsProtocolDefined(node.Type):
            self.errors.append(f"The Type {node.Type} is not defined in this scope")
        #Checking doble parameters
        ParameterNames=[x.name for x in node.Parameters]
        if NotEqualObjects(ParameterNames):
            self.errors.append(f"A method can't have 2 parameters with the same name")
        #--------------------------------------------------------------------
            #VISITING ALL CHILDREN ✔️
        #--------------------------------------------------------------------
        [self.visit(x,scope) for x in node.Parameters]
        #--------------------------------------------------------------------
#_______________________________________________________________________________________        

    @visitor.when(ParameterNode)
    def visit(self, node, scope:Scope=None): # ✔️
        #--------------------------------------------------------------------
        # CHECKING POSSIBLE ERRORS IN PARAMETER NODE ✔️
        #--------------------------------------------------------------------
         #Checking parameter Type
        if not scope.IsTypeDefined(node.Type) and not scope.IsProtocolDefined(node.Type):
            self.errors.append(f"The Type {node.Type} is not defined in this scope")        
        #--------------------------------------------------------------------
#_______________________________________________________________________________________        

    @visitor.when(TypeNode)
    def visit(self, node, scope:Scope=None): #✔️
        
        firstVisit=scope.AlreadyVisitedType(node.name)
        #--------------------------------------------------------------------
            # CHECKING POSSIBLE ERRORS IN TYPE NODE ✔️
        #--------------------------------------------------------------------
        if firstVisit:
            # Avoiding self inherence
            if node.inherits == node.name:
                self.errors.append(f"The protocol {node.inherits} doesn't exist in the current context")
            #Cheking that the type inherits exist
            if not scope.IsTypeDefined(node.inherits) and not scope.IsProtocolDefined(node.inherits):
                self.errors.append(f"The type {node.inherits} doesn't exist in the current context")            
            #Avoiding duplicated constructor parameters
            ParameterNames=[x.name for x in node.ConstructorParameters]
            if NotEqualObjects(ParameterNames):
                self.errors.append(f"A method can't have 2 parameters with the same name")
            #Avoiding duplicated Atributes
            AtributeNames=[x.name for x in node.Corpus if x is TypeAtributeNode]
            if NotEqualObjects(AtributeNames):
                self.errors.append(f"A type can't have 2 atributes with the same name")
            #Avoiding duplicated functions
            AtributeNames=[x for x in node.Corpus if x is FunctionNode]
            if NotEqualObjects(AtributeNames):
                self.errors.append(f"A type can't have 2 functions with the same name and the same amount of parameters")
            #checking that the inherit parameters amount match with the Arguments number
            parentParameters=scope.SearchTypeParameters(node.inherits)
            if len(parentParameters)!=len(node.Arguments):
                self.errors.append(f"Expected {len(parentParameters)} arguments instead of {len(node.Arguments)}")
        
        else:
            #Checking that the argument match with the parameters
            parentParameters=scope.SearchTypeParameters(node.inherits)
            for i in len(parentParameters):
                self.visit(node.Arguments[i])
                if not scope.AreRelated(self.LastValueType,parentParameters[i].Type):
                    self.errors.append(f"Expected type {parentParameters[i].Type} instead of {self.LastValueType}")
        #--------------------------------------------------------------------
            #SAVING EVERY PIECE OF INFORMATION NEEDED IN SCOPE✔️
        #--------------------------------------------------------------------
        if firstVisit:
            #Scope for parameters and self atribute
            new_scope=scope.CreateChild(node.name)
            map(lambda x:new_scope.AddVariable(x.name,x.Type),node.ConstructorParameters)
            if not 'self' in [x.name for x in node.ConstructorParameters]:
                #scope for atributes and functions
                new_scope.AddVariable('scope',node.name)
            new_scope=new_scope.CreateChild('self')
            scope.AddTypeFunctions([ProtocolMethodNode(x.name,x.Parameters,x.Type) for x in node.Corpus if x is FunctionNode])
        #-----------------------------------------------------------------------
            #VISITING ALL CHILDREN ✔️
        #--------------------------------------------------------------------
        #Visiting the parameters
        [self.visit(x,scope) for x in node.Parameters]
        #Visiting the atributes
        [self.visit(x,scope.GetChild(node.name).GetChild('self')) 
                    for x in node.Corpus if x is TypeAtributeNode]
        #Visiting the functions
        [self.visit(x,scope.GetChild(node.name).GetChild('self')) 
                    for x in node.Corpus if x is FunctionNode]
        #--------------------------------------------------------------------    
#_______________________________________________________________________________________  

    @visitor.when(TypeAtributeNode)
    def visit(self, node, scope:Scope=None):#✔️     
         #Define the variable on first visit
        if scope.IsVariableDefined(node.name):
            scope.AddVariable(node.name,'Object')
        #Explore the value on second visit
        else:
            scope.RemoveVariable(node.name,'Object')
            self.visit(node.value,scope)
            scope.UpdateVariableValue(node.name,self.LastValueType)
#_______________________________________________________________________________________  
    
    @visitor.when(FunctionNode)
    def visit(self, node, scope:Scope=None): #✔️   
        #--------------------------------------------------------------------
            # CHECKING POSSIBLE ERRORS IN FUNCTION NODE ON FIRST VISIT✔️
        #--------------------------------------------------------------------
        if scope.AlreadyVisitedFunction(node.name):
            #Checking function Type
            if not scope.IsTypeDefined(node.Type) and not scope.IsProtocolDefined(node.Type):
                self.errors.append(f"The Type {node.Type} is not defined in this scope")
            #Checking doble parameters
            ParameterNames=[x.name for x in node.Parameters]
            if NotEqualObjects(ParameterNames):
                self.errors.append(f"A method can't have 2 parameters with the same name")
        #--------------------------------------------------------------------
            # VISITING THE CHILDREN ✔️
        #--------------------------------------------------------------------        
            [self.visit(x,scope) for x in node.Parameters]
        #--------------------------------------------------------------------
            #SAVING EVERY PIECE OF INFORMATION NEEDED IN SCOPE 1ST VISIT✔️
        #--------------------------------------------------------------------
            scope.AddFunctions(ProtocolMethodNode(node.name,node.Parameters,node.Type))
        #--------------------------------------------------------------------
            # VISIT THE EXPRESSION ✔️
        #--------------------------------------------------------------------
        else:
            #Creating the scope for parameters
            new_scope=scope.CreateChild(node.name+' ')
            map(lambda x:new_scope.AddVariable(x.name,x.Type),node.Parameters)
            #visiting the corpus
            self.visit(node.Corpus,new_scope)
        #--------------------------------------------------------------------
            # CHECKING POSSIBLE ERRORS IN FUNCTION NODE ON SECOND VISIT ✔️
        #--------------------------------------------------------------------    
            if not scope.AreRelated(node.Type,self.LastValueType):
                self.errors.append("The method doesn't return the specified type")        
        #--------------------------------------------------------------------
#_______________________________________________________________________________________  
        
    @visitor.when(ExpressionBlockNode)
    def visit(self, node, scope:Scope=None): #✔️  
        for Expression in node.Expressions:
            self.visit(Expression,scope)
#_______________________________________________________________________________________  

    @visitor.when(LetNode)
    def visit(self, node, scope:Scope=None): #✔️  
        new_scope=scope.CreateChild('let expression')
        for i in len(node.variables):
            self.visit(node.variables_values[i],new_scope)
            ValueType=self.LastValueType
            self.visit(node.variables[i],scope)
            if not scope.AreRelated(ValueType,node.variables[i].Type):
                self.errors.append(f'The expresion return {ValueType}, but {node.variables[i].Type} was expected')
            new_scope.AddVariable(node.variables[i].name,node.variables[i].Type)
        self.visit(node.Expression,new_scope)
#_______________________________________________________________________________________  

    @visitor.when(IfElseExpression)
    def visit(self, node, scope:Scope=None): #✔️  
        #First check if the conditions are bool
        for i in len(node.Conditions):
            self.visit(node.Conditions[i],scope)
            if self.LastValueType not in ['Boolean','Object']:
                self.errors.append(f'Boolean expression was expected')
        PossibleValueReturns=set()
        for i in len(node.cases):
            self.visit(node.cases[i],scope)
            PossibleValueReturns.add(self.LastValueType)
        #To edit: if all are equal return the type, else return object
        if len(PossibleValueReturns)!=1:
            self.LastValueType='Object'
#_______________________________________________________________________________________  

    @visitor.when(whileNode)
    def visit(self, node, scope:Scope=None): #✔️  
        #First check if the condition is bool
        self.visit(node.Condition,scope)        
        if self.LastValueType not in ['Boolean','Object']:
            self.errors.append(f'Boolean expression was expected')
        self.visit(node.Expression,scope)
#_______________________________________________________________________________________  

    @visitor.when(forNode)
    def visit(self, node, scope:Scope=None): #✔️  
        #First check if the condition is bool
        self.visit(node.Colection,scope)        
        if scope.AreRelated(self.LastValueType,'Iterable') or self.LastValueType=='Object':
            self.errors.append(f'Collection was expected')
        new_scope=scope.CreateChild('for expression')
        new_scope.AddVariable(node.name,'Object')
        self.visit(node.Expression,new_scope)
#_______________________________________________________________________________________  

    @visitor.when(DestructiveExpression)
    def visit(self, node, scope:Scope=None): #✔️
        if not scope.IsVariableDefined(node.name):
            self.errors.append(f"{node.name} doesn't exist in the current context")
        #A modificar
        if node.name=='scope':
            self.errors.append(f"{node.name} can't be destroyed")
        self.visit(node.Expression,scope)    
#_______________________________________________________________________________________  
    
    @visitor.when(NewNode)
    def visit(self, node, scope:Scope=None): #✔️
        if not scope.IsTypeDefined(node.name):
            self.errors.append(f"The {node.name} type doesn't exist in the current context")
        Constructor=scope.SearchTypeParameters(node.name)
        if len(Constructor)!=len(node.arguments):
            self.errors.append(f"Expected {len(Constructor)} arguments instead of {len(node.arguments)}")
        for i in len(Constructor):
            self.visit(node.arguments[i])
            if not scope.AreRelated(self.LastValueType,Constructor[i].Type):
                self.errors.append(f"Expected type {Constructor[i].Type} instead of {self.LastValueType}")
        self.LastValueType=node.name

#_______________________________________________________________________________________  

    @visitor.when(OrAndExpression)
    def visit(self, node, scope:Scope=None): #✔️
        self.visit(node.left,scope)
        if self.LastValueType not in ['Boolean','Object']:
            self.errors.append(f'Boolean expression was expected')
        self.visit(node.right,scope)
        if self.LastValueType not in ['Boolean','Object']:
            self.errors.append(f'Boolean expression was expected')
        self.LastValueType='Boolean'
#_______________________________________________________________________________________  

    @visitor.when(NotExpression)
    def visit(self, node, scope:Scope=None): #✔️
        self.visit(node.left,scope)
        if self.LastValueType not in ['Boolean','Object']:
            self.errors.append(f'Boolean expression was expected')
        self.LastValueType='Boolean'
#_______________________________________________________________________________________  

    @visitor.when(ComparationExpression)
    def visit(self, node, scope:Scope=None): #✔️
        self.visit(node.left,scope)
        self.visit(node.right,scope)
        self.LastValueType='Boolean'
#_______________________________________________________________________________________  

    @visitor.when(AritmethicExpression)
    def visit(self, node, scope:Scope=None): #✔️
        self.visit(node.left,scope)
        if self.LastValueType not in ['Number','Object']:
            self.errors.append(f'Number expression was expected')
        self.visit(node.right,scope)
        if self.LastValueType not in ['Number','Object']:
            self.errors.append(f'Number expression was expected')
        self.LastValueType='Number'
#_______________________________________________________________________________________  

    @visitor.when(StringConcatenationNode)
    def visit(self, node, scope:Scope=None): #✔️
        self.visit(node.Left,scope)
        if self.LastValueType not in ['String','Object']:
            self.errors.append(f'String expression was expected')
        self.visit(node.right,scope)
        if self.LastValueType not in ['String','Object']:
            self.errors.append(f'String expression was expected')
        self.LastValueType='String'
#_______________________________________________________________________________________  

    @visitor.when(IsExpression)
    def visit(self, node, scope:Scope=None): #✔️
        self.visit(node.left,scope)
        if scope.IsTypeDefined(node.name):
            self.errors.append(f"The {node.name} type doesn't exist in the current context")
        self.LastValueType='Boolean'    
#_______________________________________________________________________________________  

    @visitor.when(NumberNode)
    def visit(self, node, scope:Scope=None): #✔️
        self.LastValueType='Number'
    @visitor.when(BooleanNode)
    def visit(self, node, scope:Scope=None): #✔️
        self.LastValueType='Boolean'
    @visitor.when(StringNode)
    def visit(self, node, scope:Scope=None): #✔️
        self.LastValueType='String'
    @visitor.when(Variable)
    def visit(self, node, scope:Scope=None): #✔️
        if not scope.IsVariableDefined(node.name):
            self.errors.append(f"{node.name} doesn't exist in the current context")
        self.LastValueType=scope.VariableType(node.name)
    @visitor.when(asNode)
    def visit(self, node, scope:Scope=None): #✔️
        if not scope.IsTypeDefined(node.Type):
            self.errors.append(f"{node.name} type doesn't exist in the current context")
        self.visit(node.Expression,scope)
        if not scope.AreRelated(node.Type,self.LastValueType):
            self.errors.append(f"The type of the expression doesmn't match correctly")
        self.LastValueType=node.Type
    
#_______________________________________________________________________________________  
    
    @visitor.when(FunctionCallNode)
    def visit(self, node, scope:Scope=None): #✔️
        function=scope.SearhFunction(node.function)
        if function==None:
            self.errors.append(f"The function {node.function} doesn't exist in the current context")
        if len(function.Parameters)!=len(node.Arguments):
            self.errors.append(f"Expected {len(function.Parameters)} arguments instead of {len(node.Arguments)}")
        for i in len(function.Parameters):
            self.visit(node.Arguments[i])
            if not scope.AreRelated(self.LastValueType,function.Parameters[i].Type):
                self.errors.append(f"Expected type {function.Parameters[i].Type} instead of {self.LastValueType}")
        self.LastValueType=function.Type

    @visitor.when(TypeFunctionCallNode)
    def visit(self, node, scope:Scope=None): #✔️
        self.visit(node.classCalling)
        if self.LastValueType != 'Object':
            function=scope.SearhFunction(node.function,self.LastValueType)
            if function==None:
                self.errors.append(f"The function {node.function} doesn't exist in the current context")
            if len(function.Parameters)!=len(node.Arguments):
                self.errors.append(f"Expected {len(function.Parameters)} arguments instead of {len(node.Arguments)}")
            for i in len(function.Parameters):
                self.visit(node.Arguments[i])
                if not scope.AreRelated(self.LastValueType,function.Parameters[i].Type):
                    self.errors.append(f"Expected type {function.Parameters[i].Type} instead of {self.LastValueType}")
            self.LastValueType=function.Type
        else:
            for param in node.Arguments:
                self.visit(param,scope)
            self.LastValueType='Object'
#_______________________________________________________________________________________  

    @visitor.when(ListNode)
    def visit(self, node, scope:Scope=None): #✔️
        for element in node.Elements:
            self.visit(element,scope)
        self.LastValueType='Vector'
    @visitor.when(ImplicitListNode)
    def visit(self, node, scope:Scope=None): #✔️
        self.visit(node.collection,scope)
        if self.LastValueType!='Object' and not scope.AreRelated(self.LastValueType,'Iterable'):
            self.errors.append(f"{self.LastValueType} object is not a iterable")
        new_scope=scope.CreateChild('Implicit List')
        new_scope.AddVariable(node.iterator,'Object')
        self.visit(node.operator,new_scope)
        self.LastValueType='Vector'
    @visitor.when(InexingNode)
    def visit(self, node:InexingNode, scope:Scope=None): #✔️
        self.visit(node.collection,scope)
        if not scope.AreRelated('Iterable',self.LastValueType):
            self.errors.append(f"{self.LastValueType} object is not a iterable")
        self.visit(node.index,scope)
        if not scope.AreRelated('Number',self.LastValueType):
            self.errors.append(f"{self.LastValueType} object is not a number")
        self.LastValueType='Object'