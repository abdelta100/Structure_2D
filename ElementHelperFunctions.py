import copy

from Element import Element
from Node import Node


class ElementHelper:
    @staticmethod
    def copyElementPropertiesSansNodes(element: Element) -> Element:
        newElem = copy.deepcopy(element)
        #TODO jugaar here, initialzed to random node
        newElem.i_Node = Node(0,0, -999)
        newElem.j_Node = Node(0,0, -999)
        return newElem
