from .chartsolver import ChartSolver
from kiwisolver import Constraint, Solver
from kiwiplots.variablechart import VariableLineChart, VariableChart
from typing import Union
from kiwiplots.plotelement import ValueRectangle, VariableRectangle
from kiwiplots.utils import *

class LineChartSolver(ChartSolver):
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
        constraints : set[Constraint] = set(self.variableChart.GetAllConstraints())
        for constraint in constraints:
            self.solver.addConstraint(constraint)
    
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
    
    def _initialSuggest(self):
        chart : VariableLineChart = self.variableChart
        self.solver.suggestValue(self.variableChart.yAxisHeight, max(self.initialValues)+10)
        self.solver.suggestValue(chart.width, self.initialWidth)
        self.solver.suggestValue(chart.origin.X, self.initialxCoordinate)
        self.solver.suggestValue(chart.origin.Y,self.initialyCoordinate)
        self.solver.suggestValue(chart.padding,self.initialPadding)
        valuePairs = list(pairwise(self.initialValues))
        for i in range(len(chart.lines)):
            line = chart.lines[i]
            values = valuePairs[i]
            self.solver.suggestValue(line.leftHeight, values[0])
            self.solver.suggestValue(line.rightHeight,values[1])
    
    def Feed(self, otherSolver: "LineChartSolver"):
        origin = self.GetOrigin()
        otherSolver.ChangeOrigin(origin.X, origin.Y)
        otherSolver.ChangeAxisHeight(self.GetAxisHeight())
        otherSolver.ChangeWidth(self.GetWidth())
        otherSolver.ChangePadding(self.GetPadding())
        otherSolver.Solve()

    def GetLineData(self):
        return [line.Value() for line in self.variableChart.lines]

    def GetPoints(self):
        lines = self.GetLineData()
        if len(lines) == 0:
            return []
        return [lines[0].leftEnd] + [line.rightEnd for line in lines]
    
    def SwitchPointLock(self, pointIndex: int):
        if pointIndex in self.lockedPoints:
            self.lockedPoints.remove(pointIndex)
            return False
        else:
            self.lockedPoints.add(pointIndex)
            return True
    
    def ChangeHeight(self, pointIndex: int, height: float):
        if pointIndex in self.lockedPoints:
            return
        self.solver.suggestValue(self.variableChart.GetHeightList()[pointIndex], height)
        self.Solve()
    
    def ChangePadding(self, newPadding: float):
        self.solver.suggestValue(self.variableChart.padding,newPadding)
        self.Solve()
    
    def GetPadding(self):
        return self.variableChart.padding.value()

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
        self.Solve()
