from Common.ASTNodes import *

class Scope:
    def __init__(self, parent=None):
        self.PARENT = parent  #Used for search in the parent scope
        self.TYPE_NAMES=[]  #Used to comprobe if a type exist
        self.PROTOCOL_NAMES=[]  #Used to comprobe if a protocol exist
        self.VISITED_TYPES=set()  #Allows to visit a Type two times
        self.VISITED_FUNCTIONS=set()  #Allows to visit a function two times
        self.VARS=[]  #Allows to comprobe if a variable was declared
        self.FUNCTIONS=[]  #Used to comprobe if a method exist
        self.CHILDREN=dict()  #Allow to have a children scope
        self.PROTOCOL_FUNCT=dict()  #Remember all the methods of a Protocol
        self.PROTOCOL_EXTENSIONS=dict()  #Remember the hierarchy for protocols
        self.TYPE_FUNCTIONS=dict()  #Remember all the methods of a Type
        self.TYPE_HIERARCHY=dict()  #Remember the hierarchy for types
        self.CONSTRUCTORS=dict()  #Remember the constructor for every class
        self.SELF_ACTIVE=False if parent is None else parent.SELF_ACTIVE #To avoid self:=...
#----------------------------------------------------------------------------
    #MANAGE THE TYPES OF THE SCOPE
#----------------------------------------------------------------------------
    def AddTypes(self,types:list[str])->None:
    #ADD THE TYPES FOR THE SCOPE
        self.TYPE_NAMES=types
    
    def IsTypeDefined(self,name:str)->bool:
    #CHECK IF A TYPE IS DEFINED
        if name in self.TYPE_NAMES:
            return True
        if self.PARENT==None:
            return False
        return self.PARENT.IsTypeDefined(name)
    
    def AddTypeHierarchy(self,Hierarchy:dict[str,str])->None:
    #ADD THE HIERARCHY
        self.TYPE_HIERARCHY=Hierarchy
    
    def AddTypeParameters(self,name:str,params:list[ParameterNode])->None:
    #ADD THE CONSTRUCTORS FOR A TYPE
        self.CONSTRUCTORS[name]=params
    
    def SearchTypeParameters(self,name:str)->list[ParameterNode]:
    #SEARCH THE CONSTRUCTOR OF A TYPE
        if name in self.TYPE_NAMES:
            return self.CONSTRUCTORS[name]
        elif self.PARENT==None:
            return []
        return self.PARENT.SearchTypeParameters(name)
    
    def AddTypeFunctions(self,name:str,functions:list[FunctionNode])->None:
    #SAVE THE FUNCTIONS OF THE TYPE (used for checking if satisfies a protocol)
        self.TYPE_FUNCTIONS[name]=[ProtocolMethodNode(x.NAME,x.PARAMETERS,x.TYPE) for x in functions]
    
    def TypeVisited(self,name:str)->bool:
    #RETURN FALSE ONLY IF YOU HAVENT VISITED
        if name in self.VISITED_TYPES:
            return True
        self.VISITED_TYPES.add(name)
        return False
    
#----------------------------------------------------------------------------
    #MANAGE THE PROTOCOLS OF THE SCOPE
#----------------------------------------------------------------------------
    def AddProtocols(self,protocols:list[str])->None:
    #ADD THE PROTOCOLS FOR THE SCOPE
        self.PROTOCOL_NAMES=protocols
    
    def IsProtocolDefined(self,name:str)->bool:
    #SEARCH IF THE PROTOCOL WAS DEFINED
        if name in self.PROTOCOL_NAMES:
            return True
        if self.PARENT==None:
            return False
        return self.PARENT.IsProtocolDefined(name)
    
    def AddProtocolFunctions(self,name:str,functions:list[ProtocolMethodNode])->None:
    #ADD THE FUNCTIONS THAT THE PROTOCOL CONTAINS
        self.PROTOCOL_FUNCT[name]=functions
    
    def AddProtocolExtensions(self,extensions:dict[str,str])->None:
    #ADD THE PROTOCOL EXTENSIONS
        self.PROTOCOL_EXTENSIONS=extensions

#----------------------------------------------------------------------------
    #MANAGE THE VARIABLES OF THE SCOPE
#----------------------------------------------------------------------------
    #DEFINE A VARIABLE FOR A SCOPE
    def AddVariable(self,name:str,type:str)->None:
        self.VARS.append((name,type))
        if name == 'self':
            self.SELF_ACTIVE=False
    
    def IsVariableDefined(self,name:str)->bool:
    #RETURN TRUE IF THE VARIABLE WAS IN THE SCOPE OR IN A FATHER SCOPE
        if name in [x[0] for x in self.VARS]:
            return True
        elif self.PARENT==None:
            return False
        return self.PARENT.IsVariableDefined(name)
    
    def UnlockVariables(self)->None:
    #USED TO INFER THE TYPE
        self.VARS=[(x[0][1:],x[1]) for x in self.VARS if x[0][0]==' ']
    
    def RemoveVariable(self,name:str,type:str)->None:
    #AVOID A=A IN TYPE ATRIBUTES
        self.VARS.remove((name,type))
    
    def VariableType(self,name:str)->str:
    #RETURN THE TYPE OF A VARIABLE
        if name in [x[0] for x in self.VARS]:
            return [x[1] for x in self.VARS if x[0]==name][0]
        elif self.PARENT==None:
            return 'Object'
        return self.PARENT.VariableType(name)
    
#----------------------------------------------------------------------------
    #MANAGE THE FUNCTIONS OF THE SCOPE
#----------------------------------------------------------------------------
    def AddFunctions(self,method:ProtocolMethodNode)->None:
    #SAVE A FUNCTION NAME, AND PARAMS
        self.FUNCTIONS.append(method)
    def RemoveFunction(self,method:str):
    #REMOVE A FUNCTION
        self.FUNCTIONS=[x for x in self.FUNCTIONS if x.NAME==method]

    def FunctionVisited(self,name:str)->bool:
    #ALLOWS TO VISIT A METHOD TWICE, (only for program node)
        if name in self.VISITED_FUNCTIONS:
            return True
        self.VISITED_FUNCTIONS.add(name)
        return False
    
    def SearhFunction(self,name:str,OnType:str='')->ProtocolMethodNode:
    #SEARCH A FUNCTION. OnType!='' FOR TYPE METHODS
        if OnType=='':
        #Global function case
            for funct in self.FUNCTIONS:
                if funct.NAME==name:
                    return funct
            if self.PARENT==None:
                return None
            return self.PARENT.SearhFunction(name,'')
        #Type case, searching. The search extends for all possible class hierarchy
        if OnType in self.TYPE_NAMES:
            for funct in self.ExtendedSearch(OnType):
                if funct.NAME==name:
                    return funct
        #Asking the parent
        if self.PARENT==None:
            return None
        return self.PARENT.SearhFunction(self,name,OnType)
    
    def ExtendedSearch(self,type_name:str):
    #RETURN THE FUNCTIONS FROM THE TYPE
        #First check the Functions from itself or his ancestors
        x=type_name
        while x!='Object':
            if x not in self.TYPE_NAMES:
                return
            for f in self.TYPE_FUNCTIONS[x]:
                yield f
            x=self.TYPE_HIERARCHY[x]
#----------------------------------------------------------------------------
    #MANAGE THE SCOPES
#----------------------------------------------------------------------------
    def CreateChild(self,name:str):
    #CREATES A NEW SCOPE WITH A SPECIFIC NAME
        child_scope = Scope(self)
        self.CHILDREN[name]=child_scope
        return child_scope
    
    def GetChild(self,name:str):
    #RETURN A SCOPE WITH A NAME
        return self.CHILDREN[name]

    def Descend(self,Child:str, Ancestor:str)->bool:
        #Check if a type is the ancestor of the other
        aux=Child
        while(aux!='Object'):    
            if aux==Ancestor:
                return True
            if not aux in self.TYPE_HIERARCHY.keys():
                return False
            aux=self.TYPE_HIERARCHY[aux]
        return False
#----------------------------------------------------------------------------
    #CHECK RELATION BETWEEN TYPES AND PROTOCOLS
#----------------------------------------------------------------------------
    def Extends(self,Extension:str,Base:str)->bool:
        #Check if a protocol extends the other
        aux=Extension
        while(aux!=''):    
            if aux==Base:
                return True
            if not aux in self.PROTOCOL_EXTENSIONS.keys():
                return False
            aux=self.PROTOCOL_EXTENSIONS[aux]
        return False
    
    def TypeIsProtocol(self,type,protocol)->bool:
        
        #Getting all the functions that the type contains, including the inherit ones
        type_funcs=[]
        aux=type
        while aux!='Object':
            if aux not in self.TYPE_NAMES:
                return False
            type_funcs+=self.TYPE_FUNCTIONS[aux]
            aux=self.TYPE_HIERARCHY[aux]
        #Removing the types before adding the methods
        type_funcs=[(x.NAME,len(x.PARAMETERS)) for x in type_funcs]
        
        #Getting all the functions that the protocol contains, including the extensions
        protocol_funcs=[]
        aux=protocol
        while aux!='':
            if aux not in self.PROTOCOL_NAMES:
                return False        
            protocol_funcs+=self.PROTOCOL_FUNCT[aux]
            aux=self.PROTOCOL_EXTENSIONS[aux]
        #Removing the types before adding the methods
        protocol_funcs=[(x.NAME,len(x.PARAMETERS)) for x in protocol_funcs]

        #Checking if the type is the protocol
        return all([x in type_funcs for x in protocol_funcs])
    
    def AreRelated(self,Type1:str,Type2:str)->bool:
        #Go to parent
        if self.PARENT!=None:
            return self.PARENT.AreRelated(Type1,Type2)
        #if one is object, this is obviously related
        if Type1=='Object' or Type2=='Object':
            return True
        #Check if they are both types
        if Type1 in self.TYPE_NAMES and Type2 in self.TYPE_NAMES:
            return self.Descend(Type1,Type2) or self.Descend(Type2,Type1)
        #Check if they are both protocols
        if Type1 in self.PROTOCOL_NAMES and Type2 in self.PROTOCOL_NAMES:
            return self.Extends(Type1,Type2) or self.Extends(Type2,Type1)
        #else, one is a type and the other is a protocol
        Type=Type1 if Type1 in self.TYPE_NAMES else Type2
        Protocol= Type1 if  Type1 in self.PROTOCOL_NAMES else Type2
        return self.TypeIsProtocol(Type,Protocol)
    
    def CommonAncestor(self,type1:str,type2:str):
        Ancestors=set()
        aux=type1
        while aux!='':
            if aux not in self.TYPE_NAMES:
                return 'Object'
            Ancestors.add(aux)
            aux=self.TYPE_HIERARCHY[aux]
        aux=type2
        while aux!='Object':
            if aux in Ancestors:
                return aux
            aux=self.TYPE_HIERARCHY[aux]
        return 'Object'

    def LastCommonAncestor(self,Posibilitys:list[str]):
        #Empty list, return object
        if len(Posibilitys)==0:
            return 'Object'
        #Only one element: return that element
        if len(Posibilitys)==1:
            return Posibilitys[0]
        #With two elements, call the function above
        if len(Posibilitys)==2:
            self.CommonAncestor(Posibilitys[0],Posibilitys[1])
        #More than two elements, call the function above between the recursive calls
        Frist_Half_Common_Ancestor=self.LastCommonAncestor(Posibilitys[:len(Posibilitys)//2])
        Second_Half_Common_Ancestor=self.LastCommonAncestor(Posibilitys[len(Posibilitys)//2:])
        return self.CommonAncestor(Frist_Half_Common_Ancestor , Second_Half_Common_Ancestor)
#----------------------------------------------------------------------------