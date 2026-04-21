from .chartsolver import ChartSolver
from kiwiplots.variablechart import VariableCandlesticChart, VariableChart
from typing import Union
from kiwiplots.plotelement import ValueCandle, VariableCandle

class CandlestickChartSolver(ChartSolver):
    """
    ChartSolver version for candlestick chart.
    """
    def __init__(self, variableChart : VariableCandlesticChart, width : int, initialOpening : list[float], initialClosing : list[float], initialMinimum : list[float], initialMaximum : list[float], spacing : int, xCoordinate : int = 0, yCoordinate : int = 0):
        self.initialWidth = width
        self.initialOpening = initialOpening
        self.initialClosing = initialClosing
        self.initialMinimum = initialMinimum
        self.initialMaximum = initialMaximum
        self.initialSpacing = spacing
        self.initialxCoordinate = xCoordinate
        self.initialyCoordinate = yCoordinate

        super().__init__(variableChart)
        
        self.variableChart : VariableCandlesticChart = self.variableChart
        self.lockedCandles : set[int] = set()

    def _addEditVariables(self):
        self.solver.addEditVariable(self.variableChart.width, "strong")
        self.solver.addEditVariable(self.variableChart.spacing, "strong")
        self.solver.addEditVariable(self.variableChart.origin.X, "strong")
        self.solver.addEditVariable(self.variableChart.origin.Y, "strong")
        self.solver.addEditVariable(self.variableChart.yAxisHeight, "strong")
        for candle in self.variableChart.candles:
            self.solver.addEditVariable(candle.height, "strong")
            self.solver.addEditVariable(candle.wickBottom.Y, "strong")
            self.solver.addEditVariable(candle.wickTop.Y, "strong")
            self.solver.addEditVariable(candle.openingCorner.Y, "strong")

    def _initialSuggest(self):
        self.solver.suggestValue(self.variableChart.yAxisHeight, max(self.initialMaximum))
        self.solver.suggestValue(self.variableChart.origin.X, self.initialxCoordinate)
        self.solver.suggestValue(self.variableChart.origin.Y, self.initialyCoordinate)
        self.solver.suggestValue(self.variableChart.width,self.initialWidth)
        self.solver.suggestValue(self.variableChart.spacing,self.initialSpacing)
        for index, candle in enumerate(self.variableChart.candles):
            self.solver.suggestValue(candle.wickBottom.Y, self.initialMinimum[index])
            self.solver.suggestValue(candle.wickTop.Y, self.initialMaximum[index])
            self.solver.suggestValue(candle.openingCorner.Y, self.initialOpening[index])
            self.solver.suggestValue(candle.height, self.initialClosing[index]-self.initialOpening[index])

    #def _initializeVariableChart(self) -> VariableChart:
    #    return VariableCandlesticChart([self.initialOpening[i] - self.initialClosing[i] >= 0 for i in range(len(self.initialOpening))], self.initialNames)

    
    def SwitchCandleLock(self, index: int)->bool:
        if index in self.lockedCandles:
            self.lockedCandles.remove(index)
            return False
        else:
            self.lockedCandles.add(index)
            return True
    
    def ChangeHeight(self, candleIndex : int, height : int):
        if candleIndex in self.lockedCandles:
            return
        self.solver.suggestValue(self.variableChart.GetHeightVariable(candleIndex), height)
        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock)
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)  
        self.switchConstraintLock(self.variableChart.width, widthConstrLock)
    def ChangeMaximum(self, candleIndex : int, yValue : int):
        if candleIndex in self.lockedCandles:
            return
        topOfCandle = max(self.variableChart.GetOpeningCorner(candleIndex).Y.value(), self.variableChart.GetClosingCorner(candleIndex).Y.value())
        self.solver.suggestValue(self.variableChart.GetWickTop(candleIndex).Y, yValue if (yValue >= topOfCandle) else topOfCandle)
        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock)
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)
        self.switchConstraintLock(self.variableChart.width, widthConstrLock)

    def ChangeMinimum(self, candleIndex : int, yValue : int):
        if candleIndex in self.lockedCandles:
            return
        self.solver.suggestValue(self.variableChart.GetWickBottom(candleIndex).Y, yValue)
        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock)
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)
        self.switchConstraintLock(self.variableChart.width, widthConstrLock)

    def ChangeOpening(self, candleIndex: int, yValue : int):
        if candleIndex in self.lockedCandles:
            return
        self.solver.suggestValue(self.variableChart.GetOpeningCorner(candleIndex).Y, yValue)
        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
    
    def SwitchNameVisibility(self, index : int):
        self.variableChart.SwitchNameVisibility(index)
        self.Update()

    def ChangePositiveColor(self, color : Union[str, int]):
        self.variableChart.ChangePositiveColor(color)
        self.Update()

    def ChangeNegativeColor(self, color : Union[str, int]):
        self.variableChart.ChangeNegativeColor(color)
        self.Update()
    
    def ChangeName(self, candleIndex : int, name : str):
        self.variableChart.ChangeName(candleIndex, name)
        self.Update()

    def GetCandleData(self)->list[ValueCandle]:
        return self.data # type: ignore
    
    def GetName(self, candleIndex : int):
        return self.variableChart.GetName(candleIndex)
    
    def _refreshSuggestions(self):
        self.solver.suggestValue(self.variableChart.width, self.variableChart.width.value())
        self.solver.suggestValue(self.variableChart.spacing, self.variableChart.spacing.value())
        self.solver.suggestValue(self.variableChart.origin.X, self.variableChart.origin.X.value())
        
    
    def ChangeWidthX(self, candleIndex : int, newX : float)->None:
        var = self.variableChart.candles[candleIndex].rightTop.X
        if self.solver.hasEditVariable(var):
            self.solver.removeEditVariable(var)
        self.solver.addEditVariable(var, 1e+8)
        self.solver.suggestValue(var,newX)

        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)

        self.Solve()
        self.solver.removeEditVariable(var)

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()
    
    def ChangeSpacingX(self,candleIndex: int, newX : float):
        var = self.variableChart.candles[candleIndex].leftBottom.X
        if self.solver.hasEditVariable(var):
            self.solver.removeEditVariable(var)
        self.solver.addEditVariable(var, 1e+8)
        self.solver.suggestValue(var,newX)

        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()
        self.solver.removeEditVariable(var)

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()
    
    def ChangeOrigin(self, newX: int, newY: int):
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)
        super().ChangeOrigin(newX, newY)
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()
    
    def ChangeAxisHeight(self, newHeight: int):
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)
        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        super().ChangeAxisHeight(newHeight)
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()
    
    def AddCandle(self, name: str, opening: float, closing: float, minimum: float, maximum: float):
        spacingLock = self.switchConstraintLock(self.variableChart.spacing)
        widthLock = self.switchConstraintLock(self.variableChart.width)

        newCandle, newConstraints = self.variableChart.AddCandle(name, opening-closing >=0)
        for constr in newConstraints:
            self.solver.addConstraint(constr)
        self.solver.addEditVariable(newCandle.height,"strong")
        self.solver.addEditVariable(newCandle.openingCorner.Y,"strong")
        self.solver.addEditVariable(newCandle.wickBottom.Y,"strong")
        self.solver.addEditVariable(newCandle.wickTop.Y,"strong")

        self.solver.suggestValue(newCandle.height, closing-opening)
        self.solver.suggestValue(newCandle.openingCorner.Y, opening)
        self.solver.suggestValue(newCandle.wickBottom.Y,minimum)
        self.solver.suggestValue(newCandle.wickTop.Y,maximum)

        self.Solve()
        self.switchConstraintLock(self.variableChart.spacing,spacingLock)
        self.switchConstraintLock(self.variableChart.width,widthLock)
