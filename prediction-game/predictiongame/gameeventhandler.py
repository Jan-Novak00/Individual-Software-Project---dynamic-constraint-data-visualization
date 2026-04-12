from abc import ABC, abstractmethod
from kiwiplots import ChartSolver, PlotMetadata

class GameEventHandler(ABC):
    def __init__(self):
        self.paused = False
    
    def Pause(self):
        self.paused = True
    
    def Unpause(self):
        self.paused = False

    def IsPaused(self):
        return self.paused

    @abstractmethod
    def DisplayOther(self, otherSolver: ChartSolver):
        raise NotImplementedError("Method GameEventHandler.DisplayOther msut be definded in a subclass")
    
    @abstractmethod
    def WriteSolution(self, userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata):
        raise NotImplementedError("Method GameEventHandler.WriteSolution msut be definded in a subclass")