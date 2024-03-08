from abc import ABC

# from Core.Element import GeneralFrameElement2D
from PrincipleForce import PrincipleForce2D


class MomentLoad(ABC):
    def __int__(self):
        pass


class ForceLoad(ABC):
    def __init__(self):
        pass


class MemberLoad(ABC):
    def __init__(self, angle: float, local: bool= True, projected: bool = False):
        self.beamLength: float = 1
        self.beamAngle = 0
        self.angle = angle
        self.isLocal = local
        self.isProjected = projected
        # TODO deal with local and Projected Load
        # self.localVsGlobal(local)
        pass

    def calcFixedEndReactions(self) -> tuple[PrincipleForce2D, PrincipleForce2D]:
        pass

    def calcCentroid(self) -> float:
        pass

    def setBeamLength(self, length):
        # TODO add property handlers idk
        self.beamLength = length

    def setBeam(self, beam):
        # beam is of type GeneralFrameElement2D, workaround due to circular import
        self.beamLength = beam.length
        self.beamAngle = beam.getAngle()
        self.cleanInputs()
        if not self.isLocal:
            self.angle = self.beamAngle - self.angle
        if self.isProjected:
            self.projectionHandler()

    def setTarget(self, target):
        self.setBeam(target)


    def calcTotal(self) -> float:
        pass

    def magnitudeAtPoint(self, point: float, axis: str = "perpendicular"):
        pass

    def cleanInputs(self):
        # TODO deal with either repeating code or adding unknown variables
        # TODO think of moving this outside
        pass

    def localVsGlobal(self, isLocal: bool):
        if not isLocal:
            self.angle = 9
        pass

    def projectionHandler(self):
        pass


class NodeLoad(ABC):
    def __init__(self):
        pass

    def calcTotal(self) -> float:
        pass


class DynamicLoad(ABC):
    def __init__(self):
        pass

class ConcentratedLoad(MemberLoad):
    def __init__(self, magnitude, angle, local, projected):
        super().__init__(angle, local, projected)
        self.magnitude = magnitude

class DistributedLoad(MemberLoad):
    def __init__(self):
        super().__init__()