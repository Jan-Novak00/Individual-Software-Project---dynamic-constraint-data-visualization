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
        """Triggeres evaluation of the game

        Args:
            userData : user data
            solutionData : solution data

        Returns:
            int: score
        """
        raise NotImplementedError("Metod must be declared in a subclass.")
    