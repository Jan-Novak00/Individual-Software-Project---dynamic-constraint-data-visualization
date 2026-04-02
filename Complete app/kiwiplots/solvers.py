from .plotelement import VariableRectangleGroup, VariablePoint2D, VariableCandle, ValueRectangle, ValuePoint2D, ValueCandle
from .variableplot import *
from kiwisolver import Variable, Constraint, Solver
from typing import Union
from abc import ABC, abstractmethod
import itertools as it
from .utils import *
import time
from warnings import deprecated
import warnings
import faulthandler
faulthandler.enable()

ALMOST_REQUIRED = 5e+8

class ChartSolver(ABC):
    """
    Encapsulates Solver instance and VariableChart instance.
    """
    def __init__(self):
        self.solver : Solver = Solver()
        self.variableChart : VariableChart = self._initializeVariableChart()
        self.data = None
        self._setConstraints()
        self._addEditVariables()
        self._initialSuggest()
        self.Solve()
    
    @abstractmethod
    def _addEditVariables(self):
        raise NotImplementedError("Method must be declared in subclass")

    @abstractmethod
    def _initialSuggest(self):
        raise NotImplementedError("Method must be declared in subclass")


    @abstractmethod
    def _initializeVariableChart(self) -> VariableChart:
        raise NotImplementedError("Method must be declared in subclass")

    @abstractmethod
    def _setConstraints(self):
        raise NotImplementedError("Method must be declared in subclass")

    @deprecated("Use switchConstraintLock instead. This method somethimes does not work due to an internal error of kiwisolver.removeEditVariable")
    def switchEditVariableLock(self, variable: Variable, locked: bool, defaultStrength = "strong"):
        value = variable.value()
        locked = not locked
        strength = defaultStrength if not locked else ALMOST_REQUIRED
        if self.solver.hasEditVariable(variable):
            self.solver.removeEditVariable(variable)
        self.solver.addEditVariable(variable,strength) # pyright: ignore[reportArgumentType]
        self.solver.suggestValue(variable,value)
        return locked
    
    def switchConstraintLock(self, variable : Variable, constraint : Constraint = None)->Constraint: # pyright: ignore[reportArgumentType]
        if not constraint:
            newC = (variable == variable.value()) | "required"
            self.solver.addConstraint(newC)
            return newC
        else:
            self.solver.removeConstraint(constraint)
            return None # pyright: ignore[reportReturnType]

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
        return self.variableChart.GetOrigin()

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
    
    def ChangeWidth(self, width : float):
        warnings.warn("Method ChartSolver.ChangeWidth is deprecated and will be removed.",category=DeprecationWarning,stacklevel=1)
        self.solver.suggestValue(self.variableChart.width, width)
        self.Solve()
    
    def ChangeSpacing(self, spacing : int):
        warnings.warn("Method ChartSolver.ChangeSpacing is deprecated and will be removed.",category=DeprecationWarning,stacklevel=1)
        self.solver.suggestValue(self.variableChart.spacing, spacing)
        self.Solve()
    

class BarChartSolver(ChartSolver):
    """
    ChartSolver version for bar chart and histogram.
    """
    def __init__(self, width: int, initialHeights: Union[list[int], list[list[int]]], spacing: int, innerSpacing: int, rectangleNames : list[list[str]], xCoordinate: int = 0, yCoordinate: int = 0, widthScalesForGroups : list[list[float]] = None):
        #Variable capture for correct parent constructor call
        self.initialHeights = initialHeights
        self.initialWidth = width
        self.initialSpacing = spacing
        self.initialInnerSpacing = innerSpacing
        self.initialRectangleNames = rectangleNames
        self.initialxCoordinate = xCoordinate
        self.initialyCoordinate = yCoordinate
        self.initialWidthScaleForGroups = widthScalesForGroups
        #Parent constructor call
        super().__init__()
        #Change of typehinting for variableChart
        self.variableChart : VariableBarChart = self.variableChart

    def _initializeVariableChart(self) -> VariableChart:
        return VariableBarChart(self.initialWidth, self.initialHeights, self.initialSpacing, self.initialInnerSpacing, self.initialRectangleNames, self.initialxCoordinate, self.initialyCoordinate, self.initialWidthScaleForGroups)

    def _setConstraints(self):
        barChartConstraints = set(self.variableChart.GetAllConstraints())
        for constraint in barChartConstraints:
            self.solver.addConstraint(constraint)
    
    def _addEditVariables(self):
        self.solver.addEditVariable(self.variableChart.width, "strong")
        self.solver.addEditVariable(self.variableChart.spacing, "strong")
        self.solver.addEditVariable(self.variableChart.innerSpacing, "strong")
        for group in self.variableChart.groups:
            for rec in group:
                self.solver.addEditVariable(rec.height, "strong")
        
        self.solver.addEditVariable(self.variableChart.origin.X, "strong")
        self.solver.addEditVariable(self.variableChart.origin.Y, "strong")
        self.solver.addEditVariable(self.variableChart.yAxisHeight, "strong")
    
    def _initialSuggest(self):
        self.solver.suggestValue(self.variableChart.yAxisHeight, max(max(group) for group in self.initialHeights)+10)
        self.solver.suggestValue(self.variableChart.origin.X, self.initialxCoordinate)
        self.solver.suggestValue(self.variableChart.origin.Y, self.initialyCoordinate)
        for ig in range(len(self.variableChart.groups)):
            group = self.variableChart.groups[ig]
            for ir, rec in enumerate(group):
                self.solver.suggestValue(rec.height,self.initialHeights[ig][ir]) # pyright: ignore[reportIndexIssue] #TODO type safety
    
    def _refreshSuggestions(self):
        self.solver.suggestValue(self.variableChart.width, self.variableChart.width.value())
        self.solver.suggestValue(self.variableChart.spacing, self.variableChart.spacing.value())
        self.solver.suggestValue(self.variableChart.innerSpacing, self.variableChart.innerSpacing.value())
        self.solver.suggestValue(self.variableChart.origin.X, self.variableChart.origin.X.value())
        
    def SetIntervalValues(self, intervals: list[tuple[float,float]]):
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
        return self.variableChart.GetName(groupIndex, rectangleIndex)
    
    def ChangeHeight(self, groupIndex: int, rectangleIndex: int, newHeight: int):
        self.solver.suggestValue(self.variableChart.GetHeightVariable(groupIndex, rectangleIndex), newHeight)
        
        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        innerSpacingConstrLock = self.switchConstraintLock(self.variableChart.innerSpacing)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
    
    def ChangeInnerSpacing(self, newInnerSpacing: int):
        self.solver.suggestValue(self.variableChart.innerSpacing, newInnerSpacing)
        self.Solve()

    def ChangeColor(self, groupIndex: int, rectangleIndex: int, newColor: str):
        self.variableChart.ChangeColor(groupIndex,rectangleIndex, newColor)
        self.Update()
    
    def ChangeName(self,groupIndex: int, rectangleIndex: int, newName: str):
        self.variableChart.ChangeName(groupIndex,rectangleIndex, newName)
        self.Update()
    
    def ChangeWidthX(self,groupIndex: int, rectangleIndex : int, newX : float):
        var = self.variableChart.groups[groupIndex].rectangles[rectangleIndex].rightTop.X
        if self.solver.hasEditVariable(var):
            self.solver.removeEditVariable(var)
        self.solver.addEditVariable(var, 1e+8)
        self.solver.suggestValue(var,newX)

        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        innerSpacingConstrLock = self.switchConstraintLock(self.variableChart.innerSpacing)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)

        self.Solve()
        self.solver.removeEditVariable(var)

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()

    
    def ChangeSpacingX(self,groupIndex: int, rectangleIndex : int, newX : float):
        var = self.variableChart.groups[groupIndex].rectangles[rectangleIndex].leftBottom.X
        if self.solver.hasEditVariable(var):
            self.solver.removeEditVariable(var)
        self.solver.addEditVariable(var, 1e+8)
        self.solver.suggestValue(var,newX)

        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        innerSpacingConstrLock = self.switchConstraintLock(self.variableChart.innerSpacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()
        self.solver.removeEditVariable(var)

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()
    
    def ChangeInnerSpacingX(self,groupIndex: int, rectangleIndex : int, newX : float):
        var = self.variableChart.groups[groupIndex].rectangles[rectangleIndex].leftBottom.X
        if self.solver.hasEditVariable(var):
            self.solver.removeEditVariable(var)
        self.solver.addEditVariable(var, 1e+8)
        self.solver.suggestValue(var,newX)

        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()
        self.solver.removeEditVariable(var)

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()
    
    def ChangeOrigin(self, newX: int, newY: int):
        innerSpacingConstrLock = self.switchConstraintLock(self.variableChart.innerSpacing)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)
        super().ChangeOrigin(newX, newY)
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()
    
    def ChangeAxisHeight(self, newHeight: int):
        innerSpacingConstrLock = self.switchConstraintLock(self.variableChart.innerSpacing)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)
        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        super().ChangeAxisHeight(newHeight)
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()
    
    def AddGroup(self, firstRectangleName: str, firstRectangleHeight: float):
        print("--- solver.AddGroup method start ---")
        newGroup, newConstraints = self.variableChart.AddGroup(firstRectangleName=firstRectangleName)
        for constr in newConstraints:
            self.solver.addConstraint(constr)

        newRectangle = newGroup.rectangles[0]
        
        self.solver.addEditVariable(newRectangle.height,"strong")
        self.solver.suggestValue(newRectangle.height, firstRectangleHeight)

        widthLock = self.switchConstraintLock(self.variableChart.width)
        spacingLock = self.switchConstraintLock(self.variableChart.spacing)
        innerSpacingLock = self.switchConstraintLock(self.variableChart.innerSpacing)

        self.Solve()

        self.switchConstraintLock(self.variableChart.width, widthLock)
        self.switchConstraintLock(self.variableChart.spacing, spacingLock)
        self.switchConstraintLock(self.variableChart.innerSpacing,innerSpacingLock)
        
        print("--- solver.AddGroup method end ---")
    
    def AddRectangle(self, name: str, groupIndex: int, recHeight: float):
        print("--- solver.AddRectangle start ---")
        height, constraintsToAdd, constraintsToRemove = self.variableChart.AddRectangle(groupIndex=groupIndex,name=name)
        for constr in constraintsToRemove:
            if self.solver.hasConstraint(constr):
                self.solver.removeConstraint(constr)
        for constr in constraintsToAdd:
            self.solver.addConstraint(constr)
        
        self.solver.addEditVariable(height,"strong")
        self.solver.suggestValue(height, recHeight)

        widthLock = self.switchConstraintLock(self.variableChart.width)
        spacingLock = self.switchConstraintLock(self.variableChart.spacing)
        innerSpacingLock = self.switchConstraintLock(self.variableChart.innerSpacing)

        self.Solve()

        self.switchConstraintLock(self.variableChart.width, widthLock)
        self.switchConstraintLock(self.variableChart.spacing, spacingLock)
        self.switchConstraintLock(self.variableChart.innerSpacing,innerSpacingLock)
        print("--- solver.AddRectangle end ---")
    
class CandlestickChartSolver(ChartSolver):
    """
    ChartSolver version for candlestick chart.
    """
    def __init__(self, width : int, initialOpening : list[int], initialClosing : list[int], initialMinimum : list[int], initialMaximum : list[int], spacing : int, names : list[str],xCoordinate : int = 0, yCoordinate : int = 0):
        self.initialWidth = width
        self.initialOpening = initialOpening
        self.initialClosing = initialClosing
        self.initialMinimum = initialMinimum
        self.initialMaximum = initialMaximum
        self.initialSpacing = spacing
        self.initialNames = names
        self.initialxCoordinate = xCoordinate
        self.initialyCoordinate = yCoordinate

        
        super().__init__()
        
        self.variableChart : VariableCandlesticChart = self.variableChart

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
        for index, candle in enumerate(self.variableChart.candles):
            self.solver.suggestValue(candle.wickBottom.Y, self.initialMinimum[index])
            self.solver.suggestValue(candle.wickTop.Y, self.initialMaximum[index])
            self.solver.suggestValue(candle.openingCorner.Y, self.initialOpening[index])
            self.solver.suggestValue(candle.height, self.initialClosing[index]-self.initialOpening[index])

    def _initializeVariableChart(self) -> VariableChart:
        return VariableCandlesticChart(self.initialWidth, self.initialOpening, self.initialClosing, self.initialMinimum, self.initialMaximum, self.initialSpacing, self.initialNames, self.initialxCoordinate,self.initialyCoordinate)

    def _setConstraints(self):
        for constraint in self.variableChart.GetAllConstraints():
            self.solver.addConstraint(constraint)
    
    def ChangeHeight(self, candleIndex : int, height : int):
        self.solver.suggestValue(self.variableChart.GetHeightVariable(candleIndex), height)
        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
    
    def ChangeMaximum(self, candleIndex : int, yValue : int):
        topOfCandle = max(self.variableChart.GetOpeningCorner(candleIndex).Y.value(), self.variableChart.GetClosingCorner(candleIndex).Y.value())
        self.solver.suggestValue(self.variableChart.GetWickTop(candleIndex).Y, yValue if (yValue >= topOfCandle) else topOfCandle)
        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]

    def ChangeMinimum(self, candleIndex : int, yValue : int):
        self.solver.suggestValue(self.variableChart.GetWickBottom(candleIndex).Y, yValue)
        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]

    def ChangeOpening(self, candleIndex: int, yValue : int):
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
        print("--- solver.AddCandle method start ---")
        spacingLock = self.switchConstraintLock(self.variableChart.spacing)
        widthLock = self.switchConstraintLock(self.variableChart.width)

        newCandle, newConstraints = self.variableChart.AddCandle(name)
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

        print("--- solver.AddCandle method end ---")
        pass


class LineChartSolver(ChartSolver):
    def __init__(self, width : int, initialValues : list[float], pointNames : list[str], xCoordinate : int = 0, yCoordinate : int = 0, padding : float = 0):
        self.initialWidth : int = width
        self.initialValues : list[float] = initialValues
        self.initialPointNames : list[str] = pointNames
        self.initialxCoordinate = xCoordinate
        self.initialyCoordinate = yCoordinate
        self.initialPadding = padding
        super().__init__()
        self.variableChart : VariableLineChart = self.variableChart
        self.originLocked = False
        self.paddingLock = False
        

    def _initializeVariableChart(self):
        return VariableLineChart(self.initialWidth,self.initialValues, self.initialPointNames, self.initialxCoordinate, self.initialyCoordinate)
    
    def _setConstraints(self):
        constraints : set[Constraint] = set(self.variableChart.GetAllConstraints())
        for constraint in constraints:
            self.solver.addConstraint(constraint)
    
    def _addEditVariables(self):
        chart : VariableLineChart = self.variableChart
        self.solver.addEditVariable(self.variableChart.width, "strong")
        self.solver.addEditVariable(self.variableChart.origin.X, "strong")
        self.solver.addEditVariable(self.variableChart.origin.Y, "strong")
        self.solver.addEditVariable(self.variableChart.yAxisHeight, "strong")
        self.solver.addEditVariable(self.variableChart.GetPadding(), "strong")
        for line in chart.lines:
            self.solver.addEditVariable(line.leftHeight, "strong")
            self.solver.addEditVariable(line.rightHeight, "medium")
    
    def _initialSuggest(self):
        chart : VariableLineChart = self.variableChart
        self.solver.suggestValue(self.variableChart.yAxisHeight, max(self.initialValues)+10)
        self.solver.suggestValue(chart.width, self.initialWidth)
        self.solver.suggestValue(chart.origin.X, self.initialxCoordinate)
        self.solver.suggestValue(chart.origin.Y,self.initialyCoordinate)
        self.solver.suggestValue(chart.GetPadding(),self.initialPadding)
        valuePairs = list(pairwise(self.initialValues))
        for i in range(len(chart.lines)):
            line = chart.lines[i]
            values = valuePairs[i]
            self.solver.suggestValue(line.leftHeight, values[0])
            self.solver.suggestValue(line.rightHeight,values[1])

    def GetLineData(self):
        return [line.Value() for line in self.variableChart.lines]

    def GetPoints(self):
        lines = self.GetLineData()
        if len(lines) == 0:
            return []
        return [lines[0].leftEnd] + [line.rightEnd for line in lines]
    
    def ChangeHeight(self, pointIndex: int, height: float):
        self.solver.suggestValue(self.variableChart.GetHeightList()[pointIndex], height)
        self.Solve()
    
    def ChangePadding(self, newPadding: float):
        self.solver.suggestValue(self.variableChart.GetPadding(),newPadding)
        self.Solve()
    
    def GetPadding(self):
        return self.variableChart.GetPadding().value()

    def ChangeX(self, pointIndex: int, newX: float):
        lineIndex = pointIndex if pointIndex == 0 else pointIndex - 1
        var = self.variableChart.lines[lineIndex].leftEnd.X if pointIndex == 0 else self.variableChart.lines[lineIndex].rightEnd.X
        strength = "strong" if pointIndex == 0 else 1e+8 # magic number = stronger than strong
        if (not self.solver.hasEditVariable(var)):
                self.solver.addEditVariable(var,strength)
        self.solver.suggestValue(var, newX)
        
        originLock = self.switchConstraintLock(self.variableChart.origin.X)
        paddingLock = self.switchConstraintLock(self.variableChart.padding)
        self.Solve()
        self.solver.removeEditVariable(var)
        self.solver.suggestValue(self.variableChart.width, self.variableChart.width.value())
        self.switchConstraintLock(self.variableChart.padding,paddingLock)
        self.switchConstraintLock(self.variableChart.origin.X,originLock)
    
    def AddPoint(self, value: float, name: str): #NEW FUNCTION
        print("--- solver.AddPoint method start ---")
                              #TODO nebude fungova pro prazdny
        lastPointValue = self.variableChart.lines[-1].rightHeight.value()
        newLine, newConstraints = self.variableChart.AddPoint(name)
        self.solver.addEditVariable(newLine.leftHeight, "strong")
        self.solver.addEditVariable(newLine.rightHeight, "medium")
        for constr in newConstraints:
            self.solver.addConstraint(constr)
        self.solver.suggestValue(newLine.leftHeight,lastPointValue)
        self.solver.suggestValue(newLine.rightHeight,value)
        print("new constraints added -> solving")
        self.Solve()
        print("last line =",self.GetLineData()[-1])
        print(self.solver.dumps())
        print("--- solver.AddPoint method end ---")
        pass


class HistogramSolver(ChartSolver):
    @classmethod
    def new(cls,width: int, initialHeights: list[int], intervals: list[tuple[float,float]], paddingLeft: int, widhtScalesForGroups : list[list[float]], xCoordinate : int = 0, yCoordinate : int = 0):
        solver : BarChartSolver = BarChartSolver(width=width,
                                                           initialHeights=initialHeights,
                                                           spacing=paddingLeft,
                                                           innerSpacing=0,
                                                           rectangleNames=[["" for _ in initialHeights]],
                                                           xCoordinate=xCoordinate,
                                                           yCoordinate=yCoordinate,
                                                           widthScalesForGroups=widhtScalesForGroups)
        solver.SetIntervalValues(intervals=intervals)
        return cls(solver)
        


    def __init__(self,solver : BarChartSolver):
        # solver has to have set intervals #TODO
        self.innerSolver : BarChartSolver = solver
    
    def _initializeVariableChart(self) -> VariableChart:
        return None # pyright: ignore[reportReturnType]
    
    def _setConstraints(self):
        return
    
    def _addEditVariables(self):
        return
    
    def _initialSuggest(self):
        return
    
    def Solve(self):
        self.innerSolver.Solve()
    
    def Update(self):
        self.innerSolver.Update()
    
    def GetOrigin(self):
        return self.innerSolver.GetOrigin()
    
    def GetSpacing(self):
        return self.innerSolver.GetSpacing()
    
    def GetWidth(self):
        return self.innerSolver.GetWidth()
    
    def GetAxisHeight(self):
        return self.innerSolver.GetAxisHeight()
    
    def ChangeOrigin(self, newX: int, newY: int):
        self.innerSolver.ChangeOrigin(newX,newY)
    
    def ChangeAxisHeight(self, newHeight : int):
        self.innerSolver.ChangeAxisHeight(newHeight)
    
    def ChangeWidth(self, width: float):
        self.innerSolver.ChangeWidth(width)
    
    def ChangeSpacing(self, spacing: int):
        self.innerSolver.ChangeSpacing(spacing)
    
    def GetRectangleData(self):
        return self.innerSolver.GetRectangleData()
    
    def GetRectangleDataAsList(self):
        return self.GetRectangleDataAsList()
    
    def GetInnerSpacing(self):
        warnings.warn("GetInnerSpacing called on histogram!!!",category=RuntimeWarning,stacklevel=1)
        return 0 #odebrat
    
    def GetName(self, groupIndex: int, rectangleIndex: int):
        return self.innerSolver.GetName(groupIndex,rectangleIndex)
    
    def ChangeHeight(self, groupIndex: int, rectangleIndex: int, newHeight: int):
        self.innerSolver.ChangeHeight(groupIndex,rectangleIndex,newHeight)
    
    def ChangeInnerSpacing(self, newInnerSpacing: int):
        warnings.warn("ChangeInnerSpacing called on histogram!!!",category=RuntimeWarning,stacklevel=1)
        return
    
    def ChangeColor(self, groupIndex: int, rectangleIndex: int, newColor: str):
        self.innerSolver.ChangeColor(groupIndex,rectangleIndex,newColor)
    
    def ChangeName(self,groupIndex: int, rectangleIndex: int, newName: str):
        self.innerSolver.ChangeName(groupIndex, rectangleIndex, newName)
    
    def ChangeWidthX(self,groupIndex: int, rectangleIndex : int, newX : float):
        self.innerSolver.ChangeWidthX(groupIndex,rectangleIndex,newX)
    
    def ChangeSpacingX(self,groupIndex: int, rectangleIndex : int, newX : float):
        self.innerSolver.ChangeSpacingX(groupIndex,rectangleIndex,newX)
    
    def ChangeInnerSpacingX(self,groupIndex: int, rectangleIndex : int, newX : float):
        warnings.warn("ChangeInnerSpacingX called on histogram!!!",category=RuntimeWarning,stacklevel=1)
        return
    
    def AddRectangle(self,start: float, end: float, height: float):
        print("--- solver.AddRectangle start ---")
        print("TODO")
        print("--- solver.AddRectangle end ---")
        pass