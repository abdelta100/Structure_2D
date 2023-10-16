class Node:
    def __init__(self, x, y, idnum):
        self.idnum = idnum
        self.x = x
        self.y = y
        self._pos = (x, y)
        # float for releases is proxy for stiffness. Maybe Check
        self.xActive: float = 1
        self.yActive: float = 1
        # self.zActive = True
        self.RxyActive: float = 1
        # self.RyzActive = True
        # self.RxzActive = True
        # TODO implement moment and displacement releases, maybe in the element

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, x, y):
        self._pos = (x, y)

    def __repr__(self):
        selfrep = ("Node ID: " + str(self.idnum) + '\n' +
                   "Coordinates: " + str(self.pos) + '\n')
        return selfrep
