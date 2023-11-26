from abc import ABC

from AuxillaryFunctions import *


class Load(ABC):
    def __init__(self, magnitude: float = 0, local=False):
        self.loadClass: str = "None"
        self.name: str = "None"
        self.beamLength: float = 1
        # TODO implement local and global load application

    def calcCentroid(self) -> float:
        pass

    def calcTotal(self) -> float:
        pass

    def calcFixedEndReactions(self) -> list[float]:
        pass

    def cleanInputs(self):
        # TODO deal with either repeating code or adding unknown variables
        if self.start < 0: self.start = 0
        if self.start > self.beamLength: self.start = self.beamLength
        if self.end > self.beamLength: self.end = self.beamLength
        if self.end < 0: self.end = 0
        if self.start > self.end: self.end = self.start


class UniformDistributedLoad(Load):
    def __init__(self, magnitude, start_location, end_location):
        super().__init__()
        self.loadClass = "Uniformly Distributed Load"
        self.magnitude = magnitude
        self.start = start_location
        self.end = end_location
        self.beamLength = 1

    def calcTotal(self):
        return self.magnitude * (self.end - self.start)

    def calcCentroid(self):
        return (self.end + self.start) / 2

    def calcFixedEndReactions(self):
        dist = (self.end - self.start)
        mid = self.calcCentroid()
        length = self.beamLength
        dN1 = mid
        dN2 = length - mid
        R1 = (dN1 * (dN2 ** 2) + ((dN1 - 2 * dN2) * dist ** 2) / 12) * (self.magnitude * dist) / length ** 2
        R2 = -(dN2 * (dN1 ** 2) + ((dN2 - 2 * dN1) * dist ** 2) / 12) * (self.magnitude * dist) / length ** 2
        V1 = -((2 * dN1 + length) * dN2 ** 2 + ((dN1 - dN2) / 4) / dist ** 2) * (self.magnitude * dist) / length ** 3
        V2 = -((2 * dN2 + length) * dN1 ** 2 - ((dN1 - dN2) / 4) / dist ** 2) * (self.magnitude * dist) / length ** 3

        # V2 = R1 + R2 + self.calcTotal() * mid / length
        # V1 = self.calcTotal() - V2

        return R1, R2, V1, V2


class PointLoad(Load):
    def __init__(self, magnitude, angle_degree=0, local=False):
        super().__init__()
        self.loadClass = "Point Load"
        self.magnitude = magnitude
        # TODO implement rad to degree?
        self.angle: float = degree2rad(angle_degree)

    def getComponents(self):
        c = math.cos(self.angle)
        s = math.sin(self.angle)

        # TODO added to manually force zeros
        zerolim = 10E-9
        if -zerolim < c < zerolim:
            c = 0
        if -zerolim < s < zerolim:
            s = 0
        selfx = self.magnitude * c
        selfy = self.magnitude * s

        return selfx, selfy

    def __add__(self, other):
        if isinstance(other, PointLoad):
            selfx, selfy = self.getComponents()
            otherx, othery = other.getComponents()

            combx = selfx + otherx
            comby = selfy + othery

            combmag = math.sqrt(combx ** 2 + comby ** 2)
            combangle = math.atan2(comby, combx)

            newPointLoad = PointLoad(combmag, angle_degree=rad2degree(combangle))

            return newPointLoad
        else:
            # TODO check what exception to throw
            # raise Exception
            return self

    def calcTotal(self):
        return self.magnitude


class PointLoadMember(PointLoad):
    def __init__(self, magnitude, location):
        super().__init__(magnitude)
        self.location = location
        # TODO jugar fix this
        self.beamLength = 10

    def calcCentroid(self):
        return self.location

    def calcFixedEndReactions(self):
        # TODO amend for axial force too
        length = self.beamLength
        dN1 = self.location
        dN2 = length - dN1

        V1 = -(3 * dN1 + dN2) * self.magnitude * dN2 ** 2 / length ** 3
        V2 = -(3 * dN2 + dN1) * self.magnitude * dN1 ** 2 / length ** 3
        R1 = self.magnitude * dN1 * dN2 ** 2 / length ** 2
        R2 = -self.magnitude * dN2 * dN1 ** 2 / length ** 2

        return R1, R2, V1, V2


class VaryingDistributedLoad(Load):
    def __init__(self, start_magniude, end_magnitude, start_location, end_location):
        super().__init__()
        self.loadClass = "Varying Distributed Load"
        self.start_magnitude = start_magniude
        self.end_magnitude = end_magnitude
        self.start = start_location
        self.end = end_location

    def calcCentroid(self):
        dist = self.end - self.start

        rect_centr = (self.end + self.start) / 2
        rect_weight = self.start_magnitude * dist

        tri_centr = (2 / 3) * dist + self.start
        tri_weight = (1 / 2) * dist * (self.end_magnitude - self.start_magnitude)

        centr = (rect_centr * rect_weight + tri_centr * tri_weight) / self.calcTotal()
        return centr

    def calcTotal(self):
        total = (self.end - self.start) * (self.end_magnitude + self.start_magnitude) / 2
        return total

    def calcFixedEndReactions(self):
        # TODO either find complete formula, or restrict case to start at 0 and end at L
        pass


class Moment(Load):
    def __init__(self, magnitude):
        super().__init__(magnitude)
        self.loadClass = "Moment"
        self.magnitude = magnitude

    def calcTotal(self):
        return self.magnitude

    def __add__(self, other):
        if isinstance(other, Moment):
            return self.magnitude + other.magnitude
        else:
            # TODO check what exception to throw
            # raise Exception
            return self


class MomentMember(Moment):
    # TODO figure moment fem transfer in case moment is not at node
    def __init__(self, magnitude, location):
        super().__init__(magnitude)
        self.location = location

    def calcCentroid(self):
        return self.location

    def toNode(self):
        pass
