from Common.ASTNodes import *

class Scope:
    def __init__(self, parent=None):
        self.parent = parent  #Used for search in the parent scope
        self.type_names=[]  #Used to comprobe if a type exist
        self.protocol_names=[]  #Used to comprobe if a protocol exist
        self.AlreadyVisitedType=set()  #Allows to visit a Type two times
        self.AlreadyVisitedFunction=set()  #Allows to visit a function two times
        self.variables=[]  #Allows to comprobe if a variable was declared
        self.localFunctions=[]  #Used to comprobe if a method exist
        self.children=dict()  #Allow to have a children scope
        self.ProtocolFunctions=dict()  #Remember all the methods of a Protocol
        self.ProtocolExtensions=dict()  #Remember the hierarchy for protocols
        self.TypeFunctions=dict()  #Remember all the methods of a Type
        self.TypeHierarchy=dict()  #Remember the hierarchy for types
        self.TypeParameters=dict()  #Remember the constructor for every class

    #ADD THE TYPES FOR THE SCOPE
    def AddTypes(self,types:list[str]):
        self.type_names=types
    #CHECK IF A TYPE IS DEFINED
    def IsTypeDefined(self,name:str):
        if name in self.type_names:
            return True
        if self.parent==None:
            return False
        return self.parent.IsTypeDefined(name)
    #ADD THE HIERARCHY
    def AddTypeHierarchy(self,Hierarchy:dict[str,str]):
        self.TypeHierarchy=Hierarchy
    #ADD THE CONSTRUCTORS FOR A TYPE
    def AddTypeParameters(self,name:str,params:list):
        self.TypeParameters[name]=params
    #SEARCH THE CONSTRUCTOR OF A TYPE
    def SearchTypeParameters(self,name):
        if name in self.type_names:
            return self.TypeParameters[name]
        elif self.parent==None:
            return []
        return self.parent.SearchTypeParameters(name)
    #SAVE THE FUNCTIONS OF THE TYPE (used for checking if satisfies a protocol)
    def AddTypeFunctions(self,name:str,functions:list):
        self.TypeFunctions[name]=functions
    #RETURN FALSE ONLY IF YOU HAVENT VISITED
    def TypeVisited(self,name:str):
        if name in self.AlreadyVisitedType:
            return True
        self.AlreadyVisitedType.add(name)
        return False

    #ADD THE PROTOCOLS FOR THE SCOPE
    def AddProtocols(self,protocols:list[str]):
        self.protocol_names=protocols
    #SEARCH IF THE PROTOCOL WAS DEFINED
    def IsProtocolDefined(self,name:str):
        if name in self.protocol_names:
            return True
        if self.parent==None:
            return False
        return self.parent.IsProtocolDefined(name)
    #ADD THE FUNCTIONS THAT THE PROTOCOL CONTAINS
    def AddProtocolFunctions(self,name:str ,functions:list):
        self.ProtocolFunctions[name]=functions
    #ADD THE PROTOCOL EXTENSIONS
    def AddProtocolExtensions(self,extensions:dict[str,str]):
        self.ProtocolExtensions=extensions

    #DEFINE A VARIABLE FOR A SCOPE
    def AddVariable(self,name:str,type:str):
        self.variables.append((name,type))
    #RETURN TRUE IF THE VARIABLE WAS IN THE SCOPE OR IN A FATHER SCOPE
    def IsVariableDefined(self,name):
        if name in [x[0] for x in self.variables]:
            return True
        elif self.parent==None:
            return False
        return self.parent.IsVariableDefined(name)
    #USED TO INFER THE TYPE
    def UpdateVariableValue(self,name,type):
        self.variables=[x if name!=x[0] else (name,type) for x in self.variables]
    #AVOID A=A IN TYPE ATRIBUTES
    def RemoveVariable(self,name,type):
        self.variables.remove((name,type))
    #RETURN THE TYPE OF A VARIABLE
    def VariableType(self,name):
        if name in [x[0] for x in self.variables]:
            return [x[1] for x in self.variables if x[0]==name][0]
        elif self.parent==None:
            return 'Object'
        return self.parent.VariableType(name)

    #SAVE A FUNCTION NAME, AND PARAMS
    def AddFunctions(self,method):
        self.localFunctions(method)
    #ALLOWS TO VISIT A METHOD TWICE
    def FunctionVisited(self,name:str):
        if name in self.AlreadyVisitedFunction:
            return True
        self.AlreadyVisitedFunction.add(name)
        return False
    def SearhFunction(self,name:str,OnType:str=''):
        if OnType=='':
            for funct in self.localFunctions:
                if funct.name==name:
                    return funct
            if self.parent==None:
                return None
            return self.parent.SearhFunction(self,name,'')
        if name in self.type_names:    
            for funct in self.TypeFunctions[OnType]:
                if funct.name==name:
                    return funct
        if self.parent==None:
            return None
        return self.parent.SearhFunction(self,name,OnType)
    
    #CREATES A NEW SCOPE WITH A SPECIFIC NAME
    def CreateChild(self,name:str):
        child_scope = Scope(self)
        self.children[name]=child_scope
        return child_scope
    #RETURN A SCOPE WITH A NAME
    def GetChild(self,name:str):
        return self.children[name]
    

    def AreRelated(self,Type1:str,Type2:str):
        pass