import copy

from Core.Element import GeneralFrameElement2D
from Core.Node import Node
from AuxillaryFunctions import rad2degree
from Core.Load import PointLoadMember, MomentMember, UniformDistributedLoad, TrapezoidalDistributedLoad, \
    VaryingDistributedLoad
import matplotlib.pyplot as plt


class ElementHelper:

    @staticmethod
    def plotAxialForceDiagram(element: GeneralFrameElement2D):
        x, afd = element.calcAxialForceDiagram()
        plt.plot(x, afd, label="Axial Force")
        plt.axvline(x=0, c="black", label="length")
        plt.axhline(y=0, c="black", label="Axial Force Magnitude")
        plt.axvline(x=x[-1], c="black", label="length")
        plt.xlim(0, x[-1])
        plt.title("Axial Force Diagram")
        plt.show()

    @staticmethod
    def plotShearForceDiagram(element: GeneralFrameElement2D):
        x, sfd = element.calcShearForceDiagram()
        plt.plot(x, sfd, label= "Shear Force")
        plt.axvline(x=0, c="black", label="length")
        plt.axhline(y=0, c="black", label="Shear Magnitude")
        plt.axvline(x=x[-1], c="black", label="length")
        plt.xlim(0, x[-1])
        plt.title("Shear Force Diagram")
        plt.show()

    @staticmethod
    def plotBendingMomentDiagram(element: GeneralFrameElement2D):
        x, bmd = element.calcBendingMomentDiagram()
        # plotting negative bmd here for convention purposes
        plt.plot(x, -bmd, label= "Bending Moment")
        plt.axvline(x=0, c="black", label="length")
        plt.axhline(y=0, c="black", label="Bending Moment Magnitude")
        plt.axvline(x=x[-1], c="black", label="length")
        plt.xlim(0, x[-1])
        plt.title("Bending Moment Diagram")
        plt.show()

    @staticmethod
    def plotRotationDiagram(element: GeneralFrameElement2D):
        x, rot = element.calcRotation()
        plt.plot(x, rot, label= "Rotation")
        plt.axvline(x=0, c="black", label="length")
        plt.axhline(y=0, c="black", label="Rotation Angle")
        plt.axvline(x=x[-1], c="black", label="length")
        plt.xlim(0, x[-1])
        plt.title("Rotation/Slope Diagram")
        plt.show()

    @staticmethod
    def plotDeflectionDiagram(element: GeneralFrameElement2D):
        x, deflection = element.calcDeflectionMajor()
        plt.plot(x, deflection, label= "Deflection (Major)")
        plt.axvline(x=0, c="black", label="length")
        plt.axhline(y=0, c="black", label="Deflection")
        plt.axvline(x=x[-1], c="black", label="length")
        plt.xlim(0, x[-1])
        plt.title("Deflection Diagram (Major)")
        plt.show()

    @staticmethod
    def plotInternals(element: GeneralFrameElement2D):
        x, afd, sfd, bmd, rot, deflection = element.calcInternals()
        figure, axis = plt.subplots(5, 1, constrained_layout=True)

        axis[0].plot(x, afd, label="Axial Force Force")
        axis[0].axvline(x=0, c="black", label="length")
        axis[0].axhline(y=0, c="black", label="Axial Force Magnitude")
        axis[0].axvline(x=x[-1], c="black", label="length")
        axis[0].set_xlim(0, x[-1])
        axis[0].set_title("Axial Force Diagram")

        axis[1].plot(x, sfd, label="Shear Force")
        axis[1].axvline(x=0, c="black", label="length")
        axis[1].axhline(y=0, c="black", label="Shear Magnitude")
        axis[1].axvline(x=x[-1], c="black", label="length")
        axis[1].set_xlim(0, x[-1])
        axis[1].set_title("Shear Force Diagram")

        axis[2].plot(x, -bmd, label= "Bending Moment")
        axis[2].axvline(x=0, c="black", label="length")
        axis[2].axhline(y=0, c="black", label="BMD Magnitude")
        axis[2].axvline(x=x[-1], c="black", label="length")
        axis[2].set_xlim(0, x[-1])
        axis[2].set_title("Bending Moment Diagram")

        axis[3].plot(x, rot, label="Rotation")
        axis[3].axvline(x=0, c="black", label="length")
        axis[3].axhline(y=0, c="black", label="Rotation Angle")
        axis[3].axvline(x=x[-1], c="black", label="length")
        axis[3].set_xlim(0, x[-1])
        axis[3].set_title("Rotation/Slope Diagram")

        axis[4].plot(x, deflection, label="Deflection (Major)")
        axis[4].axvline(x=0, c="black", label="length")
        axis[4].axhline(y=0, c="black", label="Deflection")
        axis[4].axvline(x=x[-1], c="black", label="length")
        axis[4].set_xlim(0, x[-1])
        axis[4].set_title("Deflection Diagram (Major)")

        plt.show()

    @staticmethod
    def copyElementPropertiesSansNodes(element: GeneralFrameElement2D, clearLoads=True) -> GeneralFrameElement2D:
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
                    if minusdist <= load.location < plusdist:
                        subElem.addLoad(
                            PointLoadMember(load.magnitude, load.location - minusdist, angle=rad2degree(load.angle)))
                        break
                if isinstance(load, MomentMember):
                    if minusdist <= load.location < plusdist:
                        subElem.addLoad(
                            MomentMember(load.magnitude, load.location - minusdist))
                        break
                elif isinstance(load, UniformDistributedLoad):
                    if minusdist <= load.start < plusdist:
                        if minusdist <= load.end <= plusdist:
                            subElem.addLoad(load)
                        else:
                            subElem.addLoad(UniformDistributedLoad(load.magnitude, load.start - minusdist, length,
                                                                   angle=rad2degree(load.angle)))
                    elif minusdist < load.end <= plusdist:
                        subElem.addLoad(UniformDistributedLoad(load.magnitude, 0, load.end - minusdist,
                                                               angle=rad2degree(load.angle)))
                    elif load.start < minusdist and load.end > plusdist:
                        subElem.addLoad(UniformDistributedLoad(load.magnitude, 0, length, angle=rad2degree(load.angle)))
                elif isinstance(load, TrapezoidalDistributedLoad):
                    if minusdist <= load.location_list[0] < plusdist:
                        if minusdist <= load.location_list[-1] <= plusdist:
                            subElem.addLoad(load)
                        else:
                            subElem.addLoad(
                                TrapezoidalDistributedLoad([load.location_list[0] - minusdist, length],
                                                           [load.magnitudeAtPoint(load.location_list[0], axis='abs'),
                                                            load.magnitudeAtPoint(load.location_list[0] + length,
                                                                                  axis='abs')],
                                                           angle=rad2degree(load.angle)))
                    elif minusdist < load.location_list[-1] <= plusdist:
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
                    if minusdist <= load.start < plusdist:
                        if minusdist <= load.end <= plusdist:
                            subElem.addLoad(load)
                        else:
                            subElem.addLoad(
                                VaryingDistributedLoad(load.magnitudeAtPoint(load.start, axis='abs'),
                                                       load.magnitudeAtPoint(plusdist, axis='abs'),
                                                       load.start - minusdist, length, angle=rad2degree(load.angle)))
                    elif minusdist < load.end <= plusdist:
                        subElem.addLoad(
                            VaryingDistributedLoad(load.magnitudeAtPoint(minusdist, axis='abs'),
                                                   load.magnitudeAtPoint(load.end, axis='abs'), 0,
                                                   load.end - minusdist, angle=rad2degree(load.angle)))
                    elif load.start < minusdist and load.end > plusdist:
                        subElem.addLoad(
                            VaryingDistributedLoad(load.magnitudeAtPoint(minusdist, axis='abs'),
                                                   load.magnitudeAtPoint(plusdist, axis='abs'), 0,
                                                   length, angle=rad2degree(load.angle)))
