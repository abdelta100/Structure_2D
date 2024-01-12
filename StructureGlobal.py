import numpy as np

from AuxillaryFunctions import matrixStabilityCheck
from Element import Element
from ElementHelperFunctions import ElementHelper
from Load import StaticLoad
from Node import Node
from Support import Support


class StructureGlobal:
    def __init__(self):
        self.nodes: list[Node] = []
        self.elements: list[Element] = []
        self.supports: list[Support] = []
        self.loads: list[StaticLoad] = []
        self.stiffnessMatrix: np.array = np.zeros(shape=(len(self.nodes) * 3, len(self.nodes) * 3))
        self.dof = 3

    def createGlobalStiffnessMatrix(self):
        # TODO include element node releases or something
        # transformedElementMatrices=[element.transformedMatrix for element in self.elements]
        globalStiffnessMatrix = np.zeros(shape=(len(self.nodes) * 3, len(self.nodes) * 3), dtype=np.float64)
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
                [support.xActive, support.yActive, support.RxyActive])
        perm_order = np.argsort(disp_vector)
        permutation_matrix = np.zeros(shape=(disp_vector.shape[0], disp_vector.shape[0]))
        for i, j in zip(range(len(disp_vector)), perm_order):
            permutation_matrix[i, j] = 1
        return permutation_matrix, np.matmul(permutation_matrix, disp_vector)

    def _solver(self):
        # TODO handle single beam edge case or similar
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
        appLoads = np.zeros(shape=len(self.nodes) * 3)
        for node in self.nodes:
            # TODO reconcile self.dof and len netload,
            # both should be same but different variables are referenced may cause issue
            appLoads[node.idnum * self.dof:node.idnum * self.dof + len(node.netLoad)] = node.netLoad

        orderedLoads = np.matmul(permutationMatrix, appLoads)
        return orderedLoads

    def _pushDisplacements(self, orderedDispVector, permutationMatrix):
        # TODO future issue here. If my internal nodes are not fixed in some dof, I might have to transfer my nodal
        #  loads (received from analysis) back to nodes, and draw sfd etc from that
        origOrderDisplacement = np.matmul(permutationMatrix.T, orderedDispVector)
        for node in self.nodes:
            tempdisp = origOrderDisplacement[node.idnum * self.dof:(node.idnum + 1) * self.dof]
            # transformedtemdisp=np.matmul(nod)
            node.disp["Dx"] = tempdisp[0]
            node.disp["Dy"] = tempdisp[1]
            node.disp["Rxy"] = tempdisp[2]

    def _pushReactions(self, orderedForceVector, permutationMatrix):
        # TODO figure out force/reaction push details since i'm not pushing anything to nodes here, just supports
        origOrderForce = np.matmul(permutationMatrix.T, orderedForceVector)

        for support in self.supports:
            tempforce = origOrderForce[support.idnum * self.dof:(support.idnum + 1) * self.dof]
            support.reactions["Fx"] = tempforce[0]
            support.reactions["Fy"] = tempforce[1]
            support.reactions["Mxy"] = tempforce[2]

    def runAnalysis(self):
        self._structureModelIntegrityChecker()
        self._singleFixedBeamHandler()
        self._solver()

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
        if len(self.elements) == 1:
            self.nodes.append(
                Node((self.elements[0].i_Node.x + self.elements[0].j_Node.x) / 2,
                     (self.elements[0].i_Node.y + self.elements[0].j_Node.y) / 2, 2))
            # TODO add property copying logic that does not copy member end nodes i guess
            subelems: list[Element] = []
            subelems.append(ElementHelper.copyElementPropertiesSansNodes(self.elements[0]))
            subelems.append(ElementHelper.copyElementPropertiesSansNodes(self.elements[0]))
            subelems[0].i_Node = self.nodes[0]
            subelems[0].j_Node = self.nodes[2]
            self.elements.append(ElementHelper.copyElementPropertiesSansNodes(self.elements[0]))
            subelems[0].i_Node = self.nodes[2]
            subelems[0].j_Node = self.nodes[1]

            ElementHelper.subDivElementLoads(self.elements[0], subElems=subelems)
            self.elements = subelems
        pass
