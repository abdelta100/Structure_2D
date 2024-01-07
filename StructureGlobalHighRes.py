from Element import Element
from ElementHelperFunctions import ElementHelper
from Load import *
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
        self.subDivElementLoads(element, subElems)
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

    def subDivElementLoads(self, element, subElems):
        for load in element.loads:
            minusdist = 0
            plusdist = 0
            for subElem in subElems:
                subElem.clearLoads()
                minusdist = plusdist
                length = subElem.length
                plusdist += length
                if isinstance(load, PointLoadMember):
                    if minusdist < load.location < plusdist:
                        subElem.addLoad(PointLoadMember(load.magnitude, load.location-minusdist, angle=rad2degree(load.angle)))
                        break
                if isinstance(load, UniformDistributedLoad):
                    if minusdist < load.start < plusdist:
                        if minusdist < load.end < plusdist:
                            subElem.addLoad(load)
                        else:
                            subElem.addLoad(UniformDistributedLoad(load.magnitude, load.start-minusdist, length, angle=rad2degree(load.angle)))
                    elif minusdist < load.end < plusdist:
                        subElem.addLoad(UniformDistributedLoad(load.magnitude, 0, load.end - minusdist, angle=rad2degree(load.angle)))
                    elif load.start < minusdist and load.end > plusdist:
                        subElem.addLoad(UniformDistributedLoad(load.magnitude, 0, length, angle=rad2degree(load.angle)))
                if isinstance(load, VaryingDistributedLoad):
                    if minusdist < load.start < plusdist:
                        if minusdist < load.end < plusdist:
                            subElem.addLoad(load)
                        else:
                            subElem.addLoad(
                                VaryingDistributedLoad(load.magnitudeAtPoint(load.start),
                                                       load.magnitudeAtPoint(plusdist),
                                                       load.start - minusdist, length, angle=rad2degree(load.angle)))
                    elif minusdist < load.end < plusdist:
                        subElem.addLoad(
                            VaryingDistributedLoad(load.magnitudeAtPoint(minusdist), load.magnitudeAtPoint(load.end), 0,
                                                   load.end - minusdist, angle=rad2degree(load.angle)))
                    elif load.start < minusdist and load.end > plusdist:
                        VaryingDistributedLoad(load.magnitudeAtPoint(minusdist), load.magnitudeAtPoint(plusdist), 0,
                                               length, angle=rad2degree(load.angle))
