from abc import ABC


class Material(ABC):
    def __init__(self):
        """
        A non instantiable abstract class that acts as base for all material types.
        """
        self.name: str = "None"
        self.density: float = 1.0
        self.compressiveStrength: float = 1
        self.tensileStrength: float = self.compressiveStrength
        self.elasticModulus: float = 1
        self.poissonRatio: float = 1

    def __repr__(self):
        selfrep = (
                "Name: " + str(self.name) + '\n' +
                "Density: " + str(self.density) + '\n' +
                "Comp Strength: " + str(self.compressiveStrength) + '\n' +
                "Elastic Modulus: " + str(self.elasticModulus) + '\n')
        return selfrep


class NewMaterial(Material):
    def __init__(
            self,
            name: str,
            density: float,
            elastic_mod: float,
            poisson_ratio: float,
            comp_strength: float,
            tensile_strength: float = None):
        """
        A new material class that allows users to specify a new material for use in analysis or design. Not all
        functionality fleshed out yet.
        :rtype: NewMaterial
        :param name: Name given to new Material
        :param density: Density of Material
        :param elastic_mod: Elastic Modulus of Material.
        :param poisson_ratio: Poisson Ratio of Material.
        :param comp_strength: Material Strength in Compression. Yield strength will do for now.
        :param tensile_strength: Material Strength in Tension. Yield strength will do for now.
        """
        super().__init__()
        self.name: str = name
        self.density: float = density
        self.compressiveStrength: float = comp_strength
        self.tensileStrength: float = comp_strength
        if tensile_strength is not None:
            self.tensileStrength = tensile_strength
        self.elasticModulus: float = elastic_mod
        self.poissonRatio: float = poisson_ratio


class DefaultMaterial(Material):
    def __init__(self):
        """
Initializes a DefaultMaterial object. Takes no inputs. Default Material Values are assigned.\n
\n
Compressive Strength: 3000 units\n
Elastic Modulus: 2700000 units\n
Poisson Ration: 0.33
        :rtype: Material
        """
        super().__init__()
        self.name: str = "Default"
        self.compressiveStrength: float = 3000
        self.elasticModulus: float = 2700000
        self.poissonRatio: float = 0.33


class TestMaterial(DefaultMaterial):
    def __init__(self, E: float):
        """
        A quick material class for use while testing or checking. Doesn't require fancy params, only the basic elastic
        modulus, other values are inherited from DefaultMaterial class.
        :param E: Elastic Modulus of material
        """
        super().__init__()
        self.elasticModulus = E
