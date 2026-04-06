from kiwiplots import *

class GameDataViewer(DataViewer):
    @abstractmethod
    def WriteSolution(self, userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata : PlotMetadata):
        raise NotImplementedError("Method GameDataViewer.writeSolution must be declared in subclass.")