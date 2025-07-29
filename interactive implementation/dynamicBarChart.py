import kiwisolver
from kiwisolver import Variable, Constraint, Solver
import random
from typing import Union
import warnings
import functools
import tkinter as tk
import numpy as np


class ValuePoint2D:
    """
    Holds information about 2D points.
    """
    def __init__(self, X: int, Y: int):
        self.X = X
        self.Y = Y
    def __str__(self):
        return f"({self.X}, {self.Y})"

class ValueRectangle:
    """
    Holds information about given rectangle
    """
    def __init__(self, leftBottomCorner: ValuePoint2D, rightTopCorner: ValuePoint2D, color: Union[str, int] = "blue", name: str = ""):
        self.leftBottom = leftBottomCorner
        self.rightTop = rightTopCorner
        self.color = color
        self.name = name
    
    def __str__(self):
        return f"{self.name} LB: ({self.leftBottom.X}, {self.leftBottom.Y}), RT: ({self.rightTop.X}, {self.rightTop.Y})"

class VariablePoint2D:
  """
  Used for constraint declaration
  """
  def __init__(self, name: str = ""):
        self.X = Variable("X"+f"_{name}")
        self.Y = Variable("Y"+f"_{name}")
  def Value(self):
        return ValuePoint2D(self.X.value(), self.Y.value())


class VariableRectangle:
    """
    Creates constraints for a given rectangle.
    Width is maintained globaly, height localy
    """
    def __init__(self, width: Variable, height: int, name: str, color = "blue"):
        self.height = Variable(f"{name}_height")
        self.width = width
        self.name = name
        self.color = color
        self.leftBottom = VariablePoint2D(name)
        self.rightTop = VariablePoint2D(name)

        self.heightConstraint : Constraint = None
        self.horizontalPositionConstraint : Constraint = None
        self.verticalPositionConstraint : Constraint = None

        self.bottomLeftXPositionConstraint : Constraint = None
        self.bottomLeftYPositionConstraint : Constraint = None

        self.spacingConstraint : Constraint = None

        self._createHeightConstraint(height)
        self._createCornerConstraints()

    def __iter__(self):
        constraints = [self.heightConstraint]
        if self.spacingConstraint is not None:
            constraints.append(self.spacingConstraint)
        if self.bottomLeftXPositionConstraint is not None:
            constraints.append(self.bottomLeftXPositionConstraint)
        if self.bottomLeftYPositionConstraint is not None:
            constraints.append(self.bottomLeftYPositionConstraint)
        constraints.append(self.horizontalPositionConstraint)
        constraints.append(self.verticalPositionConstraint)
        return iter(constraints)
    
    def _createHeightConstraint(self, height: int):
        self.heightConstraint = ((self.height == height) | "strong")

    def _createCornerConstraints(self):
        self.horizontalPositionConstraint = ((self.leftBottom.X + self.width == self.rightTop.X) | "strong")
        self.verticalPositionConstraint = ((self.leftBottom.Y + self.height == self.rightTop.Y) | "weak")

    def FixBottomLeftCorner(self, X: int, Y: int):
        self.bottomLeftXPositionConstraint = ((self.leftBottom.X == X) | "weak")
        self.bottomLeftYPositionConstraint = ((self.leftBottom.Y == Y) | "weak")
    
    def ChangeHeight(self, height: int):
        self.heightConstraint = (((self.height == height) | "strong"))
    
    def SetSpacingConstraint(self, spacingConstraint : Constraint):
        self.spacingConstraint = spacingConstraint
    
    def GetAllConstraints(self):
        constraints = [constraint for constraint in self] + [(self.leftBottom.X >= 0) | "required", (self.leftBottom.Y >= 0) | "required", (self.rightTop.X >= 0) | "required", (self.rightTop.Y >= 0) | "required"]
        print(constraints)
        return constraints
    
    def Value(self):
        return ValueRectangle(self.leftBottom.Value(), self.rightTop.Value(), self.color, self.name)

class VariableBarChart:
    def __init__(self, width: int, initialHeights: list[int], spacing: int, xCoordinate: int = 0, yCoordinate: int = 0):
        self.width = Variable("global_width")

        self.spacing = Variable("global_spacing")
        self.spacingValueConstraint : Constraint = None
        self.ChangeSpacing(spacing)
        
        self.widthValueConstraint : Constraint = None
        self.ChangeWidth(width)

        self.rectangles = [VariableRectangle(self.width, initialHeights[i], f"rectangle_no_{i}") for i in range(len(initialHeights))]
        self._createRectangleSpacingConstraints()

        self.rectangles[0].FixBottomLeftCorner(xCoordinate, yCoordinate)
    
    def ChangeWidth(self, width: int):
        self.widthValueConstraint = ((self.width == width) | "strong")
        print("!!!!!!!!!!!!!")
        print(self.widthValueConstraint)
    
    def ChangeSpacing(self, spacing: int):
        self.spacingValueConstraint = ((self.spacing == spacing) | "strong")
    
    def _createRectangleSpacingConstraints(self):
        for index, rec in enumerate(self.rectangles):
            if index != 0:
                rec.SetSpacingConstraint((self.rectangles[index-1].rightTop.X + self.spacing == rec.leftBottom.X) | "strong")
    
    def ChangeHeight(self, rectangleIndex: int, newHeight: int):
        self.rectangles[rectangleIndex].ChangeHeight(newHeight)
    
    
    def Value(self):
        return [rec.Value() for rec in self.rectangles]

    def GetAllConstraints(self):
        result = []
        for rec in self.rectangles:
            result.extend(rec.GetAllConstraints())
        return result + [(self.width >= 0) | "required"] \
                    + [self.rectangles[i].leftBottom.Y == self.rectangles[i-1].leftBottom.Y for i in range(1,len(self.rectangles))] \
                    + [self.widthValueConstraint, self.spacingValueConstraint]
    
class BarChartSolver:
    def __init__(self, width: int, initialHeights: list[int], spacing: int, xCoordinate: int = 0, yCoordinate: int = 0):
        self.solver = Solver()
        self.variableBarChart = VariableBarChart(width, initialHeights, spacing, xCoordinate, yCoordinate)
        self.rectangleData = None

        for constraint in self.variableBarChart.GetAllConstraints():
            self.solver.addConstraint(constraint)
        
        self.solver.addEditVariable(self.variableBarChart.width, "strong")
        self.solver.addEditVariable(self.variableBarChart.spacing, "strong")

        for rec in self.variableBarChart.rectangles:
            self.solver.addEditVariable(rec.height, "strong")
    
    def GetRectanglePositions(self):
        if self.rectangleData == None:
            self.solver.updateVariables()
            self.rectangleData = self.variableBarChart.Value()
        return self.rectangleData
    
    def ChangeWidth(self, newWidth: int):
        self.rectangleData = None
        self.solver.suggestValue(self.variableBarChart.width, newWidth)
    
    def ChangeHeight(self, rectangleIndex: int, newHeight: int):
        self.rectangleData = None
        self.solver.suggestValue(self.variableBarChart.rectangles[rectangleIndex].height, newHeight)
    
    def ChangeSpacing(self, newSpacing: int):
        self.rectangleData = None
        self.solver.suggestValue(self.variableBarChart.spacing, newSpacing)


heights = [10,20,30]
barChartSolver = BarChartSolver(10,heights,20, 5,5)

a = barChartSolver.GetRectanglePositions()
print(barChartSolver.variableBarChart.width.value())
for rec in a:
    print(rec)
barChartSolver.ChangeWidth(1000)
