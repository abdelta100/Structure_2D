import math

import numpy as np

zerolim = 10e-13


def getPerpendicularComponentsRefBeam(theta, vector):
    Vx = vector * math.sin(theta)
    Vy = vector * math.cos(theta)
    return Vx, Vy


def getAxialComponentsRefBeam(theta, vector):
    Vx = vector * math.cos(theta)
    Vy = vector * math.sin(theta)
    return Vx, Vy


def rad2degree(radians):
    rad = 180 * radians / math.pi
    if -zerolim < rad < zerolim:
        rad = 0
    return rad


def degree2rad(degrees):
    # TODO take a look at this error correction here
    degree = math.pi * degrees / 180
    if -zerolim < degree < zerolim:
        degree = 0
    return degree


def matrixStabilityCheck(matrix):
    cond = np.linalg.cond(matrix)

    if cond > 1e-14:

        singular_values = np.linalg.svd(matrix)[1]
        max_sv = np.max(singular_values)
        min_sv = np.min(singular_values)

        print("Matrix Condition Number: "+ str(min_sv / max_sv)+"\n")

        matrix_nudged = matrix + np.eye(matrix.shape[0]) * 1e-9
        newcond = np.linalg.cond(matrix_nudged)

        return matrix_nudged

    else:
        return matrix


def distance(u, v):
    # TODO add iterable typing here maybe
    if len(u) != len(v):
        print("Position arrays passed for distance are of unequal length")
    dist = np.linalg.norm(np.array(u) - np.array(v))
    return dist
