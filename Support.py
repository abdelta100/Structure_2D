from Node import Node


class Support(Node):
    def __init__(self, x, y, idnum, support_num, support_type:str='fixed'):
        super().__init__(x, y, idnum)
        self.supportnum: int = support_num
        self.reactions: dict={"Fx":0, "Fy":0, "Mxy":0}
        self.setDOF(support_type)

    @staticmethod
    def init_from_node(node: Node, support_num, support_type:str='fixed'):
        support = Support(node.x, node.y, node.idnum, support_num, support_type)
        return support

    def setDOF(self, support_type:str='fixed'):

        # TODO AMEND FOR DOF > 3, in 3D Frame

        if support_type.lower()=='fixed':
            self.xActive=1
            self.yActive=1
            self.RxyActive=1

        elif support_type.lower()=='pin':
            self.xActive=1
            self.yActive=1
            self.RxyActive=0
        elif support_type.lower()=='roller':
            self.xActive=0
            self.yActive=1
            self.RxyActive=0
        elif support_type.lower()=='roller-y':
            self.setDOF(support_type='roller')
        elif support_type.lower()=='roller-x':
            self.xActive=1
            self.yActive=0
            self.RxyActive=0
        elif support_type.lower()=='other':
            #TODO find a way to set other DOFs, such as partial or tilted supports
            self.setDOF(support_type='fixed')
        pass
