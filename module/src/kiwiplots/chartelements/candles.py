"""
    This file declares classes which are used to represent candles in candlestick chart.
    Terminology:
        - opening corner: corner of the candle whose y coordiante represents the vertical position of the opening side of the candle (represents opening value). Is also always on the left side of the candle.
        - closing corner: corner of the candle whose y coordiante represents the vertical position of the closing side of the candle (represents closing value). Is also always on the right side of the candle.
        - wick top: top of the candle wick, represents high value.
        - wick bottom: bottom of the candle wick, represents low value.
"""
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
    Class which represents a candle on the canvas for candlestick chart.
    Creates constraints for a given candle.
    Width is maintained globaly, height localy.

    Attributes:
        width (Variable): globaly declared Variable of width
        height (Variable): localy declared Variable of candle height
        openingCorner (VariablePoint2D): opening corner of the candle
        closingCorner (VariablePoint2D): closing corner of the candle
        wickTop (VariablePoint2D): candle's wick top
        wickBottom (VariablePoint2D): candle's wick bottom
        name (str): name of the candle
        positiveColor (Union[str,int]): color of the candle when it represents positive value
        negativeColor (Union[str,int]): color of the candle when it represents negative value
        wickXConstraint (Constraint): constraint for the wick x coordiante
        straightWickConstraint (Constraint): constraint, which states that the wick must be vertical
        wickBottomTrueMinimumConstraints (list[Constraint]): constraints, which state that wickBottom is the bottom most point of the candle
        wickTopTrueMaximumConstraints (list[Constraint]): constraints, which state that wickTop is the top most point of the candle
        nameVisible (bool) : true if the name of the candle visible
    """    
    def __init__(self, width: Variable, isPositive : bool, name: str = "candle", positiveColor : Union[str,int] = "green", negativeColor : Union[str,int]="red"):
        
        super().__init__(width, name, positiveColor if isPositive else negativeColor)

        self.openingCorner : VariablePoint2D = self.leftBottom
        self.closingCorner : VariablePoint2D = self.rightTop

        self.wickBottom : VariablePoint2D = VariablePoint2D(self.name+".wickBottom")
        self.wickTop : VariablePoint2D = VariablePoint2D(self.name+".wickTop")
        
        self.wickXConstraint : Constraint = ((self.wickBottom.X == (self.leftBottom.X + self.rightTop.X)/2) | "required")
        self.straightWickConstraint : Constraint = ((self.wickBottom.X == self.wickTop.X) | "required")

        self.wickBottomTrueMinimumConstraints : list[Constraint] = [((self.wickBottom.Y <= self.closingCorner.Y) | "required"), ((self.wickBottom.Y <= self.openingCorner.Y) | "required")]
        self.wickTopTrueMaximumConstraints : list[Constraint] = [((self.wickTop.Y >= self.closingCorner.Y) | "required"), ((self.wickTop.Y >= self.openingCorner.Y) | "required")]

        self.positiveColor : Union[str,int] = positiveColor
        self.negativeColor : Union[str,int] = negativeColor
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
        Returns all constraints of the candle.
        """
        return self._getShapeConstraints() + self._getPositionConstraints()

    
    def Value(self):
        """
        Return ValueCandle instance, which represents a snapshot of the candle.
        """
        return ValueCandle(openingCorner=self.openingCorner.Value(), 
                           closingCorner=self.closingCorner.Value(), 
                           wickBottom=self.wickBottom.Value(), 
                           wickTop=self.wickTop.Value(), 
                           color=self.positiveColor if self.height.value() >= 0 
                                                    else self.negativeColor, 
                           name = self.name, 
                           nameVisible = self.nameVisible)
        
    def ChangePositiveColor(self, color: Union[str,int]):
        """Positive color setter.

        Args:
            color (Union[str,int]): new positive color
        """
        self.positiveColor = color

    def ChangeNegativeColor(self, color: Union[str,int]):
        """Negative value setter

        Args:
            color (Union[str,int]): _new newgative color
        """
        self.negativeColor = color

    def SwitchNameVisibility(self):
        """Negates the visibility flag of the candle.
        """
        self.nameVisible = not self.nameVisible
    
    def GetOpeningCorner(self) -> VariablePoint2D:
        """Opening corner getter.

        Returns:
            VariablePoint2D: Opening corner
        """
        return self.openingCorner
    
    def GetClosingCorner(self) -> VariablePoint2D:
        """Closing corner getter

        Returns:
            VariablePoint2D: _description_
        """
        return self.closingCorner
    
    def GetWickBottom(self) -> VariablePoint2D:
        """Wick bottom getter

        Returns:
            VariablePoint2D: wick bottom
        """
        return self.wickBottom
    
    def GetWickTop(self) -> VariablePoint2D:
        """Wick top getter

        Returns:
            VariablePoint2D: wick top
        """
        return self.wickTop
