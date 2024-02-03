import unittest
import pytest
from Core.StructureGlobal import StructureGlobal
from Core.Element import GeneralFrameElement2D
from Core.Node import Node
from Core.Support import Support
from Core.Load import *
import numpy as np
from Core.Material import DefaultMaterial, TestMaterial
from Core.CrossSection import DefaultRectangularCrossSection, TestRectangularCrossSection


# TODO get familiar with pytest and write tests to check if code has broken when imporving later

def SAP2000_material_crossSection():
    # SAP2000 Section and material
    mat = TestMaterial(E=4176000)
    cs = TestRectangularCrossSection(A=(0.0625), I=(3.255E-4))
    return mat, cs # add assertion here

@pytest.fixture
def single_bay_double_story_portal_frame():
    nodes: list[Node] = []
    nodes.append(Node(0, 0, 0))
    nodes.append(Node(-5, 20, 1))
    nodes.append(Node(0, 40, 2))
    nodes.append(Node(20, 40, 3))
    nodes.append(Node(25, 20, 4))
    nodes.append(Node(20, 0, 5))

    elements: list[GeneralFrameElement2D] = []
    elements.append(GeneralFrameElement2D(nodes[0], nodes[1]))
    elements.append(GeneralFrameElement2D(nodes[1], nodes[2]))
    elements.append(GeneralFrameElement2D(nodes[2], nodes[3]))
    elements.append(GeneralFrameElement2D(nodes[3], nodes[4]))
    elements.append(GeneralFrameElement2D(nodes[4], nodes[5]))
    elements.append(GeneralFrameElement2D(nodes[1], nodes[4]))

    material, crossSection = SAP2000_material_crossSection()
    for element in elements:
        element.setMaterial(material)
        element.setCrossSection(crossSection)

    supports: list[Support] = []
    supports.append(Support.init_from_node(nodes[0], 0, support_type='Fixed'))
    supports.append(Support.init_from_node(nodes[5], 1, support_type='fixed'))

    structure: StructureGlobal = StructureGlobal()
    structure.nodes = nodes
    structure.elements = elements
    structure.supports = supports

    return structure

def test_single_bay_double_story_portal_frame_VDL_PointLoad(single_bay_double_story_portal_frame):
    single_bay_double_story_portal_frame.reset(reset_type="hard")

    loads: list[StaticLoad] = []
    loads.append(VaryingDistributedLoad(10, 17, 3, 9, angle=-90))
    loads.append(PointLoadMember(29, 24, angle=-90))

    single_bay_double_story_portal_frame.elements[2].addLoad(loads[0])
    single_bay_double_story_portal_frame.elements[5].addLoad(loads[1])

    single_bay_double_story_portal_frame.runAnalysis()
    support1 = single_bay_double_story_portal_frame.supports[0].reaction
    support2 = single_bay_double_story_portal_frame.supports[1].reaction
    assert support1.todict() == pytest.approx(
        {'Fx': -13.259447606984395, 'Fy': 56.585910298752424, 'Mxy': -8.430530353319025})
    assert support2.todict() == pytest.approx(
        {'Fx': 13.259447610816576, 'Fy': 53.41408970121938, 'Mxy': -1.8512638218827995})

if __name__ == '__main__':
    unittest.main()
