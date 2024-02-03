import copy

from Core.Element import Element
from Core.Node import Node
from AuxillaryFunctions import rad2degree
from Core.Load import PointLoadMember, MomentMember, UniformDistributedLoad, TrapezoidalDistributedLoad, \
    VaryingDistributedLoad


class ElementHelper:
    @staticmethod
    def copyElementPropertiesSansNodes(element: Element, clearLoads=True) -> Element:
        newElem = copy.deepcopy(element)
        #TODO jugaar here, initialzed to random node
        newElem.i_Node = Node(0,0, -999)
        newElem.j_Node = Node(0,0, -999)
        if clearLoads: newElem.clearLoads()
        return newElem

    @staticmethod
    def subDivElementLoads(element, subElems):
        for load in element.loads:
            minusdist = 0
            plusdist = 0
            for subElem in subElems:
                # subElem.clearLoads()
                minusdist = plusdist
                length = subElem.length
                plusdist += length
                if isinstance(load, PointLoadMember):
                    if minusdist < load.location < plusdist:
                        subElem.addLoad(
                            PointLoadMember(load.magnitude, load.location - minusdist, angle=rad2degree(load.angle)))
                        break
                if isinstance(load, MomentMember):
                    if minusdist < load.location < plusdist:
                        subElem.addLoad(
                            MomentMember(load.magnitude, load.location - minusdist))
                        break
                elif isinstance(load, UniformDistributedLoad):
                    if minusdist < load.start < plusdist:
                        if minusdist < load.end < plusdist:
                            subElem.addLoad(load)
                        else:
                            subElem.addLoad(UniformDistributedLoad(load.magnitude, load.start - minusdist, length,
                                                                   angle=rad2degree(load.angle)))
                    elif minusdist < load.end < plusdist:
                        subElem.addLoad(UniformDistributedLoad(load.magnitude, 0, load.end - minusdist,
                                                               angle=rad2degree(load.angle)))
                    elif load.start < minusdist and load.end > plusdist:
                        subElem.addLoad(UniformDistributedLoad(load.magnitude, 0, length, angle=rad2degree(load.angle)))
                elif isinstance(load, TrapezoidalDistributedLoad):
                    if minusdist < load.location_list[0] < plusdist:
                        if minusdist < load.location_list[-1] < plusdist:
                            subElem.addLoad(load)
                        else:
                            subElem.addLoad(
                                TrapezoidalDistributedLoad([load.location_list[0] - minusdist, length],
                                                           [load.magnitudeAtPoint(load.location_list[0], axis='abs'),
                                                            load.magnitudeAtPoint(load.location_list[0] + length,
                                                                                  axis='abs')],
                                                           angle=rad2degree(load.angle)))
                    elif minusdist < load.location_list[-1] < plusdist:
                        subElem.addLoad(
                            TrapezoidalDistributedLoad([0, load.location_list[-1] - minusdist],
                                                       [load.magnitudeAtPoint(minusdist, axis='abs'),
                                                        load.magnitudeAtPoint(load.location_list[-1], axis='abs')],
                                                       angle=rad2degree(load.angle)))

                    elif load.location_list[0] < minusdist and load.location_list[-1] > plusdist:
                        subElem.addLoad(
                            TrapezoidalDistributedLoad([0, length],
                                                       [load.magnitudeAtPoint(minusdist, axis='abs'),
                                                        load.magnitudeAtPoint(plusdist, axis='abs')],
                                                       angle=rad2degree(load.angle)))

                elif isinstance(load, VaryingDistributedLoad):
                    if minusdist < load.start < plusdist:
                        if minusdist < load.end < plusdist:
                            subElem.addLoad(load)
                        else:
                            subElem.addLoad(
                                VaryingDistributedLoad(load.magnitudeAtPoint(load.start, axis='abs'),
                                                       load.magnitudeAtPoint(plusdist, axis='abs'),
                                                       load.start - minusdist, length, angle=rad2degree(load.angle)))
                    elif minusdist < load.end < plusdist:
                        subElem.addLoad(
                            VaryingDistributedLoad(load.magnitudeAtPoint(minusdist, axis='abs'),
                                                   load.magnitudeAtPoint(load.end, axis='abs'), 0,
                                                   load.end - minusdist, angle=rad2degree(load.angle)))
                    elif load.start < minusdist and load.end > plusdist:
                        VaryingDistributedLoad(load.magnitudeAtPoint(minusdist, axis='abs'),
                                               load.magnitudeAtPoint(plusdist, axis='abs'), 0,
                                               length, angle=rad2degree(load.angle))
