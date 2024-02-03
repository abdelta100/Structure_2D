import unittest
import pytest
from Core.StructureGlobal import StructureGlobal
from Core.Element import Element
from Core.Node import Node
from Core.Support import Support
from Core.Load import *
import numpy as np
from Core.Material import DefaultMaterial, TestMaterial
from Core.CrossSection import DefaultRectangularCrossSection, TestRectangularCrossSection
# TODO get familiar with pytest and write tests to check if code has broken when imporving later

def default_material_crossSection():
    mat=DefaultMaterial()
    cs=DefaultRectangularCrossSection()
    return mat, cs

@pytest.fixture
def single_bay_portal_frame():
    nodes: list[Node] = []
    nodes.append(Node(0, 0, 0))
    nodes.append(Node(0, 20, 1))
    nodes.append(Node(20, 20, 2))
    nodes.append(Node(20, 0, 3))


    elements: list[Element] = []
    elements.append(Element(nodes[0], nodes[1]))
    elements.append(Element(nodes[1], nodes[2]))
    elements.append(Element(nodes[2], nodes[3]))

    supports: list[Support] = []
    supports.append(Support.init_from_node(nodes[0], 0, support_type='fixed'))
    supports.append(Support.init_from_node(nodes[3], 1, support_type='fixed'))

    material, crossSection = default_material_crossSection()
    for element in elements:
        element.setMaterial(material)
        element.setCrossSection(crossSection)

    structure: StructureGlobal = StructureGlobal()
    structure.nodes = nodes
    structure.elements = elements
    structure.supports = supports
    return structure

def test_single_bay_portal_frame_Pointload_beam_center(single_bay_portal_frame):
    single_bay_portal_frame.reset(reset_type="hard")
    load = PointLoadMember(10, 10, -90)
    single_bay_portal_frame.elements[1].addLoad(load)
    single_bay_portal_frame.runAnalysis()
    support1 = single_bay_portal_frame.supports[0].reaction
    support2 = single_bay_portal_frame.supports[1].reaction
    assert support1.todict() == pytest.approx({'Fx': 1.243008079552516, 'Fy': 4.999999999999987, 'Mxy': -8.240107727366885})
    assert support2.todict() == pytest.approx({'Fx': -1.243008079552517, 'Fy': 4.999999999999988, 'Mxy': 8.240107727366896})

def test_single_bay_portal_frame_Momentload_beam_offcenter(single_bay_portal_frame):
    single_bay_portal_frame.reset(reset_type="hard")
    load=MomentMember(380, 4)
    single_bay_portal_frame.elements[1].addLoad(load)
    single_bay_portal_frame.runAnalysis()
    support1 = single_bay_portal_frame.supports[0].reaction
    support2 = single_bay_portal_frame.supports[1].reaction
    assert support1.todict() == pytest.approx({'Fx': -5.66811684275955, 'Fy': 18.770759403832397, 'Mxy': 35.28248527511893})
    assert support2.todict() == pytest.approx({'Fx': 5.6681168427594, 'Fy': -18.770759403832397, 'Mxy': -39.86729719846711})

def test_single_bay_portal_frame_UDL_beam_offcenter(single_bay_portal_frame):
    single_bay_portal_frame.reset(reset_type="hard")
    load=UniformDistributedLoad(10, 11, 16, angle=-50)
    single_bay_portal_frame.elements[1].addLoad(load)
    single_bay_portal_frame.runAnalysis()
    support1 = single_bay_portal_frame.supports[0].reaction
    support2 = single_bay_portal_frame.supports[1].reaction
    assert support1.todict() == pytest.approx({'Fx': -11.959642435874319, 'Fy': -1.5827130258580393, 'Mxy': 153.62734597753604})
    assert support2.todict() == pytest.approx({'Fx': -20.179738048447827, 'Fy': 39.88493518180685, 'Mxy': 208.54155917807805})

def test_single_bay_portal_frame_VDL_beam_offcenter(single_bay_portal_frame):
    single_bay_portal_frame.reset(reset_type="hard")
    load=VaryingDistributedLoad(10,3, 11, 16, angle=-110)
    single_bay_portal_frame.elements[1].addLoad(load)
    single_bay_portal_frame.runAnalysis()
    support1 = single_bay_portal_frame.supports[0].reaction
    support2 = single_bay_portal_frame.supports[1].reaction
    assert support1.todict() == pytest.approx({'Fx': 8.905105222023614, 'Fy': 15.093675714449418, 'Mxy': -88.35555455030911})
    assert support2.todict() == pytest.approx({'Fx': 2.210549436058705, 'Fy': 15.44633446109253, 'Mxy': -44.297941183165776})

def test_single_bay_portal_frame_Trapezoidal_beam_offcenter(single_bay_portal_frame):
    single_bay_portal_frame.reset(reset_type="hard")
    load=TrapezoidalDistributedLoad([2, 6, 13, 14],[10, 5, 8, 9], angle=110)
    single_bay_portal_frame.elements[1].addLoad(load)
    single_bay_portal_frame.runAnalysis()
    support1 = single_bay_portal_frame.supports[0].reaction
    support2 = single_bay_portal_frame.supports[1].reaction
    assert support1.todict() == pytest.approx({'Fx': 6.321940231171977, 'Fy': -35.34457397527611, 'Mxy': -114.32008945336591})
    assert support2.todict() == pytest.approx({'Fx': 22.407751808179512, 'Fy': -43.58960617074001, 'Mxy': -220.58153083418262})

if __name__ == '__main__':
    unittest.main()
