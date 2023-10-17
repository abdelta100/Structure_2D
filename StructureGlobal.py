import numpy as np

from Element import Element
from Node import Node
from Support import Support


class StructureGlobal:
    def __init__(self):
        self.nodes: list[Node] = []
        self.elements: list[Element] = []
        self.supports: list[Support] = []
        self.dof = 3

    def createGlobalStiffnessMatrix(self):
        # TODO implement Global Stiffness Matrix
        # transformedElementMatrices=[element.transformedMatrix for element in self.elements]
        globalStiffnessMatrix = np.zeros(shape=(len(self.nodes) * 3, len(self.nodes) * 3))
        for element in self.elements:
            i_node = element.i_Node.idnum
            j_node = element.i_Node.idnum
            for index, i in enumerate(i_node, j_node):
                for index2, j in enumerate(i_node, j_node):
                    globalStiffnessMatrix[i * self.dof:(i + 1) * self.dof,
                    j * self.dof:(j + 1) * self.dof] += element.transformedMatrix[
                                                        index * self.dof:(index + 1) * self.dof,
                                                        index2 * self.dof:(index2 + 1) * self.dof]
        return globalStiffnessMatrix

    def createPermutationMatrix(self):
        #fixity vector
        disp_vector=np.zeros(shape=(len(self.nodes)*self.dof))
        for support in self.supports:
            disp_vector[support.idnum: support.idnum+self.dof]=np.array([support.xActive, support.yActive, support.RxyActive])
        perm_order=np.argsort(disp_vector)
        permutation_matrix=np.zeros(shape=(disp_vector.shape[0], disp_vector.shape[0]))
        for i, j in zip(range(len(disp_vector)), perm_order):
            permutation_matrix[i, j] = 1
        return permutation_matrix


