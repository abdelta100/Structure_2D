from math import cos, sin

import matplotlib.pyplot as plt

from CrossSection import TestRectangularCrossSection
from Element import Element
from Load import *
from Material import TestMaterial, DefaultMaterial
from Node import Node
from StructureGlobal import StructureGlobal
from StructureGlobalHighRes import StructureGlobalHighRes
from Support import Support, FixedSupport
from StructureGlobalHelperFunctions import StructureGlobalHelper

nodes: list[Node] = []
# TODO add a idnum verifier and corrector in structure global
nodes.append(Node(0, 0, 0))
nodes.append(Node(20, 0, 1))
# nodes.append(Node(0, 20, 2))
# nodes.append(Node(20, 20, 3))
# nodes.append(Node(20, 10, 4))
# nodes.append(Node(20, 0, 5))
# nodes.append(Node(0, 60, 6))
# nodes.append(Node(20, 60, 7))
# nodes.append(Node(0, 80, 8))
# nodes.append(Node(20, 80, 9))
# nodes.append(Node(0, 100, 10))
# nodes.append(Node(10, 100, 11))
# nodes.append(Node(20, 100, 12))

# mater=NewMaterial(name="Custom", density=2000, elastic_mod=200000000, poisson_ratio=.33,comp_strength=3000)
mater = TestMaterial(E=4176000)
section = TestRectangularCrossSection(A=(0.0625), I=(3.255E-4))

elements: list[Element] = []
#TODO add a kwarg or something for direct assigning material and section in instance call
elements.append(Element(nodes[0], nodes[1]))
# elements.append(Element(nodes[1], nodes[2]))
# elements.append(Element(nodes[2], nodes[3]))
# elements.append(Element(nodes[3], nodes[4]))
# elements.append(Element(nodes[4], nodes[5]))
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


for element in elements:
    element.setMaterial(mater)
    element.setCrossSection(section)

supports: list[Support] = []
supports.append(Support.init_from_node(nodes[0], 0, support_type='Fixed'))
# supports.append(FixedSupport(nodes[0], 0))
supports.append(Support.init_from_node(nodes[1], 1, support_type='fixed'))


structure: StructureGlobal = StructureGlobal()
# structure: StructureGlobalHighRes = StructureGlobalHighRes()
structure.nodes = nodes
structure.elements = elements
structure.supports = supports
# structure.subdivAllElements()

loads: list[StaticLoad] = []
loads.append(Moment(50))
loads.append(MomentMember(124, 10))
loads.append(PointLoadMember(8, 10, angle=-90))
loads.append(VaryingDistributedLoad(0.5*cos(degree2rad(20)), 1*cos(degree2rad(20)), 4, 14, angle=-90))
loads.append(VaryingDistributedLoad(5*sin(degree2rad(20)), 10*sin(degree2rad(20)), 4, 14, angle=0))
loads.append(VaryingDistributedLoad(0, 5, 4, 14, angle=-70))
loads.append(UniformDistributedLoad(500, 4, 14, angle=-90))
loads.append(TrapezoidalDistributedLoad([5, 13, 20], [0.13, 0.28, 0.28], angle=-90))
loads.append(PointLoad(100000, 0))

#TODO error when running following line check
# nodes[1].addLoad(loads[0])
elements[0].addLoad(loads[6])
# nodes[1].addLoad(loads[-1])

# structure.subdivAllElements()
structure.runAnalysis()
print(nodes[1].disp)
# print(nodes[18].disp)
print(nodes[1].netLoad)
print(supports[0].reaction)
print(supports[1].reaction)
# x, y = elements[1].calcBendingMomentDiagram()
spr=StructureGlobalHelper
spr.graphNodalDisplacementGraph(structure=structure)


# TODO there IS an error in transferring reactionary forces or whatever  at nodes post analysis


# TODO add a function that prints model summary, maybe use __repr__ or something for individual elements
# TODO n order analysis
# TODO add section rotation capability and 1-axis 2-axis Moment of Inertia
# TODO Big probelm regarding MOMENTS AND DIRECTIONS etc