class SupportRelease2D:
    def __init__(
            self,
            Dx: float = 1,
            Dy: float = 1,
            Rxy: float = 1):
        """
        A 2D Support Node Release Class. Holds values of allowed releases a  node of a 2D support element.
        X and Y Displacement, and XY Rotation in 2D, with respect to an arbitrary XY Plane.
        1 is fixed, 0 is released
        :rtype: SupportRelease2D
        :param Dx: Force release in x-direction at i-node
        :param Dy: Force release in y-direction at i-node
        :param Rxy: Moment release in xy-plane at i-node
        """
        self._Dx = Dx
        self._Dy = Dy
        self._Rxy = Rxy

    def tolist(self):
        return [self.dx, self.dy, self.rxy]

    @staticmethod
    def init_from_array(releaseList: list[int]):
        for i in releaseList:
            if i < 0 or i > 1 or type(i) is not int:
                ValueError("Entries of release list should be either 0 or 1")

        release = SupportRelease2D(
            Dx=releaseList[0],
            Dy=releaseList[1],
            Rxy=releaseList[2])

        return release

    @property
    def dx(self):
        return self._Dx

    @dx.setter
    def dx(self, Dx):
        self._Dx = Dx

    @property
    def dy(self):
        return self._Dy

    @dy.setter
    def dy(self, Dy):
        self._Dy = Dy

    @property
    def rxy(self):
        return self._Rxy

    @rxy.setter
    def rxy(self, Rxy):
        self._Rxy = Rxy
