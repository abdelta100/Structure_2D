from abc import ABC

from AuxillaryFunctions import *
from PrincipleForce import PrincipleForce


class StaticLoad(ABC):
    def __init__(self, magnitude: float = 0, local=False):
        self.loadClass: str = "None"
        self.name: str = "None"
        self.beamLength: float = 1
        # TODO implement local and global load application

    def setBeamLength(self, length):
        # TODO add property handlers idk
        self.beamLength = length

    def calcCentroid(self) -> float:
        pass

    def calcTotal(self) -> float:
        pass

    def calcFixedEndReactions(self) -> tuple[PrincipleForce, PrincipleForce]:
        pass

    def cleanInputs(self):
        # TODO deal with either repeating code or adding unknown variables
        # TODO think of moving this outside
        if isinstance(self, TrapezoidalDistributedLoad):
            for vdl in self.VDLset:
                vdl.beamLength = self.beamLength
                vdl.cleanInputs()
        else:
            if self.start < 0: self.start = 0
            if self.start > self.beamLength: self.start = self.beamLength
            if self.end > self.beamLength: self.end = self.beamLength
            if self.end < 0: self.end = 0
            if self.start > self.end: self.end = self.start

    def magnitudeAtPoint(self, point):
        pass


class UniformDistributedLoad(StaticLoad):
    def __init__(self, magnitude, start_location, end_location, angle=270):
        # TODO implement local reference load application and projected load application
        super().__init__()
        self.loadClass = "Uniformly Distributed Load"
        self.magnitude = magnitude
        self.start = start_location
        self.end = end_location
        self.beamLength = 1
        self.angle = degree2rad(angle)

    def calcTotal(self):
        return self.magnitude * (self.end - self.start)

    def calcCentroid(self):
        return (self.end + self.start) / 2

    def calcFixedEndReactions(self) -> tuple[PrincipleForce, PrincipleForce]:
        dist = (self.end - self.start)
        mid = self.calcCentroid()
        length = self.beamLength
        if dist == 0:
            return PrincipleForce(0, 0, 0), PrincipleForce(0, 0, 0)
        perp_magnitude = self.magnitude * math.sin(self.angle)
        dN1 = mid
        dN2 = length - mid
        R1 = +(dN1 * (dN2 ** 2) + ((dN1 - 2 * dN2) * dist ** 2) / 12) * (perp_magnitude * dist) / length ** 2
        R2 = -(dN2 * (dN1 ** 2) + ((dN2 - 2 * dN1) * dist ** 2) / 12) * (perp_magnitude * dist) / length ** 2

        V2 = -(R1 + R2 + self.calcTotal() * math.sin(self.angle) * mid) / length
        V1 = -self.calcTotal() * math.sin(self.angle) - V2

        # TODO maybe yoou dont need the centroid for the Axial part but the mean? or the thingy that splits a graph into
        # two equal areas
        par_magnitude_total = self.calcTotal() * math.cos(self.angle)
        A1 = -par_magnitude_total * dN2 / (dN2 + dN1)
        A2 = -par_magnitude_total * dN1 / (dN1 + dN2)

        iNodeFer = PrincipleForce(A1, V1, R1)
        jNodeFer = PrincipleForce(A2, V2, R2)

        return iNodeFer, jNodeFer

    def magnitudeAtPoint(self, point, axis='perpendicular'):
        # TODO returning magnitude for now, but issue with projections and loads at an angle etc
        if self.start <= point <= self.end:
            magnitude = {"perpendicular": self.magnitude * math.sin(self.angle),
                         "parallel": self.magnitude * math.cos(self.angle)}
            magnitude["abs"] = math.sqrt(magnitude["perpendicular"] ** 2 + magnitude["parallel"] ** 2)
            return magnitude[axis]

        else:
            return 0


class PointLoad(StaticLoad):
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
    def __init__(self, magnitude, location, angle=270):
        super().__init__(magnitude)
        self.location = location
        # TODO jugar fix this
        self.beamLength = 10
        self.angle = degree2rad(angle)

    def calcCentroid(self):
        return self.location

    def calcFixedEndReactions(self) -> tuple[PrincipleForce, PrincipleForce]:
        # TODO amend for axial force too
        length = self.beamLength
        dN1 = self.location
        dN2 = length - dN1

        perp_magnitude = self.magnitude * math.sin(self.angle)

        V1 = -(3 * dN1 + dN2) * perp_magnitude * dN2 ** 2 / length ** 3
        V2 = -(3 * dN2 + dN1) * perp_magnitude * dN1 ** 2 / length ** 3
        #TODO some buggery here with the sign of end moments in beneath lines, reactions would be opposite and so would the deflections. idk why
        # I think it shouldve worked but now R1 needs to be negative for downward load even though my reasoning suggests it should be positive (CCW) to act as
        # reaction for downward acting load. Figure this out. this buggery also exists very likely for udl and vdl
        R1 = +perp_magnitude * dN1 * dN2 ** 2 / length ** 2
        R2 = -perp_magnitude * dN2 * dN1 ** 2 / length ** 2

        par_magnitude = self.magnitude * math.cos(self.angle)

        A1 = -par_magnitude * dN2 / (dN2 + dN1)
        A2 = -par_magnitude * dN1 / (dN1 + dN2)

        iNodeFer = PrincipleForce(A1, V1, R1)
        jNodeFer = PrincipleForce(A2, V2, R2)

        return iNodeFer, jNodeFer

    def magnitudeAtPoint(self, point, axis="perpendicular"):
        # TODO fix the axis wala jugaar
        if point == self.location:
            magnitude = {"perpendicular": self.magnitude * math.sin(self.angle),
                         "parallel": self.magnitude * math.cos(self.angle)}
            magnitude["abs"] = math.sqrt(magnitude["perpendicular"] ** 2 + magnitude["parallel"] ** 2)
            return magnitude[axis]
        else:
            return 0


class VaryingDistributedLoad(StaticLoad):
    def __init__(self, start_magniude, end_magnitude, start_location, end_location, angle=270):
        super().__init__()
        self.loadClass = "Varying Distributed Load"
        self.start_magnitude = start_magniude
        self.end_magnitude = end_magnitude
        self.start = start_location
        self.end = end_location
        self.angle = degree2rad(angle)

    def calcCentroid(self):
        dist = self.end - self.start

        rect_centr = (self.end + self.start) / 2
        rect_weight = self.start_magnitude * dist

        tri_centr = (2 / 3) * dist + self.start
        tri_weight = (1 / 2) * dist * (self.end_magnitude - self.start_magnitude)

        centr = (rect_centr * rect_weight + tri_centr * tri_weight) / self.calcTotal()
        return centr

    def calcTotal(self):
        # TODO maybe do the dictionary thing here with both projections?
        total = (self.end - self.start) * (self.end_magnitude + self.start_magnitude) / 2
        return total

    def calcFixedEndReactions(self) -> tuple[PrincipleForce, PrincipleForce]:
        # TODO work on axial comp

        # s1=pre_dist
        # s2=dist
        # s3=post_dist
        # refactor later
        s2 = self.end - self.start
        s1 = self.start - 0
        s3 = self.beamLength - self.end

        if s2 == 0:
            return PrincipleForce(0, 0, 0), PrincipleForce(0, 0, 0)

        # Split into a triangular load and a rectangular load
        # Triangular Load
        tri_mag = (self.end_magnitude - self.start_magnitude)
        tri_mag_perp = tri_mag * math.sin(self.angle)

        # Foloowing Formulae for R1 and R2, referenced from an eng-tip site
        # https://www.eng-tips.com/viewthread.cfm?qid=413577
        # Thanks to KootK, whoever he is, for saving me hours of algebra, which he probably did before I was even born
        # minus switched to maintain convention

        R1 = (1 / 60) * tri_mag_perp * s2 * (
                (2 * s2 ** 3) + (5 * s2 ** 2) * s1 + (20 * s3 ** 2) * s2 + (
                30 * s3 ** 2) * s1 + (10 * s2 ** 2) * s3 + (
                        20 * s1 * s2 * s3)) / (s1 + s2 + s3) ** 2
        R2 = -(1 / 60) * tri_mag_perp * s2 * (
                (3 * s2 ** 3) + (15 * s2 ** 2) * s3 + (10 * s1 ** 2) * s2 + (
                30 * s1 ** 2) * s3 + (10 * s2 ** 2) * s1 + (
                        40 * s1 * s2 * s3)) / (s1 + s2 + s3) ** 2
        # initialize to zero because we need total shear and for that we need to find total moment on each side,
        # which we will find in the rectange step after this
        V1 = 0
        V2 = 0

        # Finding centroid of triangular portion here
        tri_centr = (2 / 3) * s2 + s1
        tri_total_par = tri_mag * math.cos(self.angle) * s2 / 2
        A1 = -tri_total_par * tri_centr / (self.beamLength)
        A2 = -tri_total_par * (self.beamLength - tri_centr) / (self.beamLength)

        iNodeFer = PrincipleForce(A1, V1, R1)
        jNodeFer = PrincipleForce(A2, V2, R2)

        # Temporary rectangular load to handle rectangular portion calculation
        temprect = UniformDistributedLoad(self.start_magnitude, self.start, self.end, angle=rad2degree(self.angle))
        temprect.beamLength = self.beamLength

        iNodeFerTemp, jNodeFerTemp = temprect.calcFixedEndReactions()

        iNodeFer += iNodeFerTemp
        jNodeFer += jNodeFerTemp

        del temprect

        V2 = -(iNodeFerTemp.mxy + jNodeFerTemp.mxy + self.calcTotal() * math.sin(
            self.angle) * self.calcCentroid()) / self.beamLength
        V1 = -self.calcTotal() * math.sin(self.angle) - V2

        iNodeFer.fy = V1
        jNodeFer.fy = V2

        return iNodeFer, jNodeFer

    def magnitudeAtPoint(self, point, axis='perpendicular'):
        if self.start <= point <= self.end:
            magnitude = {"perpendicular": self.start_magnitude * math.sin(self.angle) + (
                    (point - self.start) * (self.end_magnitude - self.start_magnitude) * math.sin(self.angle) / (
                    self.end - self.start)),
                         "parallel": self.start_magnitude * math.cos(self.angle) + (
                                 (point - self.start) * (self.end_magnitude - self.start_magnitude) * math.cos(
                             self.angle) / (self.end - self.start))}
            magnitude["abs"] = math.sqrt(magnitude["perpendicular"] ** 2 + magnitude["parallel"] ** 2)
            return magnitude[axis]

        else:
            return 0


class Moment(StaticLoad):
    def __init__(self, magnitude):
        super().__init__(magnitude)
        self.loadClass = "Moment"
        self.magnitude = magnitude

    def calcTotal(self):
        return self.magnitude

    def __add__(self, other):
        if isinstance(other, Moment):
            return Moment(self.magnitude + other.magnitude)
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

    def calcFixedEndReactions(self) -> tuple[PrincipleForce, PrincipleForce]:
        mag = self.magnitude
        dist = self.location
        length = self.beamLength
        distend = length - dist

        R1 = mag * (distend) * (2 * dist - (distend)) / length ** 2
        R2 = mag * (dist) * (2 * (distend) - dist) / length ** 2
        V1 = 6 * mag * dist * distend / length ** 3
        V2 = -6 * mag * dist * distend / length ** 3
        A1 = 0
        A2 = 0

        iNodeFer = PrincipleForce(A1, V1, R1)
        jNodeFer = PrincipleForce(A2, V2, R2)

        return iNodeFer, jNodeFer

    def toNode(self):
        pass


class TrapezoidalDistributedLoad(VaryingDistributedLoad):

    def __init__(self, location_list: list[float], magnitude_list: list[float], angle=270):
        self.loadClass = "Trapezoidal Distributed Load"
        self.angle = degree2rad(angle)
        self.VDLset: list[VaryingDistributedLoad] = []
        self.location_list=location_list
        self.magnitude_lst=magnitude_list
        self.inputIntegrityCheck(location_list, magnitude_list)
        self.initializeVDLset(location_list, magnitude_list)

    def initializeVDLset(self, location_list, magnitude_list):
        for index in range(len(location_list) - 1):
            self.VDLset.append(
                VaryingDistributedLoad(magnitude_list[index], magnitude_list[index + 1],
                                       location_list[index], location_list[index + 1], angle=rad2degree(self.angle)))

    def inputIntegrityCheck(self, location_list, magnitude_list):
        if len(location_list) != len(magnitude_list):
            print("Location and Magnitude points are not equal. A Magnitude must be provided for each Location listed")
            raise ValueError
        # TODO create checks for sequence ordering of locations
        # TODO create a cleaner for entry data. i.e when there are two different load mags at the same point
        # pass

    def calcFixedEndReactions(self) -> tuple[PrincipleForce, PrincipleForce]:
        iNodeFer = PrincipleForce(0, 0, 0)
        jNodeFer = PrincipleForce(0, 0, 0)

        for vdl in self.VDLset:
            iNodeFerTemp, jNodeFerTemp = vdl.calcFixedEndReactions()
            iNodeFer += iNodeFerTemp
            jNodeFer += jNodeFerTemp

        return iNodeFer, jNodeFer

    def magnitudeAtPoint(self, point, axis='perpendicular'):
        for vdl in self.VDLset:
            magnitude = vdl.magnitudeAtPoint(point, axis)
            if magnitude != 0:
                return magnitude
        else:
            return 0
