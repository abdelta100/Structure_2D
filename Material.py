from abc import ABC


class Material(ABC):
    def __init__(self):
        self.name: str = "None"
        self.density: float = None
        self.elasticModulus: float = None
        self.poissonRatio: float = None

    def __repr__(self):
        selfrep = ("Name: " + str(self.name) + '\n' +
                   "Density: " + str(self.density) + '\n' +
                   "Elastic Modulus: " + str(self.elasticModulus) + '\n')
        return (selfrep)


class NewMaterial(Material):
    def __init__(self, name, density, elastic_mod, poisson_ratio):
        super().__init__()
        self.name = name
        self.density = density
        self.elasticModulus = elastic_mod
        self.poissonRatio = poisson_ratio


class DefaultMaterial(Material):
    def __init__(self):
        super().__init__()
        self.name = "Default"
        self.elasticModulus = 2700000
        self.poissonRatio = 0.33
