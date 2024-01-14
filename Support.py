from Node import Node


# class Support(Node):
# Removed subclassing from node for now
class Support(Node):
    def __init__(self, node, support_num, support_type: str = 'fixed'):
        self.node = node
        x_=node.x
        y_=node.y
        in_=node.idnum
        super().__init__(x_, y_, in_)
        self.supportnum: int = support_num
        self.reactions: dict = {"Fx": 0, "Fy": 0, "Mxy": 0}
        self.setDOF(support_type)
        self.node = node

    #TODO should be deprecated
    @staticmethod
    def init_from_node(node: Node, support_num, support_type: str = 'fixed'):
        support = Support(node, support_num, support_type)
        return support

    def setDOF(self, support_type: str = 'fixed'):

        # TODO AMEND FOR DOF > 3, in 3D Frame

        if support_type.lower() == 'fixed':
            self.xActive = 1
            self.yActive = 1
            self.RxyActive = 1

        elif support_type.lower() == 'pin':
            self.xActive = 1
            self.yActive = 1
            self.RxyActive = 0
        elif support_type.lower() == 'roller':
            self.xActive = 0
            self.yActive = 1
            self.RxyActive = 0
        elif support_type.lower() == 'roller-y':
            self.setDOF(support_type='roller')
        elif support_type.lower() == 'roller-x':
            self.xActive = 1
            self.yActive = 0
            self.RxyActive = 0
        elif support_type.lower() == 'other':
            # TODO find a way to set other DOFs, such as partial or tilted supports
            self.setDOF(support_type='fixed')
        pass

    @property
    def idnum(self):
        return self.node.idnum

    @property
    def x(self):
        x_ = self.node.x
        super().x = x_
        return x_

    @property
    def y(self):
        y_ = self.node.y
        super().y = y_
        return y_


class FixedSupport(Support):
    def __init__(self, node, support_num):
        super().__init__(node, support_num, support_type='fixed')

    def init_from_node(node: Node, support_num, support_type: str = 'fixed'):
        support = FixedSupport(node, support_num)
        return support


class RollerSupport(Support):
    def __init__(self, node, support_num):
        super().__init__( node, support_num, support_type='roller')

    def init_from_node(node: Node, support_num, support_type: str = 'roller'):
        support = RollerSupport(node, support_num)
        return support


class PinnedSupport(Support):
    def __init__(self, node, support_num):
        super().__init__(node, support_num, support_type='pin')

    def init_from_node(node: Node, support_num, support_type='pin'):
        support = PinnedSupport(node, support_num)
        return support
