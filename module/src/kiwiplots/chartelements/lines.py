from kiwisolver import Constraint, Variable
from .basicelements import *
from typing import Literal
from kiwiplots.utils import inheritdocstring

class ValueLine:
    """Class which represents a value of a line element on the chart.
    """
    def __init__(self, leftEnd : ValuePoint2D, rightEnd : ValuePoint2D, leftHeight : float, rightHeight : float):
        self.leftEnd : ValuePoint2D = leftEnd
        self.rightEnd : ValuePoint2D = rightEnd
        self.leftHeight : float = leftHeight
        self.rightHeight : float = rightHeight

    def __str__(self):
        return f"<{self.leftEnd.name}>-<{self.rightEnd.name}>: ({self.leftEnd.X}, {self.leftEnd.Y})-({self.rightEnd.X}, {self.rightEnd.Y})"

class VariableLine(VariableElement):
    """Class which represents a line element on the chart.
       Creates constraints which describe the line's geometry and hold necessary kiwisolver Variable instances.

       Attributes:
            width (Variable): Globaly declared width variable.
    """
    def __init__(self, width : Variable, xAxisHeight : Variable, leftName : str = "", rightName : str = ""):
        self.width : Variable = width
        self.xAxisHeight : Variable = xAxisHeight
        self.leftHeight : Variable = Variable(f"{leftName}_height")
        self.rightHeight : Variable = Variable(f"{rightName}_height")
        self.leftEnd : VariablePoint2D = VariablePoint2D(leftName)
        self.rightEnd : VariablePoint2D = VariablePoint2D(rightName)

        self.horizontalPositionConstraint : Constraint = ((self.leftEnd.X + self.width == self.rightEnd.X) | "required")
        self.verticalConstraints : list[Constraint] = [
            ((self.xAxisHeight + self.leftHeight == self.leftEnd.Y) | "required"),
            ((self.xAxisHeight + self.rightHeight == self.rightEnd.Y) | "required")
        ]
    
    @inheritdocstring(VariableElement.GetAllConstraints)
    def GetAllConstraints(self):
        return self.verticalConstraints + [self.horizontalPositionConstraint]
    
    def Value(self)->ValueLine:
        """Get value representation of the line.

        Returns:
            ValueLine: Snapsahot of the line
        """
        return ValueLine(self.leftEnd.Value(), self.rightEnd.Value(), self.leftHeight.value(), self.rightHeight.value())

    def ChangeName(self, name: str, whichPoint: Literal["left","right"]):
        """Change name of the givne point

        Args:
            name (str): New name of the point
            whichPoint (Literal[&quot;left&quot;,&quot;right&quot;]): left or right point
        """
        point = self.leftEnd if whichPoint == "left" else self.rightEnd
        point.name = name