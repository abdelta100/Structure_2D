class LoadPattern:
    def __init__(self, patternType: str):
        self.patternType = patternType.lower()

    def __post_init__(self):
        pass

    def isPattern(self, patternType: str):
        return patternType.lower() == self.patternType.lower()
