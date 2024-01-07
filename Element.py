import math

import numpy as np
from scipy.spatial.distance import euclidean

from CrossSection import DefaultRectangularCrossSection, CrossSection
from Load import StaticLoad, UniformDistributedLoad, VaryingDistributedLoad, PointLoadMember, MomentMember
from Material import DefaultMaterial, Material
from Node import Node
from PrincipleForce import PrincipleForce


class Element:
    def __init__(self, i: Node, j: Node):
        self._i_Node: Node | None = i
        self._j_Node: Node | None = j
        self.id = 0
        self.material: Material = DefaultMaterial()
        self.crossSection: CrossSection = DefaultRectangularCrossSection()
        self.E: float = self.material.elasticModulus
        self.I: float = self.crossSection.momentOfInertia
        self.A: float = self.crossSection.area
        self.loads: list[StaticLoad] = []
        # TODO adds x or axial comp in nodeFEM
        self.node1FEM: PrincipleForce = PrincipleForce(0, 0, 0)
        self.node2FEM: PrincipleForce = PrincipleForce(0, 0, 0)
        self.localStiffnessMatrix: np.ndarray = np.zeros(shape=(6, 6))
        self.transformationMatrix: np.ndarray = np.zeros(shape=(6, 6))
        self.globalStiffnessMatrix: np.ndarray = np.zeros(shape=(6, 6))
        try:
            self.length: float = self.calc_length()
            self.recalculateMatrices()
        except:
            pass
        # TODO add something about self weight

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

    def addLoad2(self, load: StaticLoad):
        self.loads.append(load)
        load.beamLength = self.length
        if isinstance(load, PointLoadMember):
            load.location = load.location = load.beamLength
        # TODO needs work to define order of precedence. Add load first or select member first?

    def addLoad(self, load: StaticLoad):
        load.beamLength = self.length
        if isinstance(load, UniformDistributedLoad) or isinstance(load, VaryingDistributedLoad):
            load.cleanInputs()
        self.loads.append(load)

    def clearLoads(self):
        self.loads: list[StaticLoad] = []

    def addLoadInteractive(self):
        pass

    def calculateFixedEndMoments(self):
        iNodeLoad = PrincipleForce(0, 0, 0)
        jNodeLoad = PrincipleForce(0, 0, 0)
        for load in self.loads:
            iNodeLoadTemp, jNodeLoadTemp = load.calcFixedEndReactions()
            iNodeLoad -= iNodeLoadTemp
            jNodeLoad -= jNodeLoadTemp

        self.node1FEM = iNodeLoad
        self.node2FEM = jNodeLoad

        iNodeLoadGlobal = iNodeLoad.returnTransformed(self.getAngle())
        jNodeLoadGlobal = jNodeLoad.returnTransformed(self.getAngle())

        self.i_Node.FEM += iNodeLoadGlobal
        self.j_Node.FEM += jNodeLoadGlobal

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
        i_node_Force_transformed = np.matmul(np.array(self.i_Node.FEM.tolist()), self.transformationMatrix[:3, :3])
        j_node_Force = self.j_Node.FEM
        subElems = [i * self.length / num_elems for i in range(num_elems)]
        # transform i_node force to local coords
        sfd = [-i_node_Force_transformed[1]]
        for point in subElems:
            for load in self.loads:
                # TODO may cause issue with point loads, since resolution is implied and subElems may skip that particular point
                if not isinstance(load, MomentMember):
                    sfd[-1] += load.magnitudeAtPoint(point) * resolution_distance
                    # TODO shear and bmd code is a mess fix it
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
        i_node_Force_transformed = np.matmul(np.array(self.i_Node.FEM.tolist()), self.transformationMatrix[:3, :3])
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

    def calc_length(self):
        # TODO both sets a value and returns a value, check if this is correct
        self.length: float = euclidean(self._i_Node.pos, self._j_Node.pos)
        return self.length

    @property
    def i_Node(self):
        return self._i_Node

    @i_Node.setter
    def i_Node(self, i_node):
        self._i_Node = i_node
        self.length = self.calc_length()

    @property
    def j_Node(self):
        return self._j_Node

    @j_Node.setter
    def j_Node(self, j_node):
        self._j_Node = j_node
        self.length = self.calc_length()
