from abc import ABC, abstractmethod
from kiwiplots import *


class GameEvaluator(ABC):
    """
    Evaluates user input.
    """
    @abstractmethod
    @staticmethod
    def Eval(userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata : PlotMetadata) -> int:
        raise NotImplementedError("Metod GameEvaluator.Eval must be declared in a subclass.")
    