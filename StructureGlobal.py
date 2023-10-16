import numpy as np

from Element import Element
from Node import Node


class StructureGlobal:
    def __init__(self):
        self.nodes: list[Node] = []
        self.elements: list[Element] = []
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
        pass
