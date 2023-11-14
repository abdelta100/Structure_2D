import numpy as np

from Element import Element
from Load import Load
from Node import Node
from Support import Support


class StructureGlobal:
    def __init__(self):
        self.nodes: list[Node] = []
        self.elements: list[Element] = []
        self.supports: list[Support] = []
        self.loads: list[Load] = []
        self.stiffnessMatrix: np.array = np.zeros(shape=(len(self.nodes) * 3, len(self.nodes) * 3))
        self.dof = 3

    def createGlobalStiffnessMatrix(self):
        # TODO implement Global Stiffness Matrix
        # TODO guves an error, all entries are null for some reason
        # transformedElementMatrices=[element.transformedMatrix for element in self.elements]
        globalStiffnessMatrix = np.zeros(shape=(len(self.nodes) * 3, len(self.nodes) * 3))
        for element in self.elements:
            i_node = element.i_Node.idnum
            j_node = element.j_Node.idnum
            for index, i in enumerate((i_node, j_node)):
                for index2, j in enumerate((i_node, j_node)):
                    globalStiffnessMatrix[i * self.dof:(i + 1) * self.dof, j * self.dof:(j + 1) * self.dof] += element.globalStiffnessMatrix[
                                                        index * self.dof:(index + 1) * self.dof,
                                                        index2 * self.dof:(index2 + 1) * self.dof]
        #TODO provide option to return just the stiffness witout running the solver, or maybe a model build?
        return globalStiffnessMatrix

    def createPermutationMatrix(self):
        #fixity vector
        disp_vector=np.zeros(shape=(len(self.nodes)*self.dof))
        for support in self.supports:
            #edit Line when going 3D
            disp_vector[support.idnum*self.dof: (support.idnum+1)*self.dof]=np.array([support.xActive, support.yActive, support.RxyActive])
        perm_order=np.argsort(disp_vector)
        permutation_matrix=np.zeros(shape=(disp_vector.shape[0], disp_vector.shape[0]))
        for i, j in zip(range(len(disp_vector)), perm_order):
            permutation_matrix[i, j] = 1
        return permutation_matrix, np.matmul(permutation_matrix,disp_vector)

    def solver(self):
        #TODO permutation matrix needs to be created by factoring in Supports not just nodes
        permutationMatrix, permutatedOrder=self.createPermutationMatrix()
        globalStiffness=self.createGlobalStiffnessMatrix()
        permutedMatrix=np.matmul(permutationMatrix, np.matmul(globalStiffness, permutationMatrix.T))
        fixed_index=np.where(permutatedOrder==1)[0][0]

        # | UU      UK |
        # | KU      KK |

        UU = permutedMatrix[:fixed_index, :fixed_index]
        UK = permutedMatrix[:fixed_index, fixed_index:]
        KU = permutedMatrix[fixed_index:, :fixed_index]
        KK = permutedMatrix[fixed_index:, fixed_index:]

        # | FK |
        # | FU |

        #TODO work out what index works here, current config gives FU as known instead of FK

        permutatedAppliedLoads=self.orderAppliedLoads(permutationMatrix)
        FK=permutatedAppliedLoads[:fixed_index]
        FU=permutatedAppliedLoads[fixed_index:]

        # | DU |
        # | DK |

        orderedDisplacementVector=np.zeros(shape=permutatedAppliedLoads.shape)
        DU = orderedDisplacementVector[:fixed_index]
        DK = orderedDisplacementVector[fixed_index:]

        # FK = UU*DU + UK * DK
        # DK zero by definition (not specific case yet where spring deformation)
        # DU = (FK - UK*DK) * UU.inv
        # FU = KU*DU + KK * DK

        DU = np.matmul(FK-np.matmul(UK, DK), np.linalg.inv(UU))
        FU = np.matmul(KU, DU) + np.matmul(KK, DK)

        filledDisplacementVector=np.concatenate((DU, DK), axis=0)
        filledForceVector=np.concatenate((FK, FU), axis=0)

        self.pushDisplacements(filledDisplacementVector, permutationMatrix)
        self.pushReactions(filledForceVector, permutationMatrix)


        #TODO involve displacement vector



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
        appLoads = np.zeros(shape=len(self.nodes)*3)
        for node in self.nodes:
            # TODO reconcile self.dof and len netload,
            #both should be same but different variables are referenced may cause issue
            appLoads[node.idnum*self.dof:node.idnum*self.dof + len(node.netLoad)] = node.netLoad

        orderedLoads=np.matmul(appLoads, permutationMatrix)
        return orderedLoads

    def pushDisplacements(self, orderedDispVector, permutationMatrix):
        origOrderDisplacement=np.matmul(orderedDispVector, np.linalg.inv(permutationMatrix))
        for node in self.nodes:
            tempdisp=origOrderDisplacement[node.idnum*self.dof:(node.idnum+1)*self.dof]
            node.disp["Dx"]=tempdisp[0]
            node.disp["Dy"] = tempdisp[1]
            node.disp["Rxy"] = tempdisp[2]

    def pushReactions(self, orderedForceVector, permutationMatrix):
        origOrderForce = np.matmul(orderedForceVector, np.linalg.inv(permutationMatrix))
        for support in self.supports:
            tempforce = origOrderForce[support.idnum:support.idnum+self.dof]
            support.reactions["Fx"] = tempforce[0]
            support.reactions["Fy"] = tempforce[1]
            support.reactions["Mxy"] = tempforce[2]





