from abc import ABC


class CrossSection(ABC):
    def __init__(self):
        """
        A non-instantiable abstract class that acts as base for all cross-section classes.
        """
        self.name: str = "None"
        self.momentOfInertia: float = 1
        self.area: float = 1

    def calcMomentofInertia(self) -> float:
        return 0

    def calcSectionArea(self) -> float:
        return 0


class RectangularCrossSection(CrossSection):
    def __init__(self, width: float, height: float):
        """
        A rectangular cross-section class, with methods for calculating area and moment of inertia.
        :rtype: RectangularCrossSection
        :param width: Width of Rectangular Cross-Section
        :param height: Height of Rectangular Cross-Section
        """
        super().__init__()
        self.name: str = "Rectangle"
        self.width: float = width
        self.height: float = height
        self.momentOfInertia: float = self.calcMomentofInertia()
        self.area: float = self.calcSectionArea()

    def calcMomentofInertia(self):
        momentOfInertia = (self.width * self.height ** 3) / 12
        return momentOfInertia

    def calcSectionArea(self):
        return self.width * self.height


class DefaultRectangularCrossSection(RectangularCrossSection):
    def __init__(self, width: float = 1, height: float = 3):
        """
        A class that returns a default rectangular cross-section for member/element instantiation with params provided
        by default. Params can be over-ridden but recommend you use RectangularCrossSection class for that.
        :rtype: DefaultRectangularCrossSection
        :param width: Width of rectangle cross-section. Provided as 1.0 by default.
        :param height: Height of rectangle cross-section. Provided as 3.0 by default.
        """
        super().__init__(width, height)


class TestRectangularCrossSection(CrossSection):
    def __init__(self, A: float, I: float):
        """
        A quick cross-section class for use while checking results or testing. Doesn't require dimensions,
        only parameters relevant for analysis.
        :rtype: TestRectangularCrossSection
        :param A: Area of cross-section
        :param I: Moment of Inertia of cross-section.
        """
        super().__init__()
        self.name: str = "Test Cross-Section"
        self.area = A
        self.momentOfInertia = I

    def calcSectionArea(self):
        """
        Method overrides super method to return its own area property instead of resorting to calculation.
        Will not actually be called.
        :return: float
        """
        return self.area

    def calcMomentofInertia(self):
        """
        Method overrides super method to return its own moment of inertia property instead of resorting to calculation.
        :return: float
        """
        return self.momentOfInertia
