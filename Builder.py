from Element import Element
from Load import *
from Node import Node
from StructureGlobal import StructureGlobal
from Support import Support

nodes: list[Node] = []
# TODO add a idnum verifier and corrector in structure global
nodes.append(Node(0, 0, 0))
nodes.append(Node(0, 10, 1))
nodes.append(Node(10, 10, 2))
nodes.append(Node(10, 0, 3))

elements: list[Element] = []
# TODO building element is cumbersome because of secondary addition of nodes
elements.append(Element(nodes[0], nodes[1]))
elements.append(Element(nodes[1], nodes[2]))
elements.append(Element(nodes[2], nodes[3]))


supports: list[Support] = []
supports.append(Support.init_from_node(nodes[0], 0))
supports.append(Support.init_from_node(nodes[3], 1))
#supports.append(Support.init_from_node(nodes[3], 1))

structure: StructureGlobal = StructureGlobal()
structure.nodes = nodes
structure.elements = elements
structure.supports = supports

loads:list[Load]=[]
loads.append(PointLoad(40, 270))
nodes[1].addLoad(loads[0])

#structure.createGlobalStiffnessMatrix()
#print(structure.stiffnessMatrix)
structure.solver()
print(nodes[0].disp)
print(nodes[3].disp)
print(nodes[1].netLoad)
print(supports[0].reactions)
print(supports[1].reactions)
