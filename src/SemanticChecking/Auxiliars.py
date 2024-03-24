from Common.ASTNodes import *
from SemanticChecking.Scope import Scope

def NotEqualObjects(names):
    return len(names)!=len(set(names))

def AddBasicInfo(scope:Scope):
    scope.AddProtocolFunctions('Iterable',[
                FunctionNode('next',[],'Boolean'),
                FunctionNode('current',[],'Object')
    ])
    scope.AddTypeFunctions('Object',[])
    scope.AddTypeFunctions('Number',[])
    scope.AddTypeFunctions('Boolean',[])
    scope.AddTypeFunctions('Vector',[
                FunctionNode('next',[],'Boolean'),
                FunctionNode('current',[],'Object')
    ])
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
    scope.AddFunctions(ProtocolMethodNode('print',[ParameterNode('a','Object')],'Object'))

def GetTopologicOrder(Graph:dict[str,str])->tuple[list[str],bool]:
    colors=dict()
    order=dict()
    count=0
    for key in Graph.keys():
        colors[key]='white'
    for key in Graph.keys():
        AllOK=DFS(Graph,key,colors,order,count)
        if not AllOK:
            return (Graph.keys(),False)
        count=order[key]+1
    sortedlist=list[map(lambda x:(order[x],x),Graph.keys())].sort()
    return (list[map(lambda x:x[1],sortedlist)],True)

def DFS(Graph,key,colors,order,count):
    if Graph[key]=='black':
        return True
    if Graph[key]=='grey':
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