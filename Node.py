from Load import Load, PointLoad, Moment


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
        self.nodalLoads: list[Load]=[]

    @property
    def pos(self):
        self._pos = (self.x, self.y)
        return self._pos

    @pos.setter
    def pos(self, position):
        self.x = position[0]
        self.y = position[1]
        self._pos = position

    def __repr__(self):
        selfrep = ("Node ID: " + str(self.idnum) + '\n' +
                   "Coordinates: " + str(self.pos) + '\n')
        return selfrep

    def addLoad(self, load: Load):
        self.nodalLoads.append(load)

    def combineLoads(self):
        combPointLoad=PointLoad(0, 0)
        combMomentLoad = Moment(0)
        for load in self.nodalLoads:
            if isinstance(load, PointLoad):
                combPointLoad+=load
            elif isinstance(load, Moment):
                combMomentLoad+=load

        return combPointLoad, combMomentLoad
