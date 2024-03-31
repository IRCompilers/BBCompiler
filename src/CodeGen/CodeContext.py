from src.Common.IContext import IContext


class CodeContext(IContext):
    def __init__(self, parent: IContext = None):
        self.parent = parent
        self.variables = {}
        self.functions = {}
        self.types = {}
        self.puppetList={}

    def Puppet(self,value,action):
        if str(value) not in self.puppetList:
            self.puppetList[str(value)]=(value,-1)
        if action=='current':
            return self.puppetList[str(value)][0][self.puppetList[str(value)][1]]
        elif action=='next':
            self.puppetList[str(value)]=(self.puppetList[str(value)][0],self.puppetList[str(value)][1]+1)
            return len(self.puppetList[str(value)][0])>self.puppetList[str(value)][1]
        else:
            return len(self.puppetList[value][0])
        
    def def_variable(self,name,value):
        self.variables[name]=value

    def def_function(self,name,value):
        self.functions[name]=value

    def def_type(self,name,value):
        self.types[name]=value

    def has_variable(self, name: str) -> bool:
        return name in self.variables or (self.parent and self.parent.has_variable(name))

    def has_function(self, name: str, lookup=True) -> bool:
        return name in self.functions or (self.parent and self.parent.has_function(name) and lookup)

    def has_type(self, name: str) -> bool:
        return name in self.types or (self.parent and self.parent.has_type(name))

    def get_variable(self, name: str):
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get_variable(name)

        return None
    def edit_variable(self,name:str,value):
        if name in self.variables:
            self.variables[name]=value
        elif self.parent:
            self.parent.edit_variable(name,value)
        return None

    def get_function(self, name: str,LookUp=True):
        if name in self.functions:
            return self.functions[name]
        elif self.parent and LookUp:
            return self.parent.get_function(name)
        return None

    def get_type(self, name: str):
        if name in self.types:
            return self.types[name]
        elif self.parent:
            return self.parent.get_type(name)
        return None
    
    def remove_function(self,name):
        self.functions.pop(name)