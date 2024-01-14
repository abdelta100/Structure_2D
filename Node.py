from Load import StaticLoad, PointLoad, Moment
from PrincipleForce import PrincipleForce


class Node:
    def __init__(self, x, y, idnum):
        self._idnum: int = idnum
        self._x: float = x
        self._y: float = y
        self._pos: tuple[float, float] = (x, y)
        # float for releases is proxy for stiffness. Maybe Check
        self.xActive: float = 1
        self.yActive: float = 1
        # self.zActive = True
        self.RxyActive: float = 1
        # self.RyzActive = True
        # self.RxzActive = True
        # TODO implement moment and displacement releases, maybe in the element
        self.nodalLoads: list[StaticLoad] = []
        self.FEM: PrincipleForce = PrincipleForce(0, 0, 0)
        self.netLoad: list[float] = [0, 0, 0]  # [Moment, Perp Reaction Force]
        self.disp: dict = {"Dx": 0, "Dy": 0, "Rxy": 0}
        self.nodalForces: dict = {"Fx": 0, "Fy": 0, "Mxy": 0}

    @property
    def idnum(self):
        return self._idnum

    @idnum.setter
    def idnum(self, idnum):
        self._idnum = idnum

    @property
    def pos(self):
        self._pos = (self.x, self.y)
        return self._pos

    @pos.setter
    def pos(self, position):
        self._x = position[0]
        self._y = position[1]
        self._pos = position

    @property
    def x(self):
        # return self.pos[0]
        return self._x

    @x.setter
    def x(self, x_):
        # self.pos=(x_, self.pos[1])
        self._x = x_

    @property
    def y(self):
        # return self.pos[1]
        return self._y

    @y.setter
    def y(self, y_):
        # self.pos = (self.pos[1], y_)
        self._y = y_

    def __repr__(self):
        selfrep = ("Node ID: " + str(self.idnum) + ' \n' +
                   "Coordinates: " + str(self.pos) + ' \n')
        return selfrep

    def addLoad(self, load: StaticLoad):
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

        Fx += self.FEM.fx
        Fy += self.FEM.fy
        Mxy += self.FEM.mxy
        # TODO check if the following line should contain load objects or just magnitude
        # TODO also see if i should use a dict object here or not
        self.netLoad = [Fx, Fy, Mxy]

    def pushNodalForces(self):
        pass
