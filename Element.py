import math

import numpy as np

from CrossSection import DefaultRectangularCrossSection, CrossSection
from Load import Load
from Material import DefaultMaterial, Material
from Node import Node
from AuxillaryFunctions import getComponentsRefBeam


class Element:
    def __init__(self):
        self.i_Node: Node = None
        self.j_Node: Node = None
        self.length: float = 0
        self.material: Material = DefaultMaterial()
        self.crossSection: CrossSection = DefaultRectangularCrossSection()
        self.E = self.material.elasticModulus
        self.I = self.crossSection.momentOfInertia
        self.A = self.crossSection.area
        self.stiffnessMatrix = self.elementStiffnessMatrix()
        self.loads: list[Load] = []
        self.node1FEM: list[float] = [0, 0]
        self.node2FEM: list[float] = [0, 0]

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
                                     [0, pt3, pt4 / 2, 0, -pt3, pt4]])

        return stiffness_matrix

    def elementTransformationMatrix(self):
        theta = np.arctan2(self.j_Node.y, self.i_Node.y, self.j_Node.x - self.i_Node.x)
        c = np.cos(theta)
        s = np.sin(theta)
        # recheck the bottom
        transformation_matrix = np.array([[c, s, 0, 0, 0, 0],
                                          [-s, c, 0, 0, 0, 0],
                                          [0, 0, 1, 0, 0, 0],
                                          [0, 0, 0, c, s, 0],
                                          [0, 0, 0, -s, c, 0],
                                          [0, 0, 0, 0, 0, 1]])

        return transformation_matrix

    def addLoad(self, load: Load):
        self.loads.append(load)
        #TODO needs work to define order of precedence. Add load first or select member first?


    def addLoadInteractive(self):
        pass

    def calculateFixedEndMoments(self):
        ER1=0
        ER2=0
        EV1=0
        EV2=0
        for load in self.loads:
            tR1, tR2, tV1, tV2 = load.calcFixedEndReactions()
            ER1 += tR1
            ER2 += tR2
            EV2 += tV1
            EV2 += tV2

        self.node1FEM = [ER1, EV1]
        self.node2FEM = [ER2, EV2]

        EV1x, EV1y = getComponentsRefBeam(self.getAngle(), EV1)
        EV2x, EV2y = getComponentsRefBeam(self.getAngle(), EV2)

        self.i_Node.FEM[0] += EV1x
        self.i_Node.FEM[1] += EV1x
        self.i_Node.FEM[2] += ER1
        self.j_Node.FEM[0] += EV2x
        self.j_Node.FEM[1] += EV2y
        self.j_Node.FEM[1] += ER2

    def getAngle(self):
        angle = math.atan2(self.j_Node.y-self.i_Node.y, self.j_Node.x-self.i_Node.x)
        return angle