import copy

from Element import Element


class ElementHelper:
    @staticmethod
    def copyElementPropertiesSansNodes(element: Element) -> Element:
        newElem = copy.deepcopy(element)
        newElem.i_Node = None
        newElem.j_Node = None
        return newElem
