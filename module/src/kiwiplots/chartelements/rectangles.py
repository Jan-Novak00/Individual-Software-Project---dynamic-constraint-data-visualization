from .basicelements import *
from kiwisolver import Variable, Constraint
from typing import Union

class ValueRectangle:
    """
    Holds information about a given rectangle
    """
    def __init__(self, leftBottomCorner: ValuePoint2D, rightTopCorner: ValuePoint2D, color: Union[str, int] = "blue", name: str = ""):
        self.leftBottom = leftBottomCorner
        self.rightTop = rightTopCorner
        self.color = color
        self.name = name
    
    def __str__(self):
        return f"{self.name} LB: ({self.leftBottom.X}, {self.leftBottom.Y}), RT: ({self.rightTop.X}, {self.rightTop.Y})"
    def GetHeight(self)->float:
        return self.rightTop.Y-self.leftBottom.Y

class VariableRectangle(VariableElement):
    """
    Creates constraints for a given rectangle.
    Width is maintained globaly, height localy
    Arguments:
        width - globaly declared Variable of width
        height - pixel height of the rectangle
        name - name of the rectangle
        color - color of the ractangle
        widthScale - scale of the width. Resulting pixel width of the rectangle is widthScale*width.value()
    """
    def __init__(self, width: Variable, name: str, color : Union[str,int] = "blue", widthScale : float = 1):
        self.height = Variable(f"{name}_height")
        self.width = width
        self.widthScale = widthScale
        self.name = name
        self.color = color
        self.leftBottom = VariablePoint2D(name+".leftBottom")
        self.rightTop = VariablePoint2D(name+".rightTop")

        #self.heightConstraint : Constraint = (self.height == float(height)) | "strong"
        self.horizontalPositionConstraint : Constraint = ((self.leftBottom.X + self.width * self.widthScale == self.rightTop.X) | "required")
        self.verticalPositionConstraint : Constraint = ((self.leftBottom.Y + self.height == self.rightTop.Y) | "required")

        self.bottomLeftXPositionConstraint : Constraint | None = None
        self.bottomLeftYPositionConstraint : Constraint | None = None

        self.spacingConstraint : Constraint | None = None 


    def ChangeName(self, name: str):
        self.name = name
    
    def ChangeColor(self, color: Union[str,int]):
        self.color = color
   
    def _getShapeConstraints(self) -> list[Constraint]:
        """
        Returns iterator over basic constraints.
        """
        constraints = []
        if self.spacingConstraint is not None:
            constraints.append(self.spacingConstraint)
        if self.bottomLeftXPositionConstraint is not None:
            constraints.append(self.bottomLeftXPositionConstraint)
        if self.bottomLeftYPositionConstraint is not None:
            constraints.append(self.bottomLeftYPositionConstraint)
        constraints.append(self.horizontalPositionConstraint)
        constraints.append(self.verticalPositionConstraint)
        return constraints

    def _getPositionConstraints(self) -> list[Constraint]:
        return [(self.height >= 0)|"required",(self.leftBottom.X >= 0) | "required", (self.leftBottom.Y >= 0) | "required", (self.rightTop.X >= 0) | "required", (self.rightTop.Y >= 0) | "required"]


    def SetSpacingConstraint(self, spacingConstraint : Constraint):
        self.spacingConstraint = spacingConstraint
    

    def GetAllConstraints(self)->list[Constraint]:
        """
        Returns all constraints, both from __iter__ method and constraints which specify domain of variables
        """
        return self._getShapeConstraints() + self._getPositionConstraints()
    
    def Value(self)->ValueRectangle:
        """
        Returns ValueRectangle representation of the instance.
        """
        return ValueRectangle(self.leftBottom.Value(), self.rightTop.Value(), self.color, self.name)
    
    def GetName(self)->str:
        return self.name
    
    def GetHeightVariable(self) -> Variable:
        return self.height