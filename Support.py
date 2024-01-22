from Node import Node
from PrincipleForce import Reaction


# class Support(Node):
# TODO Remove subclassing from node?
class Support(Node):
    def __init__(self, node: Node, support_num: int, support_type: str = 'fixed'):
        """
        A class that returns a 2D support object, that can have a max of 3 fixities. Partial fixities not yet
        implemented.
        :rtype: Support
        :param node: Node object at which support exists.
        :param support_num: Manually assigned support ID number. Must be unique.
        :param support_type: string to identify which type of support this is. "Fixed", "Pinned", "Roller-x", "Roller-y"
        """
        self.node: Node = node
        x_ = node.x
        y_ = node.y
        in_ = node.idnum
        super().__init__(x_, y_, in_)
        self.supportnum: int = support_num
        self.reaction: Reaction = Reaction()
        self.setDOF(support_type)

    # TODO should be deprecated
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
    def __init__(self, node: Node, support_num: int):
        """
        Returns a Support that has full fixities in x and y displacement as well as xy rotation.
        :rtype: FixedSupport
        :param node: Node object at which support exists
        :param support_num: Manually assigned support ID number. Must be unique.
        """
        super().__init__(node, support_num, support_type='fixed')

    @staticmethod
    def init_from_node(node: Node, support_num, support_type: str = 'fixed'):
        support = FixedSupport(node, support_num)
        return support


class RollerSupport(Support):
    def __init__(self, node: Node, support_num: int):
        """
        Returns a Support that has full fixities in either x or y displacement. Rotation and translation in the other
        axis are free.
        :rtype: RollerSupport
        :param node: Node object at which support exists
        :param support_num: Manually assigned support ID number. Must be unique.
        """
        super().__init__(node, support_num, support_type='roller')

    @staticmethod
    def init_from_node(node: Node, support_num, support_type: str = 'roller'):
        support = RollerSupport(node, support_num)
        return support


class PinnedSupport(Support):
    def __init__(self, node: Node, support_num: int):
        """
        Returns a Support that has full fixities in x and y displacement. Rotation is free.
        :rtype: PinnedSupport
        :param node: Node object at which support exists
        :param support_num: Manually assigned support ID number. Must be unique.
        """
        super().__init__(node, support_num, support_type='pin')

    @staticmethod
    def init_from_node(node: Node, support_num, support_type='pin'):
        support = PinnedSupport(node, support_num)
        return support
