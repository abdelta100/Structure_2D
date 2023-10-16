import numpy as np

from CrossSection import DefaultRectangularCrossSection, CrossSection
from Load import Load
from Material import DefaultMaterial, Material
from Node import Node


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

    def elementStiffnessMatrix(self):
        pt1 = self.E * self.A / self.length                 #Partial Term 1: EA/L
        pt2 = 12 * (self.E * self.I) / self.length ** 3     #Partial Term 2: 12EI/L^3
        pt3 = 6 * (self.E * self.I) / self.length ** 2      #Partial Term 3: 6EI/L^2
        pt4 = 4 * (self.E * self.I) / self.length           #Partial Term 4: 4EI/L
        stiffness_matrix = np.array([[pt1, 0, 0, -pt1, 0, 0],
                                     [0, pt2, pt3, 0, -pt2, pt3],
                                     [0, pt3, pt4, 0, -pt3, pt4 / 2],
                                     [-pt1, 0, 0, pt1, 0, 0],
                                     [0, -pt2, -pt3, 0, pt2, -pt3],
                                     [0, pt3, pt4 / 2, 0, -pt3, pt4], ])

        return stiffness_matrix

    def elementTransformationMatrix(self):
        pass

    def addLoad(self, load: Load):
        pass
