from .plotelement import VariableRectangleGroup, VariablePoint2D, VariableCandle, ValueRectangle, ValuePoint2D
from .variableplot import VariableChart, VariableBarChart, VariableCandlesticChart
from kiwisolver import Variable, Constraint, Solver
from typing import Union




class ChartSolver:
    """
    Encapsulates Solver instance and VariableChart instance.
    """
    def __init__(self):
        self.solver : Solver = Solver()
        self.variableChart : VariableChart = None
        self.data = None
        pass

    def Solve(self):
        """
        Updates all variables
        """
        self.solver.updateVariables()
        self.Update()
    
    def Update(self):
        """
        Updates cached data
        """
        self.data = self.variableChart.Value()
    
    def GetOrigin(self):
        return ValuePoint2D(self.variableChart.origin.X.value(),self.variableChart.origin.Y.value())

    def GetSpacing(self):
        return self.variableChart.spacing.value()
    
    def GetWidth(self):
        return self.variableChart.width.value()
    
    def GetAxisHeight(self):
        return self.variableChart.yAxisHeight.value()
    
    def ChangeOrigin(self, newX: int, newY: int):
        self.solver.suggestValue(self.variableChart.origin.X, newX)
        self.solver.suggestValue(self.variableChart.origin.Y, newY)
        self.Solve()
    
    def ChangeAxisHeight(self, newHeight : int):
        self.solver.suggestValue(self.variableChart.yAxisHeight, newHeight)
        self.Solve()
    
    def ChangeWidth(self, width : int):
        self.solver.suggestValue(self.variableChart.width, width)
        self.Solve()
    
    def ChangeSpacing(self, spacing : int):
        self.solver.suggestValue(self.variableChart.spacing, spacing)
        self.Solve()






class BarChartSolver(ChartSolver):
    """
    ChartSolver version for bar chart and histogram.
    """
    def __init__(self, width: int, initialHeights: Union[list[int], list[list[int]]], spacing: int, innerSpacing: int, rectangleNames : list[list[str]], xCoordinate: int = 0, yCoordinate: int = 0, widthScalesForGroups : list[list[float]] = None):
        super().__init__()
        self.variableChart = VariableBarChart(width, initialHeights, spacing, innerSpacing, rectangleNames, xCoordinate, yCoordinate, widthScalesForGroups)

        barChartConstraints = set(self.variableChart.GetAllConstraints())
        
        for constraint in barChartConstraints:
            self.solver.addConstraint(constraint)

        self.solver.addEditVariable(self.variableChart.width, "strong")
        self.solver.addEditVariable(self.variableChart.spacing, "strong")
        self.solver.addEditVariable(self.variableChart.innerSpacing, "strong")


        for group in self.variableChart.groups:
            for rec in group:
                self.solver.addEditVariable(rec.height, "strong")
        
        self.solver.addEditVariable(self.variableChart.origin.X, "strong")
        self.solver.addEditVariable(self.variableChart.origin.Y, "strong")

        self.solver.addEditVariable(self.variableChart.yAxisHeight, "strong")
        self.solver.suggestValue(self.variableChart.yAxisHeight, max(max(group) for group in initialHeights)+10)
        
        self.Solve()
    
    def SetIntervalValues(self, intervals: list[list[float,float]]):
        self.variableChart.SetIntervalValues(intervals)

    def GetRectangleData(self):
        return self.data
    
    def GetRectangleDataAsList(self) -> list[ValueRectangle]:
        result = []
        data = self.GetRectangleData()
        for group in data:
            result.extend(group)
        return result

    def GetInnerSpacing(self):
        return self.variableChart.innerSpacing.value()
    
    def GetName(self, groupIndex: int, rectangleIndex: int):
        return self.variableChart.groups[groupIndex].rectangles[rectangleIndex].name
    
    def ChangeHeight(self, groupIndex: int, rectangleIndex: int, newHeight: int):
        self.solver.suggestValue(self.variableChart.groups[groupIndex].rectangles[rectangleIndex].height, newHeight)
        self.Solve()
    
    def ChangeInnerSpacing(self, newInnerSpacing: int):
        self.solver.suggestValue(self.variableChart.innerSpacing, newInnerSpacing)
        self.Solve()

    def ChangeColor(self, groupIndex: int, rectangleIndex: int, newColor: str):
        self.variableChart.ChangeColor(groupIndex,rectangleIndex, newColor)
        self.Update()
    
    def ChangeName(self,groupIndex: int, rectangleIndex: int, newColor: str):
        self.variableChart.ChangeName(groupIndex,rectangleIndex, newColor)
        self.Update()

class CandlestickChartSolver(ChartSolver):
    """
    ChartSolver version for candlestick chart.
    """
    def __init__(self, width : int, initialOpening : list[int], initialClosing : list[int], initialMinimum : list[int], initialMaximum : list[int], spacing : int, names : list[str], xCoordinate : int = 0, yCoordinate : int = 0):
        super().__init__()
        self.variableChart : VariableCandlesticChart = VariableCandlesticChart(width,initialOpening,initialClosing,initialMinimum,initialMaximum,spacing,names,xCoordinate,yCoordinate)

        for constraint in self.variableChart.GetAllConstraints():
            self.solver.addConstraint(constraint)

        self.solver.addEditVariable(self.variableChart.width, "strong")
        self.solver.addEditVariable(self.variableChart.spacing, "strong")
        self.solver.addEditVariable(self.variableChart.origin.X, "strong")
        self.solver.addEditVariable(self.variableChart.origin.Y, "strong")

        for index, candle in enumerate(self.variableChart.candles):
            self.solver.addEditVariable(candle.height, "strong")
            self.solver.addEditVariable(candle.wickBottom.Y, "strong")
            self.solver.addEditVariable(candle.wickTop.Y, "strong")
            self.solver.addEditVariable(candle.openingCorner.Y, "strong")

            self.solver.suggestValue(candle.wickBottom.Y, initialMinimum[index])
            self.solver.suggestValue(candle.wickTop.Y, initialMaximum[index])
            self.solver.suggestValue(candle.openingCorner.Y, initialOpening[index])

        self.solver.addEditVariable(self.variableChart.yAxisHeight, "strong")
        self.solver.suggestValue(self.variableChart.yAxisHeight, max(initialMaximum))
        
        
        self.Solve()
    
    def ChangeHeight(self, candleIndex : int, height : int):
        self.solver.suggestValue(self.variableChart.candles[candleIndex].height, height)
        self.Solve()
    
    def ChangeMaximum(self, candleIndex : int, yValue : int):
        topOfCandle = max(self.variableChart.candles[candleIndex].openingCorner.Y.value(), self.variableChart.candles[candleIndex].closingCorner.Y.value())
        self.solver.suggestValue(self.variableChart.candles[candleIndex].wickTop.Y, yValue if (yValue >= topOfCandle) else topOfCandle)
        self.Solve()

    def ChangeMinimum(self, candleIndex : int, yValue : int):
        self.solver.suggestValue(self.variableChart.candles[candleIndex].wickBottom.Y, yValue)
        self.Solve()

    def ChangeOpening(self, candleIndex: int, yValue : int):
        self.solver.suggestValue(self.variableChart.candles[candleIndex].openingCorner.Y, yValue)
        self.Solve()
    
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
        self.variableChart.candles[candleIndex].name = name
        self.Update()

    def GetCandleData(self):
        return self.data
    
    def GetName(self, candleIndex : int):
        return self.variableChart.candles[candleIndex].name