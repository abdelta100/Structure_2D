from math import cos, sin

from Core.CrossSection import TestRectangularCrossSection
from Core.Element import Element
from Core.Load import *
from Core.Material import TestMaterial
from Core.Node import Node
from Core.StructureGlobal import StructureGlobal
from Core.Support import Support
from StructureGlobalHelperFunctions import StructureGlobalHelper

nodes: list[Node] = []
# TODO add a idnum verifier and corrector in structure global
nodes.append(Node(0, 0, 0))
nodes.append(Node(-5, 20, 1))
nodes.append(Node(0, 40, 2))
nodes.append(Node(20, 40, 3))
nodes.append(Node(25, 20, 4))
nodes.append(Node(20, 0, 5))
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
elements.append(Element(nodes[1], nodes[2]))
elements.append(Element(nodes[2], nodes[3]))
elements.append(Element(nodes[3], nodes[4]))
elements.append(Element(nodes[4], nodes[5]))
elements.append(Element(nodes[1], nodes[4]))
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
supports.append(Support.init_from_node(nodes[5], 1, support_type='fixed'))


structure: StructureGlobal = StructureGlobal()
# structure: StructureGlobalHighRes = StructureGlobalHighRes()
structure.nodes = nodes
structure.elements = elements
structure.supports = supports
# structure.subdivAllElements()

loads: list[StaticLoad] = []
loads.append(Moment(50))
loads.append(MomentMember(10, 5))
loads.append(PointLoadMember(8, 10, angle=-90))
loads.append(VaryingDistributedLoad(0.5*cos(degree2rad(20)), 1*cos(degree2rad(20)), 4, 14, angle=-90))
loads.append(VaryingDistributedLoad(5*sin(degree2rad(20)), 10*sin(degree2rad(20)), 4, 14, angle=0))
loads.append(VaryingDistributedLoad(0, 5, 4, 14, angle=-70))
loads.append(UniformDistributedLoad(500, 4, 14, angle=-90))
loads.append(TrapezoidalDistributedLoad([5, 13, 20], [0.13, 0.28, 0.28], angle=-90))
loads.append(PointLoad(100000, 0))
loads.append(VaryingDistributedLoad(10, 17, 3, 9, angle=-90))
loads.append(PointLoadMember(29, 24, angle=-90))

#TODO error when running following line check
# nodes[1].addLoad(loads[0])
elements[2].addLoad(loads[9])
elements[5].addLoad(loads[10])
# nodes[1].addLoad(loads[-1])

# structure.subdivAllElements()
structure.runAnalysis()
print(structure.modelSummary())
# x, y = elements[1].calcBendingMomentDiagram()
spr=StructureGlobalHelper
spr.graphNodalDisplacementGraph(structure=structure)


# TODO there IS an error in transferring reactionary forces or whatever  at nodes post analysis


# TODO add a function that prints model summary, maybe use __repr__ or something for individual elements
# TODO n order analysis
# TODO add section rotation capability and 1-axis 2-axis Moment of Inertia
# TODO do something about dof in structure and dof avaialable in principleforce/displacement 2D classes
# TODO add an interface for member vs point loads idk, problem in element.addLoad() if you accidentally add eg a PointLoad
# instead of a pointloadmember