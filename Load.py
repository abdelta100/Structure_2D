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
        # TODO think of moving this outside
        if isinstance(self, TrapezoidalDistributedLoad):
            for vdl in self.VDLset:
                vdl.beamLength=self.beamLength
                vdl.cleanInputs()
        else:
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
        R1 = -(dN1 * (dN2 ** 2) + ((dN1 - 2 * dN2) * dist ** 2) / 12) * (self.magnitude * dist) / length ** 2
        R2 = +(dN2 * (dN1 ** 2) + ((dN2 - 2 * dN1) * dist ** 2) / 12) * (self.magnitude * dist) / length ** 2

        # Following two lines provide incorrect result for fixed end shear
        # Ve1 = -((2 * dN1 + length) * dN2 ** 2 + ((dN1 - dN2) / 4) / dist ** 2) * (self.magnitude * dist) / length ** 3
        # Ve2 = -((2 * dN2 + length) * dN1 ** 2 - ((dN1 - dN2) / 4) / dist ** 2) * (self.magnitude * dist) / length ** 3

        V2 = -(R1 + R2 + self.calcTotal() * mid) / length
        V1 = -self.calcTotal() - V2

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

        # s1=pre_dist
        # s2=dist
        # s3=post_dist
        # refactor later
        s2 = self.end - self.start
        s1 = self.start - 0
        s3 = self.beamLength - self.end

        # Split into a triangular load and a rectangular load
        # Triangular Load
        tri_mag = self.end_magnitude - self.start_magnitude

        # Foloowing Formulae for R1 and R2, referenced from an eng-tip site
        # https://www.eng-tips.com/viewthread.cfm?qid=413577
        # Thanks to KootK, whoever he is, for saving me hours of algebra, which he probably did before I was even born
        # minus switched to maintain convention

        R1 = -(1 / 60) * tri_mag * s2 * (
                (2 * s2 ** 3) + (5 * s2 ** 2) * s1 + (20 * s3 ** 2) * s2 + (
                30 * s3 ** 2) * s1 + (10 * s2 ** 2) * s3 + (
                        20 * s1 * s2 * s3)) / (s1 + s2 + s3) ** 2
        R2 = (1 / 60) * tri_mag * s2 * (
                (3 * s2 ** 3) + (15 * s2 ** 2) * s3 + (10 * s1 ** 2) * s2 + (
                30 * s1 ** 2) * s3 + (10 * s2 ** 2) * s1 + (
                        40 * s1 * s2 * s3)) / (s1 + s2 + s3) ** 2

        V2 = -(R1 + R2 + self.calcTotal() * self.calcCentroid()) / self.beamLength
        V1 = -self.calcTotal() - V2

        # Temporary rectangular load to handle rectangular portion calculation

        temprect = UniformDistributedLoad(self.start_magnitude, self.start, self.end)
        temprect.beamLength = self.beamLength

        tR1, tR2, tV1, tV2 = temprect.calcFixedEndReactions()

        R1 += tR1
        R2 += tR2
        # V1 += tV1
        # V2 += tV2

        del temprect

        V2 = -(R1 + R2 + self.calcTotal() * self.calcCentroid()) / self.beamLength
        V1 = -self.calcTotal() - V2

        return R1, R2, V1, V2


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


class TrapezoidalDistributedLoad(VaryingDistributedLoad):

    def __init__(self, location_list: list[float], magnitude_list: list[float]):
        self.loadClass = "Trapezoidal Distributed Load"
        self.VDLset: list[VaryingDistributedLoad] = []
        self.inputIntegrityCheck(location_list, magnitude_list)
        self.initializeVDLset(location_list, magnitude_list)
        pass

    def initializeVDLset(self, location_list, magnitude_list):
        for index in range(len(location_list)-1):
            self.VDLset.append(
                VaryingDistributedLoad(magnitude_list[index], magnitude_list[index + 1],
                                       location_list[index], location_list[index + 1]))

    def inputIntegrityCheck(self, location_list, magnitude_list):
        if len(location_list) != len(magnitude_list):
            print("Location and Magnitude points are not equal. A Magnitude must be provided for each Location listed")
            raise ValueError
        # TODO create checks for sequence ordering of locations
        # pass

    def calcFixedEndReactions(self):
        R1 = 0
        R2 = 0
        V1 = 0
        V2 = 0
        A1 = 0
        A2 = 0

        for vdl in self.VDLset:
            tR1, tR2, tV1, tV2 = vdl.calcFixedEndReactions()
            R1 += tR1
            R2 += tR2
            V1 += tV1
            V2 += tV2
            A1 += 0
            A2 += 0

        return R1, R2, V1, V2
