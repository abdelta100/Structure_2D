from StructureGlobal import StructureGlobal

class StructureGlobalNOrder(StructureGlobal):
    def __init__(self):
        super().__init__()
        self.analysisOrder: int = 5

    def runNOrderAnalysis(self):
        for i in range(self.analysisOrder):
            self.runAnalysis()
            #TODO FIGURE OUT HOW TO RUN N ORDER ANALYSIS
            #TODO Also figure out if I should subclass structureglobal or provide the structure as a field
        pass