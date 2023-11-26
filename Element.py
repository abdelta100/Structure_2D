import math
from scipy.spatial.distance import euclidean

import numpy as np

from AuxillaryFunctions import getComponentsRefBeam
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
        #TODO adds x or axial comp in nodeFEM
        self.node1FEM: list[float] = [0, 0]
        self.node2FEM: list[float] = [0, 0]
        #TODO add initilaization for transformed matrix and transformation matrices
        #TODO add functions for recalculation of matrices
        self.transformationMatrix: np.ndarray = self.elementTransformationMatrix()
        self.globalStiffnessMatrix: np.ndarray = self.local2globalStiffness()

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
        theta = np.arctan2(self.j_Node.y- self.i_Node.y, self.j_Node.x - self.i_Node.x)
        c = np.cos(theta)
        s = np.sin(theta)

        #TODO added to manually force zeros
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
        load.beamLength=self.length
        if isinstance(load, PointLoadMember):
            load.location=load.location=load.beamLength
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
            tR1, tR2, tV1, tV2 = load.calcFixedEndReactions()
            ER1 += tR1
            ER2 += tR2
            EV1 += tV1
            EV2 += tV2
            #TODO implement this
            EA1 += 0
            EA2 += 0

        self.node1FEM = [ER1, EV1]
        self.node2FEM = [ER2, EV2]

        EV1x, EV1y = getComponentsRefBeam(self.getAngle(), EV1)
        EV2x, EV2y = getComponentsRefBeam(self.getAngle(), EV2)

        self.i_Node.FEM[0] += EV1x
        self.i_Node.FEM[1] += EV1y
        self.i_Node.FEM[2] += ER1
        self.j_Node.FEM[0] += EV2x
        self.j_Node.FEM[1] += EV2y
        self.j_Node.FEM[2] += ER2

    def getAngle(self):
        angle = math.atan2(self.j_Node.y - self.i_Node.y, self.j_Node.x - self.i_Node.x)
        return angle

    def recalculateMatrices(self) -> None:
        self.localStiffnessMatrix = self.elementStiffnessMatrix()
        self.transformationMatrix=self.elementTransformationMatrix()
        self.globalStiffnessMatrix=self.local2globalStiffness()

    def local2globalStiffness(self):
        globalStiffnessMatrix= np.matmul(self.transformationMatrix, np.matmul(self.localStiffnessMatrix, self.transformationMatrix.T))
        return globalStiffnessMatrix

    def addLoad(self, load:Load):
        load.beamLength = self.length
        if isinstance(load, UniformDistributedLoad) or isinstance(load, VaryingDistributedLoad):
            load.cleanInputs()
        self.loads.append(load)

    def setMaterial(self, material: Material):
        self.material=material
        self.E=self.material.elasticModulus
        self.localStiffnessMatrix: np.ndarray = self.elementStiffnessMatrix()
        self.globalStiffnessMatrix: np.ndarray = self.local2globalStiffness()

    def setCrossSection(self, section: CrossSection):
        self.crossSection=section
        self.A=self.crossSection.calcSectionArea()
        self.I=self.crossSection.calcMomentofInertia()
        self.localStiffnessMatrix: np.ndarray = self.elementStiffnessMatrix()
        self.globalStiffnessMatrix: np.ndarray = self.local2globalStiffness()
