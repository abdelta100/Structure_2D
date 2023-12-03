from StructureGlobal import StructureGlobal


class StructureGlobalHelper:
    @staticmethod
    def plotNodalDisplacementGraph(structure: StructureGlobal):
        DxScale = 10
        DyScale = 300
        RxyScale = 1

        allElemDisp=[]

        for element in structure.elements:
            x1 = element.i_Node.x + DxScale * element.i_Node.disp['Dx']
            x2 = element.j_Node.x + DxScale * element.j_Node.disp['Dx']
            y1 = element.i_Node.y + DyScale * element.i_Node.disp['Dy']
            y2 = element.j_Node.y + DyScale * element.j_Node.disp['Dy']
            #TODO implement the following later

            # Rxy1 = element.i_Node.y + DxScale * element.i_Node.disp['Dy']
            # Rxy2 = element.j_Node.y + DxScale * element.j_Node.disp['Dy']

            allElemDisp.append([[x1, x2], [y1, y2]])
        return allElemDisp


        pass
