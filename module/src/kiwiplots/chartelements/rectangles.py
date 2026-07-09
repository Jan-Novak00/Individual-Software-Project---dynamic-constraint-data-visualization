from .basicelements import *
from kiwisolver import Variable, Constraint
from typing import Union
from kiwiplots.utils import inheritdocstring

class ValueRectangle:
    """
    Holds information about a given rectangle element. Represents a snapshot of VaraibleRectangle class.

    Attributes:
        leftBottom (ValuePoint2D): bottom left corner of the rectangle.
        rightTop (ValuePoint2D): top right corner of the rectangle.
        color (Union[str, int]): color of the rectangle.
        name (str): name of the rectangle

    """
    def __init__(self, leftBottomCorner: ValuePoint2D, rightTopCorner: ValuePoint2D, color: Union[str, int] = "blue", name: str = ""):
        self.leftBottom = leftBottomCorner
        self.rightTop = rightTopCorner
        self.color = color
        self.name = name
    
    def __str__(self):
        return f"{self.name} LB: ({self.leftBottom.X}, {self.leftBottom.Y}), RT: ({self.rightTop.X}, {self.rightTop.Y})"
    
    def GetHeight(self)->float:
        """
        Height getter
        
        Returns:
            float: height of the rectangle
        """
        return self.rightTop.Y-self.leftBottom.Y

class VariableRectangle(VariableElement):
    """
    Class which represents rectangle element on the chart.
    Creates constraints for a given rectangle element.
    Width is maintained globaly, height localy.

    Attributes:
        width (Variable) : globaly declared Variable of width
        height (Variable) : localy declared Variable of height
        name (str) : name of the rectangle
        color (Union[str,int]) : color of the ractangle
        widthScale (float) : scale of the width. Resulting pixel width of the rectangle is widthScale*width.value().
        leftBottom (VariablePoint2D) : bottom left corner of the rectangle
        rightTop (VariablePoint2D) : top right corner of the rectangle
        horizontalPositionConstraint (Constraint) : constraint declaring the distance of vertical sides of the rectangle
        verticalPositionConstraint (Constraint) : constraint declaring the distance of horizontal sides of the rectangle
        spacingConstraint (Constraint) : constraint declaring left spacing of the rectangle on the canvas. It is not created during construction and has to be set externaly using SetSpacingConstraint method.
    """
    def __init__(self, width: Variable, name: str, color : Union[str,int] = "blue", widthScale : float = 1):
        self.height = Variable(f"{name}_height")
        self.width = width
        self.widthScale = widthScale
        self.name = name
        self.color = color
        self.leftBottom = VariablePoint2D(name+".leftBottom")
        self.rightTop = VariablePoint2D(name+".rightTop")

        self.horizontalPositionConstraint : Constraint = ((self.leftBottom.X + self.width * self.widthScale == self.rightTop.X) | "required")
        self.verticalPositionConstraint : Constraint = ((self.leftBottom.Y + self.height == self.rightTop.Y) | "required")
        self.spacingConstraint : Constraint | None = None 


    def ChangeName(self, name: str):
        """
        Name setter,

        Args:
            name (str): name of the rectangle
        """
        self.name = name
    
    def ChangeColor(self, color: Union[str,int]):
        """
        Color setter.

        Args:
            color (Union[str,int]): color of the rectangle
        """
        self.color = color
   
    def _getShapeConstraints(self) -> list[Constraint]:

        constraints = []
        if self.spacingConstraint is not None:
            constraints.append(self.spacingConstraint)
        constraints.append(self.horizontalPositionConstraint)
        constraints.append(self.verticalPositionConstraint)
        return constraints

    def _getPositionConstraints(self) -> list[Constraint]:
        return [(self.height >= 0)|"required",(self.leftBottom.X >= 0) | "required", (self.leftBottom.Y >= 0) | "required", (self.rightTop.X >= 0) | "required", (self.rightTop.Y >= 0) | "required"]

    def SetSpacingConstraint(self, spacingConstraint : Constraint):
        """
        Spacing constraint setter,

        Args:
            spacingConstraint (Constraint): new spacing constraint
        """
        self.spacingConstraint = spacingConstraint
    
    @inheritdocstring(VariableElement.GetAllConstraints)
    def GetAllConstraints(self)->list[Constraint]:
        return self._getShapeConstraints() + self._getPositionConstraints()
    

    def Value(self)->ValueRectangle:
        """
        Returns ValueRectangle representation of the instance.
        """
        return ValueRectangle(leftBottomCorner =  self.leftBottom.Value(), rightTopCorner = self.rightTop.Value(), color = self.color,  name = self.name)
    
    def GetName(self)->str:
        """
        Name getter.

        Returns:
            str: Name of the rectangle
        """
        return self.name
    
    def GetHeightVariable(self) -> Variable:
        """
        Height variable getter
        
        Returns:
            Variable: height variable of the rectangle
        """
        return self.height