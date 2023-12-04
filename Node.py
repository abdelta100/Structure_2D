from Load import Load, PointLoad, Moment


class Node:
    def __init__(self, x, y, idnum):
        self.idnum: int = idnum
        self.x: float = x
        self.y: float = y
        self._pos: tuple[float, float] = (x, y)
        # float for releases is proxy for stiffness. Maybe Check
        self.xActive: float = 1
        self.yActive: float = 1
        # self.zActive = True
        self.RxyActive: float = 1
        # self.RyzActive = True
        # self.RxzActive = True
        # TODO implement moment and displacement releases, maybe in the element
        self.nodalLoads: list[Load] = []
        self.FEM: list[float] = [0, 0, 0]
        self.netLoad: list[float] = [0, 0, 0]  # [Moment, Perp Reaction Force]
        self.disp: dict = {"Dx":0, "Dy":0, "Rxy":0}
        self.nodalForces: dict = {"Fx":0, "Fy":0, "Mxy":0}

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

    def combineTransferredLoads(self):
        combPointLoad = PointLoad(0, 0)
        combMomentLoad = Moment(0)
        for load in self.nodalLoads:
            if isinstance(load, PointLoad):
                combPointLoad += load
            elif isinstance(load, Moment):
                combMomentLoad += load

                # TODO deal with 2 different axes for point loads

        return combPointLoad, combMomentLoad

    def combineAllLoads(self):
        combPointLoad, combMomentLoad = self.combineTransferredLoads()
        Fx, Fy = combPointLoad.getComponents()
        Mxy = combMomentLoad.magnitude

        Fx += self.FEM[0]
        Fy += self.FEM[1]
        Mxy += self.FEM[2]
        #TODO check if the following line should contain load objects or just magnitude
        #TODO also see if i should use a dict object here or not
        self.netLoad = [Fx, Fy, Mxy]

    def pushNodalForces(self):
        pass
