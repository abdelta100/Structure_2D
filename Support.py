from Node import Node


class Support(Node):
    def __init__(self, x, y, idnum, support_num):
        super().__init__(x, y, idnum)
        self.supportnum = support_num

    @staticmethod
    def init_from_node(node: Node, support_num):
        support = Support(node.x, node.y, node.idnum, support_num)
        return support
