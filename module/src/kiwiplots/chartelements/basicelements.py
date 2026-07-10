from kiwisolver import Constraint, Variable
from abc import ABC, abstractmethod

class ValuePoint2D:
    """
    Holds information about 2D points.

    Attributes:
        X (float) : x coordinate
        Y (float) : y coordinate
        name (string) : name of the point, empty by default
        secondaryName (string) : secondary name; used when point needs to carry more information about itself
    """
    def __init__(self, X: float, Y: float, name: str = "", secondaryName: str = ""):
        self.X = X
        self.Y = Y
        self.name = name
        self.secondaryName = secondaryName
    def __str__(self):
        return f"{self.name} = ({self.X}, {self.Y})"

class VariablePoint2D:
  """
  Used for constraint declaration. Represents 2D point as a pair of kiwisolver.Variable instances.

  Attributes:
    X (Variable) : x coordinate of the point
    Y (Variable) : y coordinate of the point
    name (string) : name of the point, empty by default
    secondaryName (string) : secondary name; used when point needs to carry more information about itself
  """
  def __init__(self, name: str = "", secondaryName = ""):
        self.X = Variable(f"{name}.X")
        self.Y = Variable(f"{name}.Y")
        self.name = name
        self.secondaryName = secondaryName

  def Value(self):
    """
    Getter for value of the point, represented using ValuePoint2D instance.

    Returns:
          ValuePoint2D: snapshot of the point
    """
    return ValuePoint2D(self.X.value(), self.Y.value(), self.name, self.secondaryName)

class VariableElement(ABC):
    """
        Class representing data element on the chart. Hold necessery constraints and variables whcih define the geometry of the element.
    """
    @abstractmethod
    def GetAllConstraints(self)->list[Constraint]:
        """
        Returns all constraints of the element

        Returns:
            list[Constraint]: list of all constraints
        """ 
        raise NotImplementedError("Method on_left_down must be declared in subclass")
    
    @abstractmethod
    def Value(self):
        """
        Returns value representation of the element.

        Returns:
            Any: type of the return value depends on the element.
        """ 
        raise NotImplementedError("Method on_left_down must be declared in subclass")
