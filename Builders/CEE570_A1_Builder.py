from Core.CrossSection import *
from Core.Element import *
from Core.Node import Node
from Core.Load import *
from Core.Material import *
from Core.StructureGlobal import *
from Core.Support import *
from ElementHelperFunctions import ElementHelper as Helper
from math import *
from StructureGlobalHelperFunctions import StructureGlobalHelper


# Problem 1-A
# nodes: list[Node] = []
# nodes.append(Node(x=0, y=0, idnum=0))
# nodes.append(Node(x=0, y=4, idnum=1))
# nodes.append(Node(x=2*sqrt(2), y=2*sqrt(2), idnum=2))
# nodes.append(Node(x=4, y=0, idnum=3))
#
# elements: list[TrussElement] = []
# elements.append(TrussElement(i=nodes[0], j=nodes[1]))
# elements.append(TrussElement(i=nodes[0], j=nodes[2]))
# elements.append(TrussElement(i=nodes[0], j=nodes[3]))
#
# supports: list[Support] = []
# supports.append(PinnedSupport(node=nodes[1], support_num=0))
# supports.append(PinnedSupport(node=nodes[2], support_num=1))
# supports.append(PinnedSupport(node=nodes[3], support_num=2))

# Problem 1-B
nodes: list[Node] = []
nodes.append(Node(x=0, y=0, idnum=0))
nodes.append(Node(x=-3, y=0, idnum=1))
nodes.append(Node(x=0, y=1.5, idnum=2))
nodes.append(Node(x=-5*cos(60), y=-5*sin(60), idnum=3))

elements: list[TrussElement] = []
elements.append(TrussElement(i=nodes[0], j=nodes[1]))
elements.append(TrussElement(i=nodes[0], j=nodes[2]))
elements.append(TrussElement(i=nodes[0], j=nodes[3]))

supports: list[Support] = []
supports.append(PinnedSupport(node=nodes[1], support_num=0))
supports.append(PinnedSupport(node=nodes[2], support_num=1))
supports.append(PinnedSupport(node=nodes[3], support_num=2))

material2 = TestMaterial(E=200000000000)
crossSection2 = TestRectangularCrossSection(A=0.01, I=0.035)

for element in elements:
    element.setMaterial(material2)
    element.setCrossSection(crossSection2)

structure: StructureGlobal = StructureGlobal()
structure.nodes = nodes
structure.elements = elements
structure.supports = supports

# elements[1].addLoad(UniformDistributedLoad(magnitude=10, start_location=2, end_location=7))
# Problem 1-A
# nodes[0].addLoad(PointLoad(magnitude=20000, angle=180))
# nodes[0].addLoad(PointLoad(magnitude=15000, angle=270))

# Problem 1-B
structure.runAnalysis()
nodes[0].addLoad(PointLoad(magnitude=30000, angle=270))

print(structure.resultSummary())
Helper.plotInternals(elements[1])
StructureGlobalHelper.graphNodalDisplacementGraph(structure)

print(structure.stiffnessMatrix)