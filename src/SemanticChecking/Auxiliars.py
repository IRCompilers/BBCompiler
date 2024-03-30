from src.Common.ASTNodes import *
from src.SemanticChecking.Scope import Scope


def EqualObjects(names):
    return len(names) != len(set(names))


def AddBasicInfo(scope: Scope):
    scope.AddProtocolFunctions('Iterable', [
        ProtocolMethodNode('next', [], 'Boolean'),
        ProtocolMethodNode('current', [], 'Object')
    ])
    scope.AddProtocolFunctions('Comparable', [
        ProtocolMethodNode('CompareTo', [ParameterNode('element')], 'Number')
    ])
    scope.AddProtocolFunctions('Printable', [
        ProtocolMethodNode('ToString', [], 'String')
    ])

    scope.AddTypeFunctions('Object', [])
    scope.AddTypeFunctions('Boolean', [])
    scope.AddTypeFunctions('String', [FunctionNode('ToString', [], None, 'String')])
    scope.AddTypeFunctions('Number', [FunctionNode('ToString', [], None, 'String'),
                                      FunctionNode('CompareTo', [ParameterNode('element', 'Number')], None, 'Object')])
    scope.AddTypeFunctions('Vector', [FunctionNode('next', [], None, 'Boolean'),
                                      FunctionNode('current', [], None, 'Object'),
                                      FunctionNode('size', [], None, 'Number')])

    scope.AddTypeParameters('Object', [])
    scope.AddTypeParameters('Number', [])
    scope.AddTypeParameters('Boolean', [])
    scope.AddTypeParameters('String', [])
    scope.AddTypeParameters('Vector', [])

    scope.AddFunctions(ProtocolMethodNode('sen', [ParameterNode('a', 'Number')], 'Number'))
    scope.AddFunctions(ProtocolMethodNode('cos', [ParameterNode('a', 'Number')], 'Number'))
    scope.AddFunctions(ProtocolMethodNode('exp', [ParameterNode('a', 'Number')], 'Number'))
    scope.AddFunctions(ProtocolMethodNode('sqrt', [ParameterNode('a', 'Number')], 'Number'))
    scope.AddFunctions(ProtocolMethodNode('rand', [], 'Number'))
    scope.AddFunctions(
        ProtocolMethodNode('log', [ParameterNode('a', 'Number'), ParameterNode('a', 'Number')], 'Number'))
    scope.AddFunctions(ProtocolMethodNode('print', [ParameterNode('a', 'Printable')], 'Object'))
    scope.AddFunctions(
        ProtocolMethodNode('range', [ParameterNode('a', 'Number'), ParameterNode('b', 'Number')], 'Vector'))


def GetTopologicOrder(Graph: dict[str, str]) -> tuple[list[str], bool]:
    colors = dict()
    order = dict()
    count = 0
    for key in Graph.keys():
        colors[key] = 'white'
    for key in Graph.keys():
        Error = DFS(Graph, key, colors, order, count)
        if Error!=None:
            return (Graph.keys(), Error)
        count = order[key] + 1
    sortedlist = list(map(lambda x: (order[x], x), Graph.keys()))
    sortedlist.sort(key=lambda x: x[0])
    return (list(map(lambda x: x[1], sortedlist)), None)


def DFS(Graph:dict, key, colors, order, count):
    if colors[key] == 'black':
        return None
    if colors[key] == 'grey':
        return (key,Graph[key])
    if Graph[key] == '':
        colors[key] = 'black'
        order[key] = count
        return None
    elif Graph[key] not in Graph.keys():
        return (Graph[key],)
    else:
        colors[key] = 'grey'
        error= DFS(Graph, Graph[key], colors, order, count)
        if error!=None:
            return error
        colors[key] = 'black'
        order[key] = count
        count += 1

        return None