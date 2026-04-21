from kiwisolver import Constraint, Variable
from abc import ABC, abstractmethod

class ValuePoint2D:
    """
    Holds information about 2D points.
    """
    def __init__(self, X: float, Y: float, name: str = "", secondaryName: str = ""):
        self.X = X
        self.Y = Y
        self.name = name
        self.secondaryName = secondaryName
    def __str__(self):
        return f"({self.X}, {self.Y})"

class VariablePoint2D:
  """
  Used for constraint declaration. Represents 2D point as a pair of Variable instances-
  """
  def __init__(self, name: str = "", secondaryName = ""):
        self.X = Variable(f"{name}.X")
        self.Y = Variable(f"{name}.Y")
        self.name = name
        self.secondaryName = secondaryName
  def Value(self):
        return ValuePoint2D(self.X.value(), self.Y.value(), self.name, self.secondaryName)

class VariableElement(ABC):

    @abstractmethod
    def GetAllConstraints(self)->list[Constraint]:
         raise NotImplementedError("Method on_left_down must be declared in subclass")
    @abstractmethod
    def Value(self):
         raise NotImplementedError("Method on_left_down must be declared in subclass")