import unittest
import pytest
from StructureGlobal import StructureGlobal
from Element import Element
from Node import Node
from Support import Support
from Load import *
import numpy as np
# TODO get familiar with pytest and write tests to check if code has broken when imporving later

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

    structure: StructureGlobal = StructureGlobal()
    structure.nodes = nodes
    structure.elements = elements
    structure.supports = supports
    return structure

def test_single_bay_portal_frame_point_load_top_center(single_bay_portal_frame):
    load=PointLoadMember(10, 10, -90)
    single_bay_portal_frame.elements[1].addLoad(load)
    single_bay_portal_frame.runAnalysis()
    support1 = single_bay_portal_frame.supports[0].reaction
    support2 = single_bay_portal_frame.supports[1].reaction
    assert support1.todict() == pytest.approx({'Fx': 1.243008079552516, 'Fy': 4.999999999999987, 'Mxy': -8.240107727366885})
    assert support2.todict() == pytest.approx({'Fx': -1.243008079552517, 'Fy': 4.999999999999988, 'Mxy': 8.240107727366896})


if __name__ == '__main__':
    unittest.main()
