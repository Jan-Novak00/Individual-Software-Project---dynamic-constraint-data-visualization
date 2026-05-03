from abc import ABC, abstractmethod
from kiwiplots import *


class GameEvaluator(ABC):
    """
    Evaluates user input.
    """
    def __init__(self, isGuess):
        self.isGuess = isGuess

    @abstractmethod
    def Eval(self,userData, solutionData) -> int:
        raise NotImplementedError("Metod GameEvaluator.Eval must be declared in a subclass.")
    