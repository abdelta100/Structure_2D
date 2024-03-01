from Core.CrossSection import *
from Core.Element import *
from Core.Node import Node
from Core.Load import *
from Core.Material import *
from Core.StructureGlobal import *
from Core.Support import *
from ElementHelperFunctions import ElementHelper as Helper

nodes: list[Node] = []
nodes.append(Node(x=0, y=0, idnum=0))
nodes.append(Node(x=0, y=10, idnum=1))
nodes.append(Node(x=10, y=10, idnum=2))

elements: list[GeneralFrameElement2D] = []
elements.append(FrameElement(i=nodes[0], j=nodes[1]))
elements.append(FrameElement(i=nodes[1], j=nodes[2]))

supports: list[Support] = []
supports.append(FixedSupport(node=nodes[0], support_num=0))

material2 = TestMaterial(E=200000000)
crossSection2 = TestRectangularCrossSection(A=0.25, I=0.035)

elements[0].setMaterial(material2)
elements[1].setCrossSection(crossSection2)

structure: StructureGlobal = StructureGlobal()
structure.nodes = nodes
structure.elements = elements
structure.supports = supports

elements[1].addLoad(UniformDistributedLoad(magnitude=10, start_location=2, end_location=7))
nodes[1].addLoad(PointLoad(magnitude=100, angle=0))

structure.runAnalysis()

print(structure.resultSummary())
Helper.plotInternals(elements[1])
