import copy
import math

import numpy as np
# from scipy.spatial.distance import euclidean
from AuxillaryFunctions import distance as euclidean

from .CrossSection import DefaultRectangularCrossSection, CrossSection
from .Load import StaticLoad, UniformDistributedLoad, VaryingDistributedLoad, PointLoadMember, MomentMember
from .LoadInterfaces import MemberLoad
from .Material import DefaultMaterial, Material
from .Node import Node
from PrincipleForce import PrincipleForce2D
from MemberEndRelease import FixedEndMember, MemberEndRelease2D, PinnedEndMember


# TODO Incorporate a 2D general frame element class here by renaming element class, and set element class  to inherit from it

class GeneralFrameElement2D:
    def __init__(self, i: Node, j: Node):
        """
        A 2D General Frame Element class. Linear element, has 3 DOF at each node, and 2 nodes.
        :rtype: GeneralFrameElement2D
        :param i: Node object for i-node of element
        :param j: Node object for j-node of element
        """
        self._i_Node: Node | None = i
        self._j_Node: Node | None = j
        self.id = 0
        self.material: Material = DefaultMaterial()
        self.crossSection: CrossSection = DefaultRectangularCrossSection()
        self.E: float = self.material.elasticModulus
        self.I: float = self.crossSection.momentOfInertia
        self.A: float = self.crossSection.area
        self.loads: list[MemberLoad] = []
        # TODO adds x or axial comp in nodeFEM
        self.node1FEM: PrincipleForce2D = PrincipleForce2D(0, 0, 0)
        self.node2FEM: PrincipleForce2D = PrincipleForce2D(0, 0, 0)
        self.FEM_Identity=np.eye(N=2*len(self.node1FEM))
        self.localStiffnessMatrix: np.ndarray = np.zeros(shape=(6, 6))
        self.transformationMatrix: np.ndarray = np.zeros(shape=(6, 6))
        self.globalStiffnessMatrix: np.ndarray = np.zeros(shape=(6, 6))
        self.endReleases: MemberEndRelease2D = FixedEndMember()
        # try:
        self.length: float = max(euclidean(self._i_Node.pos, self._j_Node.pos), 0.001)
        # except:
        #     pass
            # self.length=0.001
            # self.recalculateMatrices()
        # TODO add something about self weight

    def preprocessor(self, useSelfWeight: bool = False):
        self.recalculateMatrices()
        if useSelfWeight:
            # TODO check for non prismatic sections idk
            self.addLoad(UniformDistributedLoad(self.A, 0, self.length, angle=-90))

    def elementStiffnessMatrix(self):
        # Partial Term 1: EA/L
        # Partial Term 2: 12EI/L^3
        # Partial Term 3: 6EI/L^2
        # Partial Term 4: 4EI/L

        pt1 = self.E * self.A / self.length
        pt2 = 12 * (self.E * self.I) / self.length ** 3
        pt3 = 6 * (self.E * self.I) / self.length ** 2
        pt4 = 4 * (self.E * self.I) / self.length

        stiffness_matrix = np.array(
            [[pt1, 0, 0, -pt1, 0, 0],
                    [0, pt2, pt3, 0, -pt2, pt3],
                    [0, pt3, pt4, 0, -pt3, pt4 / 2],
                    [-pt1, 0, 0, pt1, 0, 0],
                    [0, -pt2, -pt3, 0, pt2, -pt3],
                    [0, pt3, pt4 / 2, 0, -pt3, pt4]],
            dtype=np.float64)

        stiffness_matrix, FEM_identity = self.endReleaseHandler(stiffness_matrix)
        self.FEM_Identity = FEM_identity

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

        # recheck the bottom
        transformation_matrix = np.array(
            [[c, s, 0, 0, 0, 0],
                    [-s, c, 0, 0, 0, 0],
                    [0, 0, 1, 0, 0, 0],
                    [0, 0, 0, c, s, 0],
                    [0, 0, 0, -s, c, 0],
                    [0, 0, 0, 0, 0, 1]], dtype=np.float64)

        return transformation_matrix

    def addLoad2(self, load: MemberLoad):
        self.loads.append(load)
        load.beamLength = self.length
        if isinstance(load, PointLoadMember):
            load.location = load.location = load.beamLength
        # TODO needs work to define order of precedence. Add load first or select member first?

    def addLoad(self, load: StaticLoad):
        #TODO add local and projection option control here?
        if isinstance(load, MemberLoad):
            load.beamLength = self.length
            load.cleanInputs()
            self.loads.append(load)
        else:
            print("Warning: Tried to apply Non-Member load on element. Load ignored.")

    def clearLoads(self):
        self.loads: list[StaticLoad] = []

    def addLoadInteractive(self):
        pass

    def calculateFixedEndMoments(self):
        iNodeLoad = PrincipleForce2D(0, 0, 0)
        jNodeLoad = PrincipleForce2D(0, 0, 0)
        for load in self.loads:
            iNodeLoadTemp, jNodeLoadTemp = load.calcFixedEndReactions()
            iNodeLoad -= iNodeLoadTemp
            jNodeLoad -= jNodeLoadTemp

        endReleaseHandledFEM = np.matmul(self.FEM_Identity, np.array(iNodeLoad.tolist()+jNodeLoad.tolist()))
        iNodeLoad.fx = endReleaseHandledFEM[0]
        iNodeLoad.fy = endReleaseHandledFEM[1]
        iNodeLoad.mxy = endReleaseHandledFEM[2]
        jNodeLoad.fx = endReleaseHandledFEM[3]
        jNodeLoad.fy = endReleaseHandledFEM[4]
        jNodeLoad.mxy = endReleaseHandledFEM[5]

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
        globalStiffnessMatrix = np.matmul(
            self.transformationMatrix.T, np.matmul(self.localStiffnessMatrix, self.transformationMatrix))
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

    def elementEndForces(self):
        pass

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
        length: float = euclidean(self._i_Node.pos, self._j_Node.pos)
        if length != self.length:
            self.recalculateMatrices()
        self.length=length
        if length==0: self.length=0.001
        return self.length

    def reset(self, reset_type="soft"):
        self.node1FEM: PrincipleForce2D = PrincipleForce2D(0, 0, 0)
        self.node2FEM: PrincipleForce2D = PrincipleForce2D(0, 0, 0)
        if reset_type == "hard":
            self.clearLoads()

    def endReleaseHandler2(self, localStiffness):
        kr=self.endReleases.tolist()
        release: np.ndarray = np.array(kr)
        base_transformation = np.eye(N=release.shape[0])
        for i in range(release.shape[0]):
            if release[i] == 0: #keep it not 1 in case further spring rotation needs to be added
                # localStiffness[i,]=1
                base_transformation[i, :] = -localStiffness[i, :]
                base_transformation[i, :] = base_transformation[i, :]/localStiffness[i,i]
                base_transformation[i, i] = 0
                for j in range(release.shape[0]):
                    if base_transformation[i, j] !=0 and base_transformation[j, j] == 0:
                        base_transformation[i, :] = base_transformation[i, :] + base_transformation[i, :] * -base_transformation[i,j]
                        base_transformation[i, :] = base_transformation[i, :] / (1-base_transformation[j, j])
                        base_transformation[j, j] = 0

                pass
        pass

    def endReleaseHandler(self, localStiffness):
        # create a release vector, ie convert to numpy array
        kr = self.endReleases.tolist()
        fixity: np.ndarray = np.array(kr)
        fixity_diag = np.diag(fixity)
        release_diag = np.diag(1-fixity)
        base_transformation = np.eye(N=fixity.shape[0])
        # create an array that stores repesantative values at indices of dependant dofs, could use better implementation
        slave_dof_copy_index = np.matmul(release_diag,np.matmul(np.ones(shape=(fixity.shape[0], fixity.shape[0])), release_diag))

        # create an array to store coefficiens of dependant dofs at their specific indices, check if element wise mult is working
        slave_dof = localStiffness * -slave_dof_copy_index

        # add 1s to slave_dof, at independent dof indices, results in slave_rref_gen
        add_to_slave_rref_gen=np.matmul(np.eye(N=fixity.shape[0]), fixity_diag)
        slave_rref_gen = np.linalg.pinv(slave_dof) + add_to_slave_rref_gen

        # final leg. substituting values of all slave_dofs including dependancy on independant dof into the modified
        # stiffness matrix, and gathering the result.
        mod_stiffness = np.matmul(slave_rref_gen, localStiffness)
        row_weight = np.matmul(mod_stiffness, release_diag)
        slave_dof_terms_eq = np.matmul(row_weight, mod_stiffness)
        final_mat_stiffness = mod_stiffness+slave_dof_terms_eq
        # in the avove few lines there maybe an issue while concising due to me thinking we need to use 1-row weight,
        # but instead it may require I-row weight, also some buggery with matmul or elementwise mult

        fem_identity = np.eye(fixity.shape[0])
        mod_fem = np.matmul(slave_rref_gen, fem_identity)
        slave_dof_terms_eq_fem = np.matmul(row_weight, mod_fem)
        final_fem_identity = mod_fem+slave_dof_terms_eq_fem
        # print(final_mat)
        # Probelm above, becuase mod_stiffness is calc some other way idk????
        # for i in z_index:
        #     # figure out concise notation for this
        #     slave_to_master[i,:] = master_dof[i, :]
        #
        # final_master_dof = np.matmul(master_dof, slave_to_master)
        a = 3
        # isolate just the transformation matrix from here plz
        return final_mat_stiffness, final_fem_identity

    def endReleaseHandlerForFEM(self):
        pass

    def setEndRelease(self, endRelease: MemberEndRelease2D):
        self.endReleases = endRelease

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


class FrameElement(GeneralFrameElement2D):
    # Aliasing generalframe element 2d requires somework, esp in sudiv elements where the element are themselves not 2D
    # General Frame
    def __init__(self, i: Node, j: Node):
        """
        A 2D Frame Element class. Linear element, has 3 DOF at each node, and 2 nodes.
        :rtype: FrameElement
        :param i: Node object for i-node of element
        :param j: Node object for j-node of element
        """
        super().__init__(i, j)

class TrussElement(GeneralFrameElement2D):
    def __init__(self, i: Node, j: Node):
        """
        A 2D Truss Element class. Linear element, has 3 DOF at each node, and 2 nodes.
        :rtype: TrussElement
        :param i: Node object for i-node of element
        :param j: Node object for j-node of element
        """
        super().__init__(i, j)
        self.endReleases: MemberEndRelease2D = PinnedEndMember()
        # self.recalculateMatrices()

