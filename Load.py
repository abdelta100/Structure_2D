from abc import ABC


class Load(ABC):
    def __init__(self, local=False):
        self.loadClass="None"
        self.name="None"
        #TODO implement local and global load application
class UniformDistributedLoad(Load):
    def __init__(self):
        super().__init__()

class PointLoad(Load):
    def __init__(self, magnitude, local=False):
        super().__init__()
        self.loadClass="Point Load"
        self.magnitude = magnitude
