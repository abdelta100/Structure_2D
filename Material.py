from abc import ABC


class Material(ABC):
    def __init__(self):
        self.name: str = "None"
        self.density: float = None
        self.compressiveStrength:float = None
        self.tensileStrength:float = self.compressiveStrength
        self.elasticModulus: float = None
        self.poissonRatio: float = None

    def __repr__(self):
        selfrep = ("Name: " + str(self.name) + '\n' +
                   "Density: " + str(self.density) + '\n' +
                   "Comp Strength: " + str(self.compressiveStrength) + '\n' +
                   "Elastic Modulus: " + str(self.elasticModulus) + '\n')
        return (selfrep)


class NewMaterial(Material):
    def __init__(self, name, density, elastic_mod, poisson_ratio, comp_strength, tensile_strength=None):
        super().__init__()
        self.name = name
        self.density = density
        self.compressiveStrength = comp_strength
        self.tensileStrength = comp_strength
        if tensile_strength is not None:
            self.tensileStrength=tensile_strength
        self.elasticModulus = elastic_mod
        self.poissonRatio = poisson_ratio


class DefaultMaterial(Material):
    def __init__(self):
        super().__init__()
        self.name = "Default"
        self.compressiveStrength=3000
        self.elasticModulus = 2700000
        self.poissonRatio = 0.33
