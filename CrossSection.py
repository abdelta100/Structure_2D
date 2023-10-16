from abc import ABC


class CrossSection(ABC):
    def __init__(self):
        self.name = "None"
        self.momentOfInertia = self.calcMomentofInertia()
        self.area = self.calcSectionArea()

    def calcMomentofInertia(self):
        return 0

    def calcSectionArea(self):
        return 0


class RectangularCrossSection(CrossSection):
    def __init__(self, width, height):
        super().__init__()
        self.name = "Rectangle"
        self.width = width
        self.height = height
        self.momentOfInertia = self.calcMomentofInertia()
        self.area=self.calcSectionArea()

    def calcMomentofInertia(self):
        I = (self.width * self.height ** 3) / 12
        return I

    def calcSectionArea(self):
        return self.width * self.height


class DefaultRectangularCrossSection(RectangularCrossSection):
    def __init__(self, width=1, height=3):
        super().__init__(width, height)
