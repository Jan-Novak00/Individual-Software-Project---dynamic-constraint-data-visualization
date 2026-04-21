from kiwisolver import Constraint, Variable
from .basicelements import *

class ValueLine:
    def __init__(self, leftEnd : ValuePoint2D, rightEnd : ValuePoint2D, leftHeight : float, rightHeight : float):
        self.leftEnd : ValuePoint2D = leftEnd
        self.rightEnd : ValuePoint2D = rightEnd
        self.leftHeight : float = leftHeight
        self.righHeight : float = rightHeight
    def __str__(self):
        return f"<{self.leftEnd.name}>-<{self.rightEnd.name}>: ({self.leftEnd.X}, {self.leftEnd.Y})-({self.rightEnd.X}, {self.rightEnd.Y})"

class VariableLine(VariableElement):
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
    
    def GetAllConstraints(self):
        return self.verticalConstraints + [self.horizontalPositionConstraint]
    
    def Value(self):
        return ValueLine(self.leftEnd.Value(), self.rightEnd.Value(), self.leftHeight.value(), self.rightHeight.value())