
from .variablechart import VariableChart, MINIMAL_WIDTH
from kiwiplots.chartelements import ValueCandle, VariableCandle, VariablePoint2D
from kiwisolver import Constraint, Variable
from typing import Union

class VariableCandlesticChart(VariableChart):
    """
    VariableChart version for candlestick chart
    """
    def __init__(self, positivity : list[bool], names : list[str]):
        super().__init__()

        self.candles = [VariableCandle(self.width, positivity[i], names[i]) for i in range(len(names))]
        
        self.leftMostCandleConstriant : Constraint = (self.candles[0].openingCorner.X >= self.origin.X) | "required"

        self._createCandleSpacingConstraints()

    def _createCandleSpacingConstraints(self):
        self.candles[0].SetSpacingConstraint((self.candles[0].openingCorner.X - self.spacing == self.origin.X) | "required") #TODO move spacing constraints out
        for index in range(1, len(self.candles)):
            self.candles[index].SetSpacingConstraint((self.candles[index-1].closingCorner.X + self.spacing == self.candles[index].openingCorner.X) | "required")
    
    def Value(self):
        return [candle.Value() for candle in self.candles]
    
    def _getCandleConstraints(self)-> list[Constraint]:
        result = []
        for candle in self.candles:
            result.extend(candle.GetAllConstraints())
        return result
    
    def _getPositionConstraints(self)-> list[Constraint]:
        return [(self.width >= MINIMAL_WIDTH) | "required", (self.spacing >= 0) | "required",self.leftMostCandleConstriant]

    def _getGlobalShapeConstraints(self)-> list[Constraint]:
        return []

    def GetAllConstraints(self)-> list[Constraint]:
        return self._getCandleConstraints() + self._getPositionConstraints() + self._getGlobalShapeConstraints()
    
    def ChangePositiveColor(self, color : Union[str,int]):
        for candle in self.candles:
            candle.ChangePositiveColor(color)
    
    def ChangeNegativeColor(self, color : Union[str,int]):
        for candle in self.candles:
            candle.ChangeNegativeColor(color)
    
    def SwitchNameVisibility(self, index : int):
        self.candles[index].SwitchNameVisibility()
    
    def ChangeName(self, index: int, name: str):
        self.candles[index].ChangeName(name)
    
    def GetHeightVariable(self, candleIndex : int) -> Variable:
        return self.candles[candleIndex].GetHeightVariable()
    
    def GetName(self, index: int):
        return self.candles[index].GetName()
    
    def GetOpeningCorner(self, index : int) -> VariablePoint2D:
        return self.candles[index].GetOpeningCorner()

    def GetClosingCorner(self, index : int) -> VariablePoint2D:
        return self.candles[index].GetClosingCorner()
    
    def GetWickBottom(self, index : int) -> VariablePoint2D:
        return self.candles[index].GetWickBottom()
    
    def GetWickTop(self, index : int) -> VariablePoint2D:
        return self.candles[index].GetWickTop()
    
    def AddCandle(self,name: str, isPositive: bool):
        lastCandle = self.candles[-1]
        newCandle = VariableCandle(self.width,True,name)
        newCandle.SetSpacingConstraint((lastCandle.closingCorner.X + self.spacing == newCandle.openingCorner.X) | "required")
        self.candles.append(newCandle)
        return newCandle, newCandle.GetAllConstraints()