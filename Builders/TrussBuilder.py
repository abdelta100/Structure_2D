from Core.CrossSection import TestRectangularCrossSection
from Core.Element import GeneralFrameElement2D, TrussElement
from Core.Load import *
from Core.Material import TestMaterial
from Core.Node import Node
from Core.StructureGlobal import StructureGlobal
from StructureGlobalHelperFunctions import StructureGlobalHelper
from Core.Support import Support
from StructureGlobalHighRes import StructureGlobalHighRes

# Create a Node List and assign node instances to it
nodes: list[Node] = []
# Node takes its x, y coords and user given idnum for init call
nodes.append(Node(0, 0, 0))
nodes.append(Node(10, 10, 1))
nodes.append(Node(20, 0, 2))
nodes.append(Node(30, 10, 3))
nodes.append(Node(40, 0, 4))

# Create a Node List and assign node instances to it
elements: list[GeneralFrameElement2D] = []
# Element takes its i-node and j-node in init call, working on assigning material and section from init call too, \
# but uses default values for material and section at init
elements.append(TrussElement(nodes[0], nodes[1]))
elements.append(TrussElement(nodes[1], nodes[2]))
elements.append(TrussElement(nodes[2], nodes[3]))
elements.append(TrussElement(nodes[3], nodes[4]))
elements.append(TrussElement(nodes[1], nodes[3]))
elements.append(TrussElement(nodes[0], nodes[2]))
elements.append(TrussElement(nodes[2], nodes[4]))


# Create custom materials and sections for use, or just let the defaults be.
# TestMaterial and Section  class used here to avoid calculation of section and material dims etc.,
# in case results need to be checked by software
# You can use other material and section classes, init call can be found in Material.py and Section.py

mater = TestMaterial(E=2E11)
section = TestRectangularCrossSection(A=(0.05), I=(0.0001))

# Assigning material and section to element, you can assign different sections etc. to different elements
# for element in elements:
#     element.setMaterial(mater)
#     element.setCrossSection(section)

# Create a support list
supports: list[Support] = []
# Use static method from support class to create a support on a predefined node. Takes predefined node,
# user given support number (different from node.idnum), and support type string (of three types for now)
supports.append(Support.init_from_node(nodes[0], 0, support_type='pin'))
supports.append(Support.init_from_node(nodes[4], 1, support_type='pin'))

# Initilalize Structure Object and assign nodes, elements and supports to it
structure: StructureGlobal = StructureGlobal()
structure.nodes = nodes
structure.elements = elements
structure.supports = supports

# structure: StructureGlobalHighRes = StructureGlobalHighRes()
# structure.nodes = nodes
# structure.elements = elements
# structure.supports = supports

# Create a Load List, not necessary for load application, you can addLoad directly to element via .addLoad() call
loads: list[StaticLoad] = []
# Each load class takes different input parameters, see documentation
loads.append(Moment(20))
loads.append(PointLoadMember(10, 8, angle=-90))
loads.append(UniformDistributedLoad(10000, 0, 20, -90))

# Assign Loads to either element or node via .addLoad call
# elements[5].addLoad(loads[2])
# elements[3].addLoad(loads[3])
# nodes[1].addLoad(loads[0])

# Run analysis
# structure.useSelfWeight()
structure.runAnalysis()

# Print support reactions
print(structure.modelSummary())

spr=StructureGlobalHelper
spr.graphNodalDisplacementGraph(structure=structure)

# Problem when applying moment load to node