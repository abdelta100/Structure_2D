import numpy as np
import matplotlib.pyplot as plt

from CrossSection import TestRectangularCrossSection
from Element import Element
from Load import *
from Material import TestMaterial
from Node import Node
from StructureGlobal import StructureGlobal
from Support import Support

nodes: list[Node] = []
# TODO add a idnum verifier and corrector in structure global
nodes.append(Node(0, 0, 0))
nodes.append(Node(0, 20, 1))
nodes.append(Node(20, 20, 2))
nodes.append(Node(20, 0, 3))

# mater=NewMaterial(name="Custom", density=2000, elastic_mod=200000000, poisson_ratio=.33,comp_strength=3000)
mater = TestMaterial(E=449570.7)
section = TestRectangularCrossSection(A=(0.0625), I=(3.255E-4))

elements: list[Element] = []
# TODO building element is cumbersome because of secondary addition of nodes
elements.append(Element(nodes[0], nodes[1]))
elements.append(Element(nodes[1], nodes[2]))
elements.append(Element(nodes[2], nodes[3]))

for element in elements:
    element.setMaterial(mater)
    element.setCrossSection(section)

supports: list[Support] = []
supports.append(Support.init_from_node(nodes[0], 0))
supports.append(Support.init_from_node(nodes[3], 1))


structure: StructureGlobal = StructureGlobal()
structure.nodes = nodes
structure.elements = elements
structure.supports = supports

loads: list[Load] = []
#loads.append(PointLoad(10, -90))
loads.append(PointLoadMember(-100, 5))
loads.append(VaryingDistributedLoad(-28, -13, 7, 15))
loads.append(UniformDistributedLoad(-28, 0, 3))
loads.append(TrapezoidalDistributedLoad([5, 13, 20], [-13, -28, -28]))
#nodes[1].addLoad(loads[0])
elements[1].addLoad(loads[2])
elements[1].addLoad(loads[3])


structure.runAnalysis()
print(nodes[0].disp)
print(nodes[3].disp)
print(nodes[2].netLoad)
print(supports[0].reactions)
print(supports[1].reactions)
x, y=elements[1].showForceDiagram()
plt.plot(x, y)
plt.plot([0, elements[1].length], [0,0])
plt.show()

# TODO solve bug when force appplied at node. Re Farhan Chat. Fixed but not yet removed todo.
# TODO Fix FEM directions, needs to be opposite applied load, and the directions need to be reversed again when
#  transferring to nodes


