from abc import ABC, abstractmethod
from kiwisolver import Variable, Constraint
from kiwiplots.plotelement import VariablePoint2D, ValuePoint2D

MINIMAL_WIDTH : float = 10

class VariableChart(ABC):
    """
    Encapsulates all variables of all plot elemenets
    """
    def __init__(self):
        self.width = Variable("global_width")

        self.spacing = Variable("global_spacing")

        self.origin: VariablePoint2D = VariablePoint2D("origin")
        self.yAxisHeight: Variable = Variable("axisTop")
    
    @abstractmethod
    def GetAllConstraints(self)->list[Constraint]:
        raise NotImplementedError("Method on_left_down must be declared in subclass")
    
    @abstractmethod
    def Value(self):
        raise NotImplementedError("Method on_left_down must be declared in subclass")
    
    def GetOrigin(self)-> ValuePoint2D:
        return self.origin.Value()