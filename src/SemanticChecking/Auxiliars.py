from Common.ASTNodes import *
from SemanticChecking.Scope import Scope

def EqualObjects(names):
    return len(names)!=len(set(names))

def AddBasicInfo(scope:Scope):
    scope.AddProtocolFunctions('Iterable',[
                ProtocolMethodNode('next',[],'Boolean'),
                ProtocolMethodNode('current',[],'Object')
    ])
    scope.AddProtocolFunctions('Comparable',[
                ProtocolMethodNode('CompareTo',[ParameterNode('element')],'Number')
    ])
    scope.AddProtocolFunctions('Printable',[
                ProtocolMethodNode('ToString',[],'String')
    ])
    
    scope.AddTypeFunctions('Object',[])
    scope.AddTypeFunctions('Boolean',[])
    scope.AddTypeFunctions('String',[FunctionNode('ToString',[],None,'String')])
    scope.AddTypeFunctions('Number',[FunctionNode('ToString',[],None,'String'),
                FunctionNode('CompareTo',[ParameterNode('element','Number')],None,'Object')])
    scope.AddTypeFunctions('Vector', [FunctionNode('next',[],None,'Boolean'),
                FunctionNode('current',[],None,'Object')])
    
    scope.AddTypeParameters('Object',[])
    scope.AddTypeParameters('Number',[])
    scope.AddTypeParameters('Boolean',[])
    scope.AddTypeParameters('String',[])
    scope.AddTypeParameters('Vector',[])

    scope.AddFunctions(ProtocolMethodNode('sen',[ParameterNode('a','Number')],'Number'))
    scope.AddFunctions(ProtocolMethodNode('cos',[ParameterNode('a','Number')],'Number'))
    scope.AddFunctions(ProtocolMethodNode('exp',[ParameterNode('a','Number')],'Number'))
    scope.AddFunctions(ProtocolMethodNode('sqrt',[ParameterNode('a','Number')],'Number'))
    scope.AddFunctions(ProtocolMethodNode('rand',[],'Number'))
    scope.AddFunctions(ProtocolMethodNode('log',[ParameterNode('a','Number'),ParameterNode('a','Number')],'Number'))
    scope.AddFunctions(ProtocolMethodNode('print',[ParameterNode('a','Printeable')],'String'))

def GetTopologicOrder(Graph:dict[str,str])->tuple[list[str],bool]:
    colors=dict()
    order=dict()
    count=0
    for key in Graph.keys():
        colors[key]='white'
    for key in Graph.keys():
        try:
            AllOK=DFS(Graph,key,colors,order,count)
            if not AllOK:
                return (Graph.keys(),False)
            count=order[key]+1
        except:
            return (Graph.keys(),False)
    sortedlist=list(map(lambda x:(order[x],x),Graph.keys()))
    sortedlist.sort(key=lambda x:x[0])
    return (list(map(lambda x:x[1],sortedlist)),True)

def DFS(Graph,key,colors,order,count):
    if colors[key]=='black':
        return True
    if colors[key]=='grey':
        return False
    if Graph[key]=='':
        colors[key]='black'
        order[key]=count
        return True    
    else:
        colors[key]='grey'
        if not DFS(Graph,Graph[key],colors,order,count):
            return False
        colors[key]='black'
        order[key]=count
        count+=1

        return True