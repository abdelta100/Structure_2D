import math


def getComponentsRefBeam(theta, vector):
    Vx = vector * math.sin(theta)
    Vy = vector * math.cos(theta)
    return Vx, Vy

def rad2degree(radians):
    return 180*radians/math.pi

def degree2rad(degrees):
    return math.pi*degrees/180
