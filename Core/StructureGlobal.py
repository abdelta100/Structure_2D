import numpy as np

from AuxillaryFunctions import matrixStabilityCheck
from .Element import GeneralFrameElement2D
from ElementHelperFunctions import ElementHelper
from .Load import StaticLoad
from .Node import Node
from .Support import Support, FixedSupport
from .Constants import *


class StructureGlobal:
    def __init__(self):
        """
        A structure class that holds the entire structure, and contains methods for analysis etc.
        """
        self.nodes: list[Node] = []
        self.elements: list[GeneralFrameElement2D] = []
        self.supports: list[Support] = []
        self.loads: list[StaticLoad] = []
        self.dof = DOF
        self._useSelfWeight: bool = False
        self.stiffnessMatrix: np.ndarray = np.zeros(shape=(len(self.nodes) * self.dof, len(self.nodes) * self.dof))

    def createGlobalStiffnessMatrix(self):
        # TODO include element node releases or something, pure release implemented, partial release not
        # transformedElementMatrices=[element.transformedMatrix for element in self.elements]
        globalStiffnessMatrix = np.zeros(shape=(len(self.nodes) * self.dof, len(self.nodes) * self.dof), dtype=np.float64)
        for element in self.elements:
            i_node = element.i_Node.idnum
            j_node = element.j_Node.idnum
            for index, i in enumerate((i_node, j_node)):
                for index2, j in enumerate((i_node, j_node)):
                    globalStiffnessMatrix[i * self.dof:(i + 1) * self.dof,
                    j * self.dof:(j + 1) * self.dof] += element.globalStiffnessMatrix[
                                                        index * self.dof:(index + 1) * self.dof,
                                                        index2 * self.dof:(index2 + 1) * self.dof]
        # TODO provide option to return just the stiffness witout running the solver, or maybe a model build?
        self.stiffnessMatrix = globalStiffnessMatrix
        return globalStiffnessMatrix

    def createPermutationMatrix(self):
        # fixity vector
        disp_vector = np.zeros(shape=(len(self.nodes) * self.dof))
        for support in self.supports:
            # edit Line when going 3D
            disp_vector[support.idnum * self.dof: (support.idnum + 1) * self.dof] = np.array(
                support.supportRelease.tolist())
        perm_order = np.argsort(disp_vector)
        permutation_matrix = np.zeros(shape=(disp_vector.shape[0], disp_vector.shape[0]))
        for i, j in zip(range(len(disp_vector)), perm_order):
            permutation_matrix[i, j] = 1
        return permutation_matrix, np.matmul(permutation_matrix, disp_vector)

    def _solver(self):
        # FIXEDTODO handle single beam edge case or similar
        # TODO permutation matrix needs to be created by factoring in Supports not just nodes
        permutationMatrix, permutatedOrder = self.createPermutationMatrix()
        globalStiffness = self.createGlobalStiffnessMatrix()
        globalStiffness = matrixStabilityCheck(globalStiffness)
        self.stiffnessMatrix = globalStiffness
        permutedMatrix = np.matmul(permutationMatrix, np.matmul(globalStiffness, permutationMatrix.T))
        fixed_index = np.where(permutatedOrder == 1)[0][0]

        # | UU      UK |
        # | KU      KK |

        UU = permutedMatrix[:fixed_index, :fixed_index]
        UK = permutedMatrix[:fixed_index, fixed_index:]
        KU = permutedMatrix[fixed_index:, :fixed_index]
        KK = permutedMatrix[fixed_index:, fixed_index:]

        # | FK |
        # | FU |

        permutatedAppliedLoads = self.orderAppliedLoads(permutationMatrix)
        FK = permutatedAppliedLoads[:fixed_index]
        FU = permutatedAppliedLoads[fixed_index:]

        # | DU |
        # | DK |

        # TODO Use actual displacement case here instead of assuming zero
        orderedDisplacementVector = np.zeros(shape=permutatedAppliedLoads.shape)
        DU = orderedDisplacementVector[:fixed_index]
        DK = orderedDisplacementVector[fixed_index:]

        # FK = UU*DU + UK * DK
        # DK zero by definition (not specific case yet where spring deformation)
        # DU = (FK - UK*DK) * UU.inv
        # FU = KU*DU + KK * DK

        DU = np.linalg.solve(UU, FK - np.matmul(UK, DK))
        # DU = np.matmul(FK-np.matmul(UK, DK), np.linalg.inv(UU))
        FU = np.matmul(KU, DU) + np.matmul(KK, DK)

        filledDisplacementVector = np.concatenate((DU, DK), axis=0)
        filledForceVector = np.concatenate((FK, FU), axis=0)

        self._pushDisplacements(filledDisplacementVector, permutationMatrix)
        self._pushReactions(filledForceVector, permutationMatrix)

        # TODO involve displacement vector

    def transferLoadstoNodes(self):
        for element in self.elements:
            element.calculateFixedEndMoments()

    def collectNodalLoads(self):
        for node in self.nodes:
            node.combineAllLoads()

    def orderAppliedLoads(self, permutationMatrix):
        self.transferLoadstoNodes()
        self.collectNodalLoads()
        # unordered applied load vector
        appLoads = np.zeros(shape=len(self.nodes) * self.dof)
        for node in self.nodes:
            # TODO reconcile self.dof and len netload,
            # both should be same but different variables are referenced may cause issue
            #netload references a principleforce2d class, which has a hardcoded length of 3, could also use self.dof here
            appLoads[node.idnum * self.dof:node.idnum * self.dof + len(node.netLoad)] = node.netLoad.tolist()

        orderedLoads = np.matmul(permutationMatrix, appLoads)
        return orderedLoads

    def _pushDisplacements(self, orderedDispVector, permutationMatrix):
        # TODO future issue here. If my internal nodes are not fixed in some dof, I might have to transfer my nodal
        #  loads (received from analysis) back to nodes, and draw sfd etc from that
        origOrderDisplacement = np.matmul(permutationMatrix.T, orderedDispVector)
        for node in self.nodes:
            tempdisp = origOrderDisplacement[node.idnum * self.dof:(node.idnum + 1) * self.dof]
            # transformedtemdisp=np.matmul(nod)
            node.disp.dx = tempdisp[0]
            node.disp.dy = tempdisp[1]
            node.disp.rxy = tempdisp[2]

    def _pushReactions(self, orderedForceVector, permutationMatrix):
        # TODO figure out force/reaction push details since i'm not pushing anything to nodes here, just supports
        origOrderForce = np.matmul(permutationMatrix.T, orderedForceVector)

        for support in self.supports:
            tempforce = origOrderForce[support.idnum * self.dof:(support.idnum + 1) * self.dof]
            nodeAppliedForce=support.node.FEM
            support.reaction.fx = tempforce[0] # -nodeAppliedForce.fx
            support.reaction.fy = tempforce[1] # -nodeAppliedForce.fy
            support.reaction.mxy = tempforce[2] # -nodeAppliedForce.mxy
            
            # Forces applied on support node are returned directly in reverse as reaction, so we subtract applied force
            # from support reaction found from analysis to get actual support reactions
            support.reaction -= nodeAppliedForce

            # TODO add some transformation thingy here for support in case support reactions are not x/y or perp or
            # something like that

    def runAnalysis(self):
        """
        Method that runs analysis of the structure.
        """
        # self._structureModelIntegrityChecker()
        self._singleFixedBeamHandler()
        self._preprocessor()
        self._solver()

    def _preprocessor(self):
        for element in self.elements:
            element.preprocessor(self._useSelfWeight)

    def useSelfWeight(self, useSelfWeight: bool = True):
        self._useSelfWeight = useSelfWeight

    def findAllNodalForcesPostAnalysis(self):
        nodeAdjacencyMatrix, elemNodeIntersection = self.createElementNodeIntersectionMatrix()
        # Source Nodes for bfs
        initialNodes = []
        for support in self.supports:
            # TODO Phase the following line out because too bulky
            initialNodes.append(support)

        # TODO implement multisource breadth first search or something to traverse all nodes by and find nodal loads
        #  via elements
        pass

    def createElementNodeIntersectionMatrix(self):
        nodeAdjacency = np.zeros(shape=(len(self.nodes), len(self.nodes)))
        elemNodeIntersection = np.zeros(shape=(len(self.nodes), len(self.elements)))
        for element in self.elements:
            nodeAdjacency[element.i_Node.idnum, element.j_Node.idnum] = 1
            elemNodeIntersection[element.id, element.i_Node.idnum] = -1
            elemNodeIntersection[element.id, element.j_Node.idnum] = 1
        return nodeAdjacency, elemNodeIntersection

    def _structureModelIntegrityChecker(self):
        # TODO check and assign id nums for nodes and assign idnums to elements, also reorder nodes or elems then
        num_nodes = len(self.nodes)
        node_num = list(range(num_nodes))
        for node in self.nodes:
            if node.idnum in node_num:
                node_num.remove(node.idnum)

        # for node in self.nodes:
        #     if node.idnum not in node_num:
        #         node.idnum = node_num[0]
        #         node_num.pop(0)

        num_supports = len(self.supports)
        support_num = list(range(num_supports))

        for support in self.supports:
            if support.supportnum in support_num:
                support_num.remove(support.supportnum)

        # for support in self.supports:
        #     if support.supportnum not in support_num:
        #         support.supportnum = support_num[0]
        #         support_num.pop(0)

        for index, element in enumerate(self.elements):
            element.id = index

    def lookupNodefromIDnum(self, idnum):
        for node in self.nodes:
            if node.idnum == idnum:
                return node

    def _singleFixedBeamHandler(self):
        if len(self.elements) == 1 and (len(self.supports) == 2 and isinstance(self.supports[0], FixedSupport) and isinstance(self.supports[1], FixedSupport)):
            self.nodes.insert(1,
                Node((self.elements[0].i_Node.x + self.elements[0].j_Node.x) / 2,
                     (self.elements[0].i_Node.y + self.elements[0].j_Node.y) / 2, 1))
            self.nodes[2].idnum=2
            # FIXEDTODO add property copying logic that does not copy member end nodes i guess
            subelems: list[GeneralFrameElement2D] = []
            subelems.append(ElementHelper.copyElementPropertiesSansNodes(self.elements[0]))
            subelems.append(ElementHelper.copyElementPropertiesSansNodes(self.elements[0]))
            subelems[0].i_Node = self.nodes[0]
            subelems[0].j_Node = self.nodes[1]
            self.elements.append(ElementHelper.copyElementPropertiesSansNodes(self.elements[0]))
            subelems[1].i_Node = self.nodes[1]
            subelems[1].j_Node = self.nodes[2]

            ElementHelper.subDivElementLoads(self.elements[0], subElems=subelems)
            self.elements = subelems

    def resultSummary(self):
        # TODO improve this
        summary = ">>>>>>>>>>>>>MODEL SUMMARY<<<<<<<<<<<<<\n"
        summary += "REACTIONS\n"
        for support in self.supports:
            summary += "Reaction at Support# "+str(support.supportnum)+" is "+str(support.reaction)+"\n"
        summary += "\n"
        summary += "NODAL DISPLACEMENTS\n"
        for node in self.nodes:
            summary += "Displacement at Node# " + str(node.idnum) + " is " + str(node.disp) + "\n"
        summary += "\n"
        summary += "NODAL FEM\n"
        for node in self.nodes:
            summary += "FEM at Node# "+str(node.idnum)+" is "+str(node.FEM)+"\n"

        return summary

    def reset(self, reset_type="soft"):
        for node in self.nodes:
            node.reset(reset_type)
        for support in self.supports:
            support.reset(reset_type)
        for element in self.elements:
            element.reset(reset_type)
