from abc import ABC, abstractmethod
from kiwisolver import Variable, Constraint
from kiwiplots.chartelements import VariablePoint2D, ValuePoint2D

MINIMAL_WIDTH : float = 10

class VariableChart(ABC):
    """Abstract base class that encapsulates all kiwisolver variables for a chart.

    Defines the shared layout variables (width, spacing, origin, axis height) that
    every concrete chart type uses.

    Attributes:
        width (Variable): Global width variable shared across chart elements.
        spacing (Variable): Global spacing variable between chart elements.
        origin (VariablePoint2D): Position of the chart origin.
        yAxisHeight (Variable): Height of the vertical axis.
    """
    def __init__(self):
        """Initializes the shared layout variables for the chart."""
        self.width = Variable("global_width")

        self.spacing = Variable("global_spacing")

        self.origin: VariablePoint2D = VariablePoint2D("origin")
        self.yAxisHeight: Variable = Variable("axisTop")
    
    @abstractmethod
    def GetAllConstraints(self)->list[Constraint]:
        """Returns all kiwisolver constraints that define the chart layout.

        Returns:
            list[Constraint]: All constraints for the chart's variables.
        """
        raise NotImplementedError("Method must be declared in a subclass.")
    
    @abstractmethod
    def Value(self):
        """Returns the resolved chart element data after solving the constraints."""
        raise NotImplementedError("Method must be declared in a subclass.")
    
    def GetOrigin(self)-> ValuePoint2D:
        """Returns the current solved position of the chart origin.

        Returns:
            ValuePoint2D: x,y coordinates of the origin.
        """
        return self.origin.Value()