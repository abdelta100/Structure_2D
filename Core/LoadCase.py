from Core.Load import StaticLoad
from Core.LoadPattern import LoadPattern


class LoadCase:
    def __init__(self, load: StaticLoad, pattern: str):
        # TODO change load to type Load instead of StaticLoad sometimes later
        self.load = load
        self.pattern = self.createPattern(pattern)

    def createPattern(self, pattern):
        return LoadPattern(pattern)

    def setTarget(self, target):
        # TODO fix the following
        # Also maybe add option to avoid duplicate load addition, and addition of same load object to different member?
        # Create a base load, then duplicate loads to add to each individual member?
        # setTarget is maybe alias for setBeam or setNode
        self.load.setTarget(target)

    def isPattern(self, patternType: str):
        return self.pattern.isPattern(patternType)

