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


class BarChartCanvas:
    def __init__(self, initialHeights: list[int], initialWidth: int, initialSpacing: int, canvasWidth: int, canvasHeight: int):
        self.canvasHeight = canvasHeight
        self.barChart = BarChartSolver(initialWidth, initialHeights, initialSpacing)
        
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=canvasWidth, height=canvasHeight, bg="white")
        self.canvas.pack()

        self.dragEdge = None
        self.dragStart = ValuePoint2D(0,0)
        self.dragIndex = None
        self.originalRightCoordinates = None
        self.originalLeftX = None


        self._drawRectangles()

        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        #self.check_cursor()
        self.root.mainloop()
    
    def _drawRectangles(self):
        """
        Draws all rectangles on canvas.
        """
        self.canvas.delete("all")
        for rec in self.barChart.GetRectanglePositions(): # constraint solving happens on this line (potentialy)
            x1 = rec.leftBottom.X
            y1 = self.canvasHeight - rec.leftBottom.Y
            
            x2 = rec.rightTop.X
            y2 = self.canvasHeight - rec.rightTop.Y

            self.canvas.create_rectangle(x1,y2,x2,y1, fill=rec.color, outline="black")
    
    @staticmethod
    def _isNear(val1, val2, tolerance=5):
        """
        Returns True, if two values are near to each other with given tolerance
        """
        return abs(val1 - val2) < tolerance
    
    def _isNearRightEdge(self, event, rectangle: ValueRectangle):
        """
        Returns True, if for given rectangle the event happened near to the right edge of the rectangle.
        For more information, see _isNear method.
        """
        leftBottomYNormalized = self.canvasHeight - rectangle.leftBottom.Y # Canvas coordinates are flipped, "Normalized" values are real y values on the canvas.
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        return self._isNear(event.x, rectangle.rightTop.X) and rightTopYNormalized <= event.y <= leftBottomYNormalized
    
    def _isNearLeftEdge(self, event, rectangle: ValueRectangle):
        """
        Returns True, if for given rectangle the event happened near to the left edge of the rectangle.
        For more information, see _isNear method.
        """
        leftBottomYNormalized = self.canvasHeight - rectangle.leftBottom.Y
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        return self._isNear(event.x, rectangle.leftBottom.X) and rightTopYNormalized <= event.y <= leftBottomYNormalized


    def _isNearTopEdge(self, event, rectangle: ValueRectangle):
        """
        Returns True, if for given rectangle the event happened near to the top edge of the rectangle.
        For more information, see _isNear method.
        """
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        return self._isNear(event.y, rightTopYNormalized) and rectangle.leftBottom.X <= event.x <= rectangle.rightTop.X

    def _clickedOnRightEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle):
        self.dragEdge = 'right'
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = rectangleIndex
        
        self.originalCoordinates = rectangle.rightTop
        self.originalLeftX = rectangle.leftBottom.X
    
    def _clickedOnLeftEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle):
        self.dragEdge = "left"
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = rectangleIndex
        
        self.originalLeftX = rectangle.leftBottom.X
        #zde zaznamenat soucasny spacing?
    
    def _clickedOnTopEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle):
        self.dragEdge = "top"
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = rectangleIndex
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        self.originalCoordinates = ValuePoint2D(rectangle.rightTop.X, rightTopYNormalized)
    
    def on_mouse_down(self, event):
        for recIndex, rec in enumerate(self.barChart.GetRectanglePositions()): # constraint solving happens on this line (potentialy)
            if self._isNearLeftEdge(event, rec) and recIndex > 0: # change in spacing
                self._clickedOnLeftEdge(event, recIndex, rec)
                return
            elif self._isNearRightEdge(event, rec): # change in width
                self._clickedOnRightEdge(event, recIndex, rec)
                return
            elif self._isNearTopEdge(event, rec): # change in height
                self._clickedOnTopEdge(event, recIndex, rec)
                return
            else:
                continue
    
    def on_mouse_move(self, event):
        if self.dragEdge is None:
            return
        
        rectangles = self.barChart.GetRectanglePositions() # constraint solving happens on this line (potentialy)

        if self.dragEdge == "right":
            newWidth = abs(event.x - self.originalLeftX)
            if newWidth > 10:
                self.barChart.ChangeWidth(newWidth)
        elif self.dragEdge == "top":
            rec = rectangles[self.dragIndex]
            newRightTopYNormalized = self.canvasHeight - (self.originalCoordinates.Y + event.y - self.dragStart.Y)
            newHeight = newRightTopYNormalized - rec.leftBottom.Y
            if newHeight > 10:
                self.barChart.ChangeHeight(self.dragIndex, newHeight)
        elif self.dragEdge == "left" and self.dragIndex > 0:
            oldSpacing = rectangles[self.dragIndex].leftBottom.X - rectangles[self.dragIndex-1].rightTop.X
            dx = event.x - self.dragStart.X
            newSpacing = oldSpacing + dx
            if newSpacing > 0:
                self.barChart.ChangeSpacing(newSpacing)
        
        self._drawRectangles()

    def on_mouse_up(self, event):
        self.dragEdge = None
        self.dragStart = ValuePoint2D(0,0)
        self.dragIndex = None
        self.originalRightCoordinates = None
        self.originalLeftX = None

    

if __name__ == "__main__":
    #initial_heights = list(map(int, np.random.poisson(50, 200)))
    initial_heights = [60, 20 ,70] 
    initial_width = 20
    initial_spacing = 10
    canvas_width = 1000
    canvas_height = 200

    BarChartCanvas(initial_heights, initial_width, initial_spacing, canvas_width, canvas_height)



