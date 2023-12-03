import math

import numpy as np
from scipy.spatial.distance import euclidean

from AuxillaryFunctions import getPerpendicularComponentsRefBeam, getAxialComponentsRefBeam
from CrossSection import DefaultRectangularCrossSection, CrossSection
from Load import Load, UniformDistributedLoad, VaryingDistributedLoad, PointLoadMember
from Material import DefaultMaterial, Material
from Node import Node


class Element:
    def __init__(self, i: Node, j: Node):
        self.i_Node: Node | None = i
        self.j_Node: Node | None = j
        self.length: float = euclidean(self.i_Node.pos, self.j_Node.pos)
        self.material: Material = DefaultMaterial()
        self.crossSection: CrossSection = DefaultRectangularCrossSection()
        self.E: float = self.material.elasticModulus
        self.I: float = self.crossSection.momentOfInertia
        self.A: float = self.crossSection.area
        self.localStiffnessMatrix: np.ndarray = self.elementStiffnessMatrix()
        self.loads: list[Load] = []
        # TODO adds x or axial comp in nodeFEM
        self.node1FEM: list[float] = [0, 0]
        self.node2FEM: list[float] = [0, 0]
        self.transformationMatrix: np.ndarray = self.elementTransformationMatrix()
        self.globalStiffnessMatrix: np.ndarray = self.local2globalStiffness()
        #TODO add something about self weight

    def elementStiffnessMatrix(self):
        # Partial Term 1: EA/L
        # Partial Term 2: 12EI/L^3
        # Partial Term 3: 6EI/L^2
        # Partial Term 4: 4EI/L

        pt1 = self.E * self.A / self.length
        pt2 = 12 * (self.E * self.I) / self.length ** 3
        pt3 = 6 * (self.E * self.I) / self.length ** 2
        pt4 = 4 * (self.E * self.I) / self.length

        stiffness_matrix = np.array([[pt1, 0, 0, -pt1, 0, 0],
                                     [0, pt2, pt3, 0, -pt2, pt3],
                                     [0, pt3, pt4, 0, -pt3, pt4 / 2],
                                     [-pt1, 0, 0, pt1, 0, 0],
                                     [0, -pt2, -pt3, 0, pt2, -pt3],
                                     [0, pt3, pt4 / 2, 0, -pt3, pt4]], dtype=np.float64)

        return stiffness_matrix

    def elementTransformationMatrix(self):
        theta = np.arctan2(self.j_Node.y - self.i_Node.y, self.j_Node.x - self.i_Node.x)
        c = np.cos(theta)
        s = np.sin(theta)

        # TODO added to manually force zeros
        zerolim = 10E-9
        if -zerolim < c < zerolim:
            c = 0
        if -zerolim < s < zerolim:
            s = 0

        print("c: ", c)
        print("s: ", s)

        # recheck the bottom
        transformation_matrix = np.array([[c, s, 0, 0, 0, 0],
                                          [-s, c, 0, 0, 0, 0],
                                          [0, 0, 1, 0, 0, 0],
                                          [0, 0, 0, c, s, 0],
                                          [0, 0, 0, -s, c, 0],
                                          [0, 0, 0, 0, 0, 1]], dtype=np.float64)

        return transformation_matrix

    def addLoad(self, load: Load):
        self.loads.append(load)
        load.beamLength = self.length
        if isinstance(load, PointLoadMember):
            load.location = load.location = load.beamLength
        # TODO needs work to define order of precedence. Add load first or select member first?

    def addLoadInteractive(self):
        pass

    def calculateFixedEndMoments(self):
        ER1 = 0
        ER2 = 0
        EV1 = 0
        EV2 = 0
        EA1 = 0
        EA2 = 0
        for load in self.loads:
            tR1, tR2, tV1, tV2, tA1, tA2 = load.calcFixedEndReactions()
            ER1 -= tR1
            ER2 -= tR2
            EV1 -= tV1
            EV2 -= tV2
            # TODO implement this
            EA1 -= tA1
            EA2 -= tA2

        self.node1FEM = [ER1, EV1]
        self.node2FEM = [ER2, EV2]

        EV1x, EV1y = getPerpendicularComponentsRefBeam(self.getAngle(), EV1)
        EV2x, EV2y = getPerpendicularComponentsRefBeam(self.getAngle(), EV2)
        EA1x, EA1y = getAxialComponentsRefBeam(self.getAngle(), EA1)
        EA2x, EA2y = getAxialComponentsRefBeam(self.getAngle(), EA2)

        self.i_Node.FEM[0] += EV1x + EA1x
        self.i_Node.FEM[1] += EV1y + EA1y
        self.i_Node.FEM[2] += ER1
        self.j_Node.FEM[0] += EV2x + EA2x
        self.j_Node.FEM[1] += EV2y + EA2y
        self.j_Node.FEM[2] += ER2

    def getAngle(self):
        angle = math.atan2(self.j_Node.y - self.i_Node.y, self.j_Node.x - self.i_Node.x)
        return angle

    def recalculateMatrices(self) -> None:
        self.localStiffnessMatrix = self.elementStiffnessMatrix()
        self.transformationMatrix = self.elementTransformationMatrix()
        self.globalStiffnessMatrix = self.local2globalStiffness()

    def local2globalStiffness(self):
        globalStiffnessMatrix = np.matmul(self.transformationMatrix,
                                          np.matmul(self.localStiffnessMatrix, self.transformationMatrix.T))
        return globalStiffnessMatrix

    def addLoad(self, load: Load):
        load.beamLength = self.length
        if isinstance(load, UniformDistributedLoad) or isinstance(load, VaryingDistributedLoad):
            load.cleanInputs()
        self.loads.append(load)

    def setMaterial(self, material: Material):
        self.material = material
        self.E = self.material.elasticModulus
        self.localStiffnessMatrix: np.ndarray = self.elementStiffnessMatrix()
        self.globalStiffnessMatrix: np.ndarray = self.local2globalStiffness()

    def setCrossSection(self, section: CrossSection):
        self.crossSection = section
        self.A = self.crossSection.calcSectionArea()
        self.I = self.crossSection.calcMomentofInertia()
        self.localStiffnessMatrix: np.ndarray = self.elementStiffnessMatrix()
        self.globalStiffnessMatrix: np.ndarray = self.local2globalStiffness()

    def calculateInternalForcesAndDisplacements(self):
        self.calcShearForceDiagram()
        pass

    def showInternals(self):
        pass

    def calcShearForceDiagram(self):
        num_elems = 1000
        resolution_distance = self.length / num_elems
        # TODO issue here in using FEM. maybe in case where node is not fixed but has a free dof.
        i_node_Force_transformed = np.matmul(np.array(self.i_Node.FEM), self.transformationMatrix[:3, :3])
        j_node_Force = self.j_Node.FEM
        subElems = [i * self.length / num_elems for i in range(num_elems)]
        # transform i_node force to local coords
        sfd = [-i_node_Force_transformed[1]]
        for point in subElems:
            for load in self.loads:
                #TODO may cause issue with point loads, since resolution is implied and subElems may skip that particular point
                sfd[-1] += load.magnitudeAtPoint(point) * resolution_distance

            sfd.append(sfd[-1])
        sfd.pop(-1)

        return subElems, sfd

    def calcBendingMomentDiagram(self):
        # TODO add cosmetic opening and closing points on diagram arrays for clarity??
        num_elems = 1000
        resolution_distance = self.length / num_elems
        subElems, sfd = self.calcShearForceDiagram()
        print(sfd)
        # TODO issue here in using FEM. maybe in case where node is not fixed but has a free dof.
        print(np.array(self.i_Node.FEM))
        print(self.transformationMatrix[:3, :3])
        i_node_Force_transformed = np.matmul(np.array(self.i_Node.FEM), self.transformationMatrix[:3, :3])
        print(i_node_Force_transformed[2])

        # transform i_node force to local coords
        bmd = [i_node_Force_transformed[2]]
        for point, sf in zip(subElems, sfd):
            bmd.append(bmd[-1])
            bmd[-1] += sf * resolution_distance

        bmd.pop(-1)

        return subElems, bmd

    def showForceDiagram(self):
        num_elems = 1000
        # TODO issue here in using FEM. maybe in case where node is not fixed but has a free dof.
        # TODO, this displays opposite force to normally seen, because the force is in fact negative, work on this.
        subElems = [i * self.length / num_elems for i in range(num_elems)]
        # transform i_node force to local coords
        fd = [0]
        for point in subElems:
            for load in self.loads:
                # TODO switching to minus here for clearer diagrams
                fd[-1] -= load.magnitudeAtPoint(point, axis="perpendicular")
            fd.append(0)
        fd.pop(-1)
        print(fd)

        return subElems, fd
