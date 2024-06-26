import matplotlib.pyplot as plt
import numpy as np

from Core.StructureGlobal import StructureGlobal


class StructureGlobalHelper:
    @staticmethod
    def plotNodalDisplacementGraph(structure: StructureGlobal):
        DxScale = 0.0005
        DyScale = 0.0005
        RxyScale = 1
        maxDxScale = 3
        maxDyScale = 3

        allElemDisp = []
        base_pos = []

        for element in structure.elements:
            x1 = element.i_Node.x
            x2 = element.j_Node.x
            y1 = element.i_Node.y
            y2 = element.j_Node.y
            dx1 = element.i_Node.disp.dx
            dx2 = element.j_Node.disp.dx
            dy1 = element.i_Node.disp.dy
            dy2 = element.j_Node.disp.dy
            # TODO implement the following later

            # Rxy1 = element.i_Node.y + DxScale * element.i_Node.disp['Dy']
            # Rxy2 = element.j_Node.y + DxScale * element.j_Node.disp['Dy']
            allElemDisp.append([dx1, dx2, dy1, dy2])
            base_pos.append([x1, x2, y1, y2])
        allElemDisp = StructureGlobalHelper.normalizeDisp(allElemDisp, base_pos, maxDxScale, maxDyScale)
        return allElemDisp

    @staticmethod
    def graphNodalDisplacementGraph(structure):
        allElemDisp = StructureGlobalHelper.plotNodalDisplacementGraph(structure)
        # print(allElemDisp)
        for element in allElemDisp:
            plt.plot(element[0], element[1], '-b')
        # plt.plot(x, y)
        # plt.plot([0, elements[1].length], [0, 0])
        plt.show()

    @staticmethod
    def normalizeDisp(allDisp, base_pos, maxDxScale, maxDyScale, split_axes=False):
        """
        Normalizes the displacements returned from analysis so that the values given to displacement structure plotter
        are proportional to their true magnitudes and represent the deformed shape adequately.

        :rtype: list[list[float, float], list[float, float]]
        :param allDisp: Deltas collected for each node of each element from analysis list[[dx1, dx2],[dy1,dy2]]
        :param base_pos: Original x, y positions for each end node for each element list[[x1, x2],[y1,y2]]
        :param maxDxScale: Maximum allowed value of normalized x-displacements
        :param maxDyScale: Maximum allowed value of normalized y-displacements
        :return:
        """
        disparray=np.array(allDisp)
        absdisparray = np.abs(disparray)
        print(absdisparray[0, 1])
        x_max = np.max(absdisparray[:, 0])
        x_max = max(x_max, float(absdisparray[0, 1]), float(absdisparray[-1, 1]))
        y_max = np.max(absdisparray[:, 2])
        y_max = max(y_max, float(absdisparray[0, 3]), float(absdisparray[-1, 3]))
        # print(x_max)
        # print(y_max)
        if not split_axes:
            absolute_max=max(x_max, y_max)
            x_max = absolute_max
            y_max = absolute_max

        unitScaledDisp = np.array([maxDxScale / x_max, maxDxScale / x_max, maxDyScale / y_max, maxDyScale / y_max])
        scaledDisp = disparray * unitScaledDisp
        totaldisp = np.array(base_pos) + scaledDisp
        python_list = np.ndarray.tolist(totaldisp)

        formatted_list = [[[i[0], i[1]], [i[2], i[3]]] for i in python_list]
        return formatted_list
