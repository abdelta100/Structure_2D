from abc import ABC


class CrossSection(ABC):
    def __init__(self):
        self.name = "None"
        self.MomentofInertia = None

    def calcMomentofInertia(self):
        pass


class RectangularCrossSection(CrossSection):
    def __init__(self, width, height):
        super().__init__()
        self.name = "Rectangle"
        self.width = width
        self.height = height
        self.MomentofInertia = self.calcMomentofInertia()

    def calcMomentofInertia(self):
        I = (self.width * self.height ** 3) / 12
        return I


class DefaultRectangularCrossSection(RectangularCrossSection):
    def __init__(self, width=1, height=3):
        super().__init__(width, height)
