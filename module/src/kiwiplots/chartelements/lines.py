from kiwisolver import Constraint, Variable
from .basicelements import *
from typing import Literal
from kiwiplots.utils import inheritdocstring

class ValueLine:
    """Class which represents a value of a line element on the chart.
    """
    def __init__(self, leftEnd : ValuePoint2D, rightEnd : ValuePoint2D, leftHeight : float, rightHeight : float, ignoreRight : bool = False):
        self.leftEnd : ValuePoint2D = leftEnd
        self.rightEnd : ValuePoint2D = rightEnd
        self.leftHeight : float = leftHeight
        self.rightHeight : float = rightHeight
        self.ignoreRight : bool = ignoreRight

    def __str__(self):
        if not self.ignoreRight:
            return f"<{self.leftEnd.name}>-<{self.rightEnd.name}>: ({self.leftEnd.X}, {self.leftEnd.Y})-({self.rightEnd.X}, {self.rightEnd.Y})"
        else:
            return str(self.leftEnd)

class VariableLine(VariableElement):
    """Class which represents a line element on the chart.
       Creates constraints which describe the line's geometry and hold necessary kiwisolver Variable instances.

       Attributes:
            width (Variable) : Globaly declared width variable.
            ignoreRight (bool) : True if the right point should be ignored.
    """
    def __init__(self, width : Variable, xAxisHeight : Variable, leftName : str = "", rightName : str = "", ignoreRight : bool = False):
        self.width : Variable = width
        self.xAxisHeight : Variable = xAxisHeight
        self.leftHeight : Variable = Variable(f"{leftName}_height")
        self.rightHeight : Variable = Variable(f"{rightName}_height")
        self.leftEnd : VariablePoint2D = VariablePoint2D(leftName)
        self.rightEnd : VariablePoint2D = VariablePoint2D(rightName)
        self.ignoreRight : bool = ignoreRight

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
        return ValueLine(self.leftEnd.Value(), self.rightEnd.Value(), self.leftHeight.value(), self.rightHeight.value(), self.ignoreRight)

    def ChangeName(self, name: str, whichPoint: Literal["left","right"]):
        """Change name of the givne point

        Args:
            name (str): New name of the point
            whichPoint (Literal[&quot;left&quot;,&quot;right&quot;]): left or right point
        """
        point = self.leftEnd if whichPoint == "left" else self.rightEnd
        point.name = name
    
    def SwitchIgnoreRight(self):
        """Negates ignoreRight flag

        Returns:
            bool: new value of ignoreRight flag

        """
        self.ignoreRight = not self.ignoreRight
        return self.ignoreRight