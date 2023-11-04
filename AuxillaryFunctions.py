import math


def getComponentsRefBeam(theta, vector):
    Vx = vector * math.sin(theta)
    Vy = vector * math.cos(theta)
    return Vx, Vy
