
from .variablechart import VariableChart, MINIMAL_WIDTH
from kiwiplots.chartelements import ValueCandle, VariableCandle, VariablePoint2D
from kiwisolver import Constraint, Variable
from typing import Union

class VariableCandlesticChart(VariableChart):
    """VariableChart implementation for candlestick charts.

    Manages a sequence of candles with shared width and spacing variables, and
    provides methods for modifying candle properties at runtime.

    Attributes:
        candles (list[VariableCandle]): The individual candles of the chart.
    """
    def __init__(self, positivity : list[bool], names : list[str]):
        """Initializes the candlestick chart with positivity flags and candle names.

        Args:
            positivity (list[bool]): Whether each candle is positive (closing > opening).
            names (list[str]): Display names for each candle.
        """
        super().__init__()

        self.candles = [VariableCandle(self.width, positivity[i], names[i]) for i in range(len(names))]
        
        #self.leftMostCandleConstriant : Constraint = (self.candles[0].openingCorner.X >= self.origin.X) | "required" #redundant

        self._createCandleSpacingConstraints()

    def _createCandleSpacingConstraints(self):
        """Creates constraints that space all candles relative to the origin and each other."""
        self.candles[0].SetSpacingConstraint((self.candles[0].openingCorner.X - self.spacing == self.origin.X) | "required")
        for index in range(1, len(self.candles)):
            self.candles[index].SetSpacingConstraint((self.candles[index-1].closingCorner.X + self.spacing == self.candles[index].openingCorner.X) | "required")
    
    def Value(self):
        """Returns the resolved data for all candles."""
        return [candle.Value() for candle in self.candles]
    
    def _getCandleConstraints(self)-> list[Constraint]:
        """Collects and returns all constraints from every candle."""
        result = []
        for candle in self.candles:
            result.extend(candle.GetAllConstraints())
        return result
    
    def _getPositionConstraints(self)-> list[Constraint]:
        """Returns constraints that enforce minimum width and non-negative spacing."""
        return [(self.width >= MINIMAL_WIDTH) | "required", (self.spacing >= 0) | "required"]

    def _getGlobalShapeConstraints(self)-> list[Constraint]:
        """Returns global shape constraints (currently none)."""
        return []

    def GetAllConstraints(self)-> list[Constraint]:
        """Returns all constraints for the candlestick chart layout."""
        return self._getCandleConstraints() + self._getPositionConstraints() + self._getGlobalShapeConstraints()
    
    def ChangePositiveColor(self, color : Union[str,int]):
        """Changes the color of all positive candles.

        Args:
            color (Union[str, int]): New color value.
        """
        for candle in self.candles:
            candle.ChangePositiveColor(color)
    
    def ChangeNegativeColor(self, color : Union[str,int]):
        """Changes the color of all negative candles.

        Args:
            color (Union[str, int]): New color value.
        """
        for candle in self.candles:
            candle.ChangeNegativeColor(color)
    
    def SwitchNameVisibility(self, index : int):
        """Toggles the name label visibility for the candle at the given index.

        Args:
            index (int): Index of the candle.
        """
        self.candles[index].SwitchNameVisibility()
    
    def ChangeName(self, index: int, name: str):
        """Changes the display name of the candle at the given index.

        Args:
            index (int): Index of the candle.
            name (str): New name string.
        """
        self.candles[index].ChangeName(name)
    
    def GetHeightVariable(self, candleIndex : int) -> Variable:
        """Returns the kiwisolver height variable for the specified candle."""
        return self.candles[candleIndex].GetHeightVariable()
    
    def GetName(self, index: int):
        """Returns the display name of the candle at the given index."""
        return self.candles[index].GetName()
    
    def GetOpeningCorner(self, index : int) -> VariablePoint2D:
        """Returns the opening corner variable point of the candle at the given index."""
        return self.candles[index].GetOpeningCorner()

    def GetClosingCorner(self, index : int) -> VariablePoint2D:
        """Returns the closing corner variable point of the candle at the given index."""
        return self.candles[index].GetClosingCorner()
    
    def GetWickBottom(self, index : int) -> VariablePoint2D:
        """Returns the bottom wick variable point of the candle at the given index."""
        return self.candles[index].GetWickBottom()
    
    def GetWickTop(self, index : int) -> VariablePoint2D:
        """Returns the top wick variable point of the candle at the given index."""
        return self.candles[index].GetWickTop()
    
    def AddCandle(self,name: str, isPositive: bool):
        """Appends a new candle to the end of the chart.

        Args:
            name (str): Display name for the new candle.
            isPositive (bool): Whether the new candle is positive.

        Returns:
            tuple: The new VariableCandle and the list of constraints to add.
        """
        lastCandle = self.candles[-1]
        newCandle = VariableCandle(self.width,True,name)
        newCandle.SetSpacingConstraint((lastCandle.closingCorner.X + self.spacing == newCandle.openingCorner.X) | "required")
        self.candles.append(newCandle)
        return newCandle, newCandle.GetAllConstraints()