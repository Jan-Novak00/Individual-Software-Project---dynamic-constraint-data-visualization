from kiwisolver import Constraint, Variable
from .rectangles import *

class ValueCandle(ValueRectangle):
    """
    Holds information about a given candle.
    """
    def __init__(self, openingCorner : ValuePoint2D, closingCorner : ValuePoint2D, wickBottom : ValuePoint2D, wickTop : ValuePoint2D, color : Union[str,int] = "blue", name : str = "", nameVisible : bool = False):
        super().__init__(openingCorner, closingCorner, color, name)
        self.openingCorner : ValuePoint2D = self.leftBottom
        self.closingCorner : ValuePoint2D = self.rightTop

        self.wickBottom : ValuePoint2D = wickBottom
        self.wickTop : ValuePoint2D = wickTop
        self.nameVisible = nameVisible
    def __str__(self):
        return f"{self.name} opening: ({self.leftBottom.X}, {self.leftBottom.Y}), closing: ({self.rightTop.X}, {self.rightTop.Y}) Wick: bottom: ({self.wickBottom.X}, {self.wickBottom.Y}) top: ({self.wickTop.X}, {self.wickTop.Y})"

class VariableCandle(VariableRectangle):
    """
    Creates constraints for a given candle.
    Width is maintained globaly, height localy
    Arguments:
        width - globaly declared Variable of width
        height - pixel height of the rectangle
        openingPosition - pixel height of the candle
        minPosition - pixel height of the minimum
        maxPosition - pixel height of the maximum
        name - name of the candle
        positiveColor - color of the candle when it represents positive value
        negativeColor - color of the candle when it represents negative value
        widthScale - scale of the width. Resulting pixel width of the rectangle is widthScale*width.value()
    """    
    def __init__(self, width: Variable, isPositive : bool, name: str = "candle", positiveColor="green", negativeColor="red"):
        
        super().__init__(width, name, positiveColor if isPositive else negativeColor)

        self.openingCorner : VariablePoint2D = self.leftBottom
        self.closingCorner : VariablePoint2D = self.rightTop

        self.wickBottom : VariablePoint2D = VariablePoint2D(self.name+".wickBottom")
        self.wickTop : VariablePoint2D = VariablePoint2D(self.name+".wickTop")
        
        self.wickXConstraint : Constraint = ((self.wickBottom.X == (self.leftBottom.X + self.rightTop.X)/2) | "required")
        self.straightWickConstraint : Constraint = ((self.wickBottom.X == self.wickTop.X) | "required")

        self.wickBottomTrueMinimumConstraints : list[Constraint] = [((self.wickBottom.Y <= self.closingCorner.Y) | "required"), ((self.wickBottom.Y <= self.openingCorner.Y) | "required")]
        self.wickTopTrueMaximumConstraints : list[Constraint] = [((self.wickTop.Y >= self.closingCorner.Y) | "required"), ((self.wickTop.Y >= self.openingCorner.Y) | "required")]

        self.positiveColor = positiveColor
        self.negativeColor = negativeColor
        self.nameVisible : bool = False
    
    def _getShapeConstraints(self) -> list[Constraint]:
        result = super()._getShapeConstraints()
        result.extend([self.wickXConstraint, self.straightWickConstraint])
        return result
    
    def _getPositionConstraints(self) -> list[Constraint]:
        return [(self.closingCorner.X >= 0) | "required", (self.openingCorner.X >= 0) | "required", (self.wickBottom.X >= 0) | "required", (self.wickTop.X >= 0) | "required"] \
                +self.wickBottomTrueMinimumConstraints+self.wickTopTrueMaximumConstraints
        
    def GetAllConstraints(self):
        """
        Returns all constraints, both from __iter__ method and constraints which specify domain of variables
        """
        return self._getShapeConstraints() + self._getPositionConstraints()

    
    def Value(self):
        """
        Return ValueCandle instances for each rectangle in the group as a list
        """
        return ValueCandle(self.openingCorner.Value(), self.closingCorner.Value(), self.wickBottom.Value(), self.wickTop.Value(), self.positiveColor if self.height.value() >= 0 else self.negativeColor, self.name, self.nameVisible)
        
    def ChangePositiveColor(self, color: Union[str,int]):
        self.positiveColor = color
    def ChangeNegativeColor(self, color: Union[str,int]):
        self.negativeColor = color
    def SwitchNameVisibility(self):
        self.nameVisible = not self.nameVisible
    
    def GetOpeningCorner(self) -> VariablePoint2D:
        return self.openingCorner
    
    def GetClosingCorner(self) -> VariablePoint2D:
        return self.closingCorner
    
    def GetWickBottom(self) -> VariablePoint2D:
        return self.wickBottom
    
    def GetWickTop(self) -> VariablePoint2D:
        return self.wickTop
