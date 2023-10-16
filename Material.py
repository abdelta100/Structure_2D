from abc import ABC


class Material(ABC):
    def __init__(self, elastic_mod, poisson_ratio):
        self.name: str = "None"
        self.elasticModulus: float = None
        self.poissonRatio: float = None


class DefaultMaterial(Material):
    def __init__(self, elastic_mod=None, poisson_ratio=None):
        super().__init__(elastic_mod, poisson_ratio)
        self.name = "Default"
        self.elasticModulus = 2700000
        self.poissonRatio = 0.33
