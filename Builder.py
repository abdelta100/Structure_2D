import matplotlib.pyplot as plt

from CrossSection import TestRectangularCrossSection
from Element import Element
from Load import *
from Material import TestMaterial
from Node import Node
from StructureGlobal import StructureGlobal
from Support import Support
from StructureGlobalHelperFunctions import StructureGlobalHelper

nodes: list[Node] = []
# TODO add a idnum verifier and corrector in structure global
nodes.append(Node(0, 0, 0))
nodes.append(Node(0, 20, 1))
nodes.append(Node(20, 20, 2))
nodes.append(Node(20, 0, 3))
# nodes.append(Node(0, 40, 4))
# nodes.append(Node(20, 40, 5))
# nodes.append(Node(0, 60, 6))
# nodes.append(Node(20, 60, 7))
# nodes.append(Node(0, 80, 8))
# nodes.append(Node(20, 80, 9))
# nodes.append(Node(0, 100, 10))
# nodes.append(Node(10, 100, 11))
# nodes.append(Node(20, 100, 12))

# mater=NewMaterial(name="Custom", density=2000, elastic_mod=200000000, poisson_ratio=.33,comp_strength=3000)
mater = TestMaterial(E=449570.7)
section = TestRectangularCrossSection(A=(0.0625), I=(3.255E-4))

elements: list[Element] = []
elements.append(Element(nodes[0], nodes[1]))
elements.append(Element(nodes[1], nodes[2]))
elements.append(Element(nodes[2], nodes[3]))
# elements.append(Element(nodes[1], nodes[4]))
# elements.append(Element(nodes[4], nodes[5]))
# elements.append(Element(nodes[5], nodes[2]))
# elements.append(Element(nodes[4], nodes[6]))
# elements.append(Element(nodes[6], nodes[7]))
# elements.append(Element(nodes[7], nodes[5]))
# elements.append(Element(nodes[6], nodes[8]))
# elements.append(Element(nodes[8], nodes[9]))
# elements.append(Element(nodes[9], nodes[7]))
# elements.append(Element(nodes[8], nodes[10]))
# elements.append(Element(nodes[10], nodes[11]))
# elements.append(Element(nodes[11], nodes[12]))
# elements.append(Element(nodes[12], nodes[9]))


#for element in elements:
#    element.setMaterial(mater)
#    element.setCrossSection(section)

supports: list[Support] = []
supports.append(Support.init_from_node(nodes[0], 0, support_type='Fixed'))
supports.append(Support.init_from_node(nodes[3], 1, support_type='fixed'))

structure: StructureGlobal = StructureGlobal()
structure.nodes = nodes
structure.elements = elements
structure.supports = supports

loads: list[StaticLoad] = []
loads.append(MomentMember(124, 10))
loads.append(PointLoadMember(100, 13, angle=0))
loads.append(VaryingDistributedLoad(3, 17, 1, 14, angle=-90))
loads.append(UniformDistributedLoad(10, 8, 17, angle=-90))
loads.append(TrapezoidalDistributedLoad([5, 13, 20], [13, 28, 28], angle=-90))
loads.append(PointLoad(1000, -90))

#TODO error when running following line check
elements[1].addLoad(loads[0])
# nodes[11].addLoad(loads[4])

structure.runAnalysis()
print(nodes[0].disp)
# print(nodes[3].disp)
print(nodes[2].netLoad)
print(supports[0].reactions)
print(supports[1].reactions)
x, y = elements[1].calcBendingMomentDiagram()

allElemDisp=StructureGlobalHelper.plotNodalDisplacementGraph(structure)
# print(allElemDisp)
for element in allElemDisp:
    plt.plot(element[0], element[1], '-b')
#plt.plot(x, y)
#plt.plot([0, elements[1].length], [0, 0])
plt.show()

# TODO Fix FEM directions, needs to be opposite applied load, and the directions need to be reversed again when
#  transferring to nodes
# TODO there IS an error in transferring reactionary forces or whatever  at nodes post analysis


# TODO add a function that prints model summary, maybe use __repr__ or something for individual elements
# TODO n order analysis