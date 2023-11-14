from Element import Element
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
supports.append(Support.init_from_node(nodes[3], 0))

structure: StructureGlobal = StructureGlobal()
structure.nodes = nodes
structure.elements = elements
structure.supports = supports

structure.createGlobalStiffnessMatrix()
print(structure.stiffnessMatrix)
