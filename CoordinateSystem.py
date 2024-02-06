import numpy as np

from AuxillaryFunctions import degree2rad


class CoordinateSystem2D:
    def __init__(self, angle):
        self.translation = np.zeros(shape=(2, 2))
        self.angle = degree2rad(angle)
        self.rotation = self.getRotationMatrix()
        pass

    def getRotationMatrix(self):
        matrix = np.array((
            [
                [np.cos(self.angle), np.sin(self.angle)],
                [-np.sin(self.angle), np.cos(self.angle)]]))
        return matrix

    def toCoordinates(self, point: tuple[float, float]):
        # add something that factors points in other coordinate_systems without manual adjustments
        base_point = np.array(point)
        transformed_point = np.matmul(self.rotation, base_point) + self.translation
        return transformed_point

    def toUCS(self, point):
        # TODO inversing transformation for now
        transformed_point = np.array(point)
        ucs_point = np.matmul(self.rotation.T, transformed_point - self.translation)
        return ucs_point


class UCS(CoordinateSystem2D):
    def __init__(self, angle):
        super().__init__(angle=0)
