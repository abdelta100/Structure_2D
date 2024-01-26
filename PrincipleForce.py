import math


class PrincipleForce2D:
    def __init__(self, Fx: float = 0, Fy: float = 0, Mxy: float = 0):
        """
        A 2D Principle Force class. Holds all types of non-dependent forces that can exist concurrently at a
        single point.
        X and Y Forces, and XY Moment in 2D, with respect to an arbitrary XY Plane.
        :rtype: PrincipleForce2D
        :param Fx: Force in x-direction
        :param Fy: Force in y-direction
        :param Mxy: Moment in xy-plane
        """
        self._Fx = Fx
        self._Fy = Fy
        self._Mxy = Mxy

    def __add__(self, other):
        # TODO find a more elegant solution idk
        return PrincipleForce2D(Fx=self.fx + other.fx, Fy=self.fy + other.fy, Mxy=self.mxy + other.mxy)

    def __sub__(self, other):
        # TODO find a more elegant solution idk
        return PrincipleForce2D(Fx=self.fx - other.fx, Fy=self.fy - other.fy, Mxy=self.mxy - other.mxy)

    def __neg__(self):
        return PrincipleForce2D(Fx=-self.fx, Fy=-self.fy, Mxy=-self.mxy)

    def __str__(self):
        representation = {"Fx": self.fx, "Fy": self.fy, "Mxy": self.mxy}
        return str(representation)

    def __len__(self):
        #FOR 2D Only
        return 3

    def transform(self, angle):
        xComp = self.fy * math.sin(angle) + self.fx * math.cos(angle)
        yComp = self.fy * math.cos(angle) + self.fx * math.sin(angle)
        return xComp, yComp

    def transformSelf(self, angle):
        xComp, yComp = self.transform(angle)
        self.fx = xComp
        self.fy = yComp

    def returnTransformed(self, angle):
        xComp, yComp = self.transform(angle)
        # multiplied by to avoid passing by reference
        mxy = self.mxy * 1.0
        return PrincipleForce2D(xComp, yComp, mxy)

    def tolist(self):
        return [self.fx, self.fy, self.mxy]

    @property
    def fx(self):
        return self._Fx

    @fx.setter
    def fx(self, Fx):
        self._Fx = Fx

    @property
    def fy(self):
        return self._Fy

    @fy.setter
    def fy(self, Fy):
        self._Fy = Fy

    @property
    def mxy(self):
        return self._Mxy

    @mxy.setter
    def mxy(self, Mxy):
        self._Mxy = Mxy


class FEM(PrincipleForce2D):
    def __init__(self, Fx: float = 0, Fy: float = 0, Mxy: float = 0):
        """
        Functionally the same as a 2D Principle Force class. Holds Fixed End Moments/Reactions at a node.
        X and Y Reactions, and XY Moment in 2D, with respect to an arbitrary XY Plane.
        :rtype: PrincipleForce2D
        :param Fx: FEM Force in x-direction
        :param Fy: FEM Force in y-direction
        :param Mxy: FEM Moment in xy-plane
        """
        super().__init__(Fx, Fy, Mxy)


class Reaction(PrincipleForce2D):
    def __init__(self, Fx: float = 0, Fy: float = 0, Mxy: float = 0):
        """
        Functionally the same as a 2D Principle Force class. Holds reactions at a support.
        X and Y Reactions, and XY Moment in 2D, with respect to an arbitrary XY Plane.
        :rtype: PrincipleForce2D
        :param Fx: Reaction Force in x-direction
        :param Fy: Reaction Force in y-direction
        :param Mxy: Reaction Moment in xy-plane
        """
        super().__init__(Fx, Fy, Mxy)
