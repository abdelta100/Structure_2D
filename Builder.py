from CrossSection import RectangularCrossSection, TestRectangularCrossSection
from Element import Element
from Load import *
from Material import Material, NewMaterial, TestMaterial
from Node import Node
from StructureGlobal import StructureGlobal
from Support import Support

nodes: list[Node] = []
# TODO add a idnum verifier and corrector in structure global
nodes.append(Node(0, 0, 0))
nodes.append(Node(0, 10, 1))
nodes.append(Node(10, 10, 2))
nodes.append(Node(10, 0, 3))

#mater=NewMaterial(name="Custom", density=2000, elastic_mod=200000000, poisson_ratio=.33,comp_strength=3000)
#mater = TestMaterial(E=200000000)
#section = TestRectangularCrossSection(A=0.05, I=0.0001)

elements: list[Element] = []
# TODO building element is cumbersome because of secondary addition of nodes
elements.append(Element(nodes[0], nodes[1]))
elements.append(Element(nodes[1], nodes[2]))
elements.append(Element(nodes[2], nodes[3]))

# for element in elements:
#     element.setMaterial(mater)
#     element.setCrossSection(section)

supports: list[Support] = []
supports.append(Support.init_from_node(nodes[0], 0))
supports.append(Support.init_from_node(nodes[3], 1))
#supports.append(Support.init_from_node(nodes[3], 1))

structure: StructureGlobal = StructureGlobal()
structure.nodes = nodes
structure.elements = elements
structure.supports = supports

loads:list[Load]=[]
#loads.append(PointLoad(40, 270))
loads.append(PointLoadMember(40, 5))
#nodes[1].addLoad(loads[0])
elements[1].addLoad(loads[0])

#structure.createGlobalStiffnessMatrix()
#print(structure.stiffnessMatrix)
structure.solver()
print(nodes[0].disp)
print(nodes[3].disp)
print(nodes[1].netLoad)
print(supports[0].reactions)
print(supports[1].reactions)

#TODO solve bug when force appplied at node. Re Farhan Chat