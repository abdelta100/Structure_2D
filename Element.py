from CrossSection import DefaultRectangularCrossSection, CrossSection
from Material import DefaultMaterial, Material
from Node import Node


class Element:
    def __init__(self):
        self.i_Node: Node = None
        self.j_Node: Node = None
        self.material: Material = DefaultMaterial()
        self.crossSection: CrossSection = DefaultRectangularCrossSection()
        self.E = self.material.elasticModulus
        self.I = self.crossSection.MomentofInertia
