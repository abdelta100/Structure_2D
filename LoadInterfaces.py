from abc import ABC
from PrincipleForce import PrincipleForce2D


class MomentLoad(ABC):
    def __int__(self):
        pass


class ForceLoad(ABC):
    def __init__(self):
        pass


class MemberLoad(ABC):
    def __init__(self):
        self.beamLength: float = 1
        pass

    def calcFixedEndReactions(self) -> tuple[PrincipleForce2D, PrincipleForce2D]:
        pass

    def calcCentroid(self) -> float:
        pass

    def setBeamLength(self, length):
        # TODO add property handlers idk
        self.beamLength = length

    def calcTotal(self) -> float:
        pass

    def magnitudeAtPoint(self, point):
        pass

    def cleanInputs(self):
        # TODO deal with either repeating code or adding unknown variables
        # TODO think of moving this outside
        pass


class NodeLoad(ABC):
    def __init__(self):
        pass

    def calcTotal(self) -> float:
        pass


class DynamicLoad(ABC):
    def __init__(self):
        pass
