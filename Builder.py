from CrossSection import TestRectangularCrossSection
from Element import Element
from Load import *
from Material import TestMaterial
from Node import Node
from StructureGlobal import StructureGlobal
from Support import Support

# Create a Node List and assign node instances to it
nodes: list[Node] = []
# Node takes its x, y coords and user given idnum for init call
nodes.append(Node(0, 0, 0))
nodes.append(Node(0, 20, 1))
nodes.append(Node(20, 20, 2))
nodes.append(Node(20, 0, 3))

# Create a Node List and assign node instances to it
elements: list[Element] = []
# Element takes its i-node and j-node in init call, working on assigning material and section from init call too, \
# but uses default values for material and section at init
elements.append(Element(nodes[0], nodes[1]))
elements.append(Element(nodes[1], nodes[2]))
elements.append(Element(nodes[2], nodes[3]))

# Create custom materials and sections for use, or just let the defaults be.
# TestMaterial and Section  class used here to avoid calculation of section and material dims etc,
# in case results need to be checked by software
# You can use other material and section classes, init call can be found in Material.py and Section.py

mater = TestMaterial(E=2E11)
section = TestRectangularCrossSection(A=(0.05), I=(0.0001))

# Assigning material and section to element, you can assign different sections etc to different elements
for element in elements:
    element.setMaterial(mater)
    element.setCrossSection(section)

# Create a support list
supports: list[Support] = []
# Use static method from support class to create a support on a predefined node. Takes predefined node,
# user given support number (different from node.idnum), and support type string (of three types for now)
supports.append(Support.init_from_node(nodes[0], 0, support_type='fixed'))
supports.append(Support.init_from_node(nodes[3], 1, support_type='fixed'))

# Initilalize Structure Object and assign nodes, elements and supports to it
structure: StructureGlobal = StructureGlobal()
structure.nodes = nodes
structure.elements = elements
structure.supports = supports

# Create a Load List, not necessary for load application, you can addLoad directly to element via .addLoad() call
loads: list[StaticLoad] = []
# Each load class takes different input parameters, see documentation
loads.append(PointLoad(20, angle_degree=0))
loads.append(PointLoadMember(50, 10, angle=0))

# Assign Loads to either element or node via .addLoad call
elements[1].addLoad(loads[1])
# nodes[1].addLoad(loads[0])

# Run analysis
structure.runAnalysis()

# Print support reactions
print(supports[0].reactions)
print(supports[1].reactions)

# Further outputs to be refined
