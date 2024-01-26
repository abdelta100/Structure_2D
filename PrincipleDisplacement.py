import math


class PrincipleDisplacement2D:
    def __init__(self, Dx: float = 0, Dy: float = 0, Rxy: float = 0):
        """
        A 2D Principle Displacement class. Holds all types of non-dependent displacements that can exist concurrently at a
        single point.
        X and Y Displacement, and XY Rotation in 2D, with respect to an arbitrary XY Plane.
        :rtype: PrincipleDisplacement2D
        :param Dx: Displacement in x-direction
        :param Dy: Displacement in y-direction
        :param Rxy: Rotation in xy-plane
        """
        self._Dx = Dx
        self._Dy = Dy
        self._Rxy = Rxy

    def __add__(self, other):
        # TODO find a more elegant solution idk
        return PrincipleDisplacement2D(Dx=self.dx + other.dx, Dy=self.dy + other.dy, Rxy=self.rxy + other.rxy)

    def __sub__(self, other):
        # TODO find a more elegant solution idk
        return PrincipleDisplacement2D(Dx=self.dx - other.dx, Dy=self.dy - other.dy, Rxy=self.rxy - other.rxy)

    def __neg__(self):
        return PrincipleDisplacement2D(Dx=-self.dx, Dy=-self.dy, Rxy=-self.rxy)

    def __str__(self):
        representation = {"Dx": self.dx, "Dy": self.dy, "Rxy": self.rxy}
        return str(representation)

    def __len__(self):
        # FOR 2D Only
        return 3

    def transform(self, angle):
        xComp = self.dy * math.sin(angle) + self.dx * math.cos(angle)
        yComp = self.dy * math.cos(angle) + self.dx * math.sin(angle)
        return xComp, yComp

    def transformSelf(self, angle):
        xComp, yComp = self.transform(angle)
        self.dx = xComp
        self.dy = yComp

    def returnTransformed(self, angle):
        xComp, yComp = self.transform(angle)
        # multiplied by to avoid passing by reference
        mxy = self.rxy * 1.0
        return PrincipleDisplacement2D(xComp, yComp, mxy)

    def tolist(self):
        return [self.dx, self.dy, self.rxy]

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


class NodalDisplacement(PrincipleDisplacement2D):
    def __int__(self, Dx: float = 0, Dy: float = 0, Rxy: float = 0):
        """
        A 2D Principle Displacement class. Holds all types of non-dependent displacements at a Node.
        X and Y Displacement, and XY Rotation in 2D, with respect to an arbitrary XY Plane.
        :rtype: NodalDisplacement
        :param Dx: Displacement in x-direction
        :param Dy: Displacement in y-direction
        :param Rxy: Rotation in xy-plane
        """
        super().__init__(Dx, Dy, Rxy)
