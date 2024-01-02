import copy
import math


class PrincipleForce:
    def __init__(self, Fx, Fy, Mxy):
        self._Fx = Fx
        self._Fy = Fy
        self._Mxy = Mxy

    def __add__(self, other):
        # TODO find a more elegant solution idk
        return PrincipleForce(Fx=self.fx + other.fx, Fy=self.fy + other.fy, Mxy=self.mxy + other.mxy)

    def __sub__(self, other):
        # TODO find a more elegant solution idk
        return PrincipleForce(Fx=self.fx - other.fx, Fy=self.fy - other.fy, Mxy=self.mxy - other.mxy)

    def __neg__(self):
        return PrincipleForce(Fx=-self.fx, Fy=-self.fy, Mxy=-self.mxy)

    def __str__(self):
        representation= {"Fx": self.fx, "Fy": self.fy, "Mxy": self.mxy}
        return str(representation)

    def transform(self, angle):
        xComp = self.fy * math.sin(angle) + self.fx * math.cos(angle)
        yComp = self.fy * math.cos(angle) + self.fx * math.sin(angle)
        return xComp, yComp

    def transformSelf(self, angle):
        xComp, yComp=self.transform(angle)
        self.fx = xComp
        self.fy = yComp

    def returnTransformed(self, angle):
        xComp, yComp = self.transform(angle)
        # multiplied by to avoid passing by reference
        mxy = self.mxy*1.0
        return PrincipleForce(xComp, yComp, mxy)

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
