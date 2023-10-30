from abc import ABC


class Load(ABC):
    def __init__(self, local=False):
        self.loadClass = "None"
        self.name = "None"
        # TODO implement local and global load application

    def calcCentroid(self):
        pass

    def calcTotal(self):
        pass


class UniformDistributedLoad(Load):
    def __init__(self, magnitude, start_location, end_location):
        super().__init__()
        self.loadClass = "Uniformly Distributed Load"
        self.magnitude = magnitude
        self.start = start_location
        self.end = end_location

    def calcTotal(self):
        return self.magnitude * (self.end - self.start)

    def calcCentroid(self):
        return self.end - self.start


class PointLoad(Load):
    def __init__(self, magnitude, local=False):
        super().__init__()
        self.loadClass = "Point Load"
        self.magnitude = magnitude

    def calcTotal(self):
        return self.magnitude


class PointLoadMember(PointLoad):
    def __init__(self, magnitude, location):
        super().__init__(magnitude)
        self.location = location

    def calcCentroid(self):
        self.location


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

    def calcTotal(self):
        total = (self.end - self.start) * (self.end_magnitude + self.start_magnitude) / 2
        return total


class Moment(Load):
    def __init__(self, magnitude):
        super.__init__()
        self.loadClass = "Moment"
        self.magnitude = magnitude

    def calcTotal(self):
        return self.magnitude


class MomentMember(Moment):
    def __init__(self, magnitude, location):
        super().__init__(magnitude)
        self.location = location

    def calcCentroid(self):
        return self.location

    def toNode(self):
        pass
