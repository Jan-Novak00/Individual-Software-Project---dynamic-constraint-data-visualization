from .chartsolver import ChartSolver
from kiwisolver import Constraint, Solver
from kiwiplots.variablechart import VariableLineChart, VariableChart
from typing import Union
from kiwiplots.chartelements import ValueRectangle, VariableRectangle
from kiwiplots.utils import *
from kiwiplots.utils import inheritdocstring

class LineChartSolver(ChartSolver):
    """
    ChartSolver version for line chart.
    Manages constraint solving for line charts.
    """
    def __init__(self, variableChart: VariableLineChart, width : int, initialValues : list[float], xCoordinate : int = 0, yCoordinate : int = 0, padding : float = 0):

        self.initialWidth : int = width
        self.initialValues : list[float] = initialValues
        self.initialxCoordinate = xCoordinate
        self.initialyCoordinate = yCoordinate
        self.initialPadding = padding

        super().__init__(variableChart)

        self.variableChart : VariableLineChart = self.variableChart
        self.lockedPoints : set[int] = set()
        
    
    def _setConstraints(self):
        """Loads constraints of the chart to the solver"""
        constraints : set[Constraint] = set(self.variableChart.GetAllConstraints())
        for constraint in constraints:
            self.solver.addConstraint(constraint)
    
    @inheritdocstring(ChartSolver._addEditVariables)
    def _addEditVariables(self):
        chart : VariableLineChart = self.variableChart
        self.solver.addEditVariable(self.variableChart.width, "strong")
        self.solver.addEditVariable(self.variableChart.origin.X, "strong")
        self.solver.addEditVariable(self.variableChart.origin.Y, "strong")
        self.solver.addEditVariable(self.variableChart.yAxisHeight, "strong")
        self.solver.addEditVariable(self.variableChart.padding, "strong")
        for line in chart.lines:
            self.solver.addEditVariable(line.leftHeight, "strong")
            self.solver.addEditVariable(line.rightHeight, "medium")
    
    @inheritdocstring(ChartSolver._initialSuggest)
    def _initialSuggest(self):
        chart : VariableLineChart = self.variableChart
        self.solver.suggestValue(self.variableChart.yAxisHeight, max(self.initialValues)+10)
        self.solver.suggestValue(chart.width, self.initialWidth)
        self.solver.suggestValue(chart.origin.X, self.initialxCoordinate)
        self.solver.suggestValue(chart.origin.Y,self.initialyCoordinate)
        self.solver.suggestValue(chart.padding,self.initialPadding)
        values = self.initialValues + ([] if not chart.lines[-1].ignoreRight else [0])
        
        valuePairs = list(pairwise(self.initialValues))
        for i in range(len(chart.lines)):
            line = chart.lines[i]
            values = valuePairs[i]
            self.solver.suggestValue(line.leftHeight, values[0])
            self.solver.suggestValue(line.rightHeight,values[1])
    
    def Feed(self, otherSolver: "LineChartSolver"):
        """Loads all solutions into another line chart solver. It is expected that the other solver operates above the same data.

        Args:
            otherSolver (LineChartSolver): Solver to which the solutions are supposed to be loaded.
        """
        origin = self.GetOrigin()
        otherSolver.ChangeOrigin(origin.X, origin.Y)
        otherSolver.ChangeAxisHeight(self.GetAxisHeight())
        otherSolver.ChangeWidth(self.GetWidth())
        otherSolver.ChangePadding(self.GetPadding())
        otherSolver.Solve()

    def GetLineData(self):
        """Retrieves the line data for the chart.

        Returns:
            list: List of all line segments with current values.
        """
        return [line.Value() for line in self.variableChart.lines]

    def GetPoints(self):
        """Retrieves all data points in the chart.

        Returns:
            list: List of all data points (endpoints of line segments).
        """
        lines = self.GetLineData()
        if len(lines) == 0:
            return []

        rightEnds = []
        for line in lines:
            if not line.ignoreRight:
                rightEnds.append(line.rightEnd)

        return [lines[0].leftEnd] + rightEnds
    
    def SwitchPointLock(self, pointIndex: int):
        """Locks or unlocks a data point from being edited.

        Args:
            pointIndex (int): Index of the point

        Returns:
            bool: True if the method call has locked the point, False if unlocked.
        """
        if pointIndex in self.lockedPoints:
            self.lockedPoints.remove(pointIndex)
            return False
        else:
            self.lockedPoints.add(pointIndex)
            return True
    
    def ChangeHeight(self, pointIndex: int, height: float):
        """Changes the height (Y value) of a data point.

        Args:
            pointIndex (int): Index of the point to modify
            height (float): New Y value for the point
        """
        if pointIndex in self.lockedPoints:
            return
        self.solver.suggestValue(self.variableChart.GetHeightList()[pointIndex], height)
        self.Solve()
    
    def ChangePadding(self, newPadding: float):
        """Changes the left padding of the chart.

        Args:
            newPadding (float): New padding value
        """
        self.solver.suggestValue(self.variableChart.padding,newPadding)
        self.Solve()
    
    def GetPadding(self):
        """Retrieves the left padding value.

        Returns:
            float: Current padding value
        """
        return self.variableChart.padding.value()
    
    def ChangeName(self, pointIndex : int, name : str):
        """Changes the name of a data point.

        Args:
            pointIndex (int): Index of the point to rename
            name (str): New name for the point
        """
        self.variableChart.ChangeName(pointIndex, name)

    def ChangeWidthX(self, pointIndex: int, newX: float):
        """Change global width of lines by stretching right side of a given line (in other words: set width of lines from cursor position).

        Args:
            pointIndex (int): Index of the point
            newX (float): Cursor X position
        """
        if pointIndex == 0:
            return
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
    
    def ChangePaddingX(self, newX: float):
        """Change padding of the chart by displacing left side of the first line (in other words: set padding of chart from cursor position).

        Args:
            newX (float): Cursor X position
        """
        firstLine = self.variableChart.lines[0]
        var = firstLine.leftEnd.X
        strength = 1e+8
        if (not self.solver.hasEditVariable(var)):
                self.solver.addEditVariable(var,strength)
        self.solver.suggestValue(var, newX)
        originLock = self.switchConstraintLock(self.variableChart.origin.X)
        #widthLock = self.switchConstraintLock(self.variableChart.width)
        self.Solve()
        self.solver.removeEditVariable(var)
        self.solver.suggestValue(self.variableChart.padding,self.variableChart.padding.value())
        #self.switchConstraintLock(self.variableChart.width,widthLock)
        self.switchConstraintLock(self.variableChart.origin.X,originLock)

    
    def AddPoint(self, value: float, name: str):
        """Appends a new data point to the chart.

        Args:
            value (float): Y value (height) of the new point
            name (str): Name of the new point
        """
                              #TODO nebude fungovat pro prazdny
        lastLine = self.variableChart.lines[-1]
        if lastLine.ignoreRight:
            lastLine.SwitchIgnoreRight()
            pointIndex = len(self.GetPoints())-1
            self.ChangeName(pointIndex,name)
            self.ChangeHeight(pointIndex,value)
        else:
            lastPointValue = lastLine.rightHeight.value()
            newLine, newConstraints = self.variableChart.AddPoint(name)
            self.solver.addEditVariable(newLine.leftHeight, "strong")
            self.solver.addEditVariable(newLine.rightHeight, "medium")
            for constr in newConstraints:
                self.solver.addConstraint(constr)
            self.solver.suggestValue(newLine.leftHeight,lastPointValue)
            self.solver.suggestValue(newLine.rightHeight,value)
            self.Solve()
