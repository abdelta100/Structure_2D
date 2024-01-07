import math

from Element import Element
from ElementHelperFunctions import ElementHelper
from Node import Node
from StructureGlobal import StructureGlobal


class StructureGlobalHighRes(StructureGlobal):
    def __init__(self):
        super().__init__()
        self.res = 1  # unit resolution

    def subdivAllElements(self):
        subElems: list[Element] = []
        for element in self.elements:
            tempElems, tempNodes = self.subdivSingleElem(element)
            self.addSubNodes(tempNodes)
            for elm in tempElems: subElems.append(elm)

        self.elements = subElems

    def subdivSingleElem(self, element):
        numElems = int(element.length) + 1
        subElems, subNodes = self.subdivElem(element, numElems)
        return subElems, subNodes

    def subdivElem(self, element, numElems):
        # TODO load application not split yet
        baseNodeNum = self.nodes[-1].idnum
        angle = element.getAngle()
        subElems: list[Element] = []
        subNodes: list[Node] = []
        subLength = element.length / numElems
        first_node = element.i_Node
        dx = element.j_Node.x - element.i_Node.x
        dy = element.j_Node.y - element.i_Node.y
        for i in range(numElems - 1):
            second_node = Node(first_node.x + subLength * math.cos(angle), first_node.y + subLength * math.sin(angle),
                               baseNodeNum + 1)
            new_elem = ElementHelper.copyElementPropertiesSansNodes(element)
            new_elem.i_Node = first_node
            new_elem.j_Node = second_node
            subElems.append(new_elem)
            subNodes.append(second_node)
            first_node = second_node
            baseNodeNum += 1
        lastElem = ElementHelper.copyElementPropertiesSansNodes(element)
        lastElem.i_Node = first_node
        lastElem.j_Node = element.j_Node
        subElems.append(lastElem)
        return subElems, subNodes

    def addSubNodes(self, subNodeList):
        for node in subNodeList:
            self.nodes.append(node)
