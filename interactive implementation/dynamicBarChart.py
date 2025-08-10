import kiwisolver
from kiwisolver import Variable, Constraint, Solver
import random
from typing import Union
import warnings
import functools
import tkinter as tk
from tkinter import simpledialog
import numpy as np
from PIL import Image


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
    def GetHeight(self):
        return self.rightTop.Y-self.leftBottom.Y

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
        constraints = [constraint for constraint in self] + [(self.height >= 0)|"required",(self.leftBottom.X >= 0) | "required", (self.leftBottom.Y >= 0) | "required", (self.rightTop.X >= 0) | "required", (self.rightTop.Y >= 0) | "required"]
        #print(constraints)
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

        self.origin: VariablePoint2D = VariablePoint2D("origin")

        self.originXCoordinateConstraint : Constraint = (self.origin.X == xCoordinate) | "strong"
        self.originYCoordinateConstraint : Constraint = (self.origin.Y == yCoordinate) | "strong"
        self.leftRectangleXCoordinateConstraint : Constraint = (self.rectangles[0].leftBottom.X == self.origin.X + self.spacing) | "required"
        self.leftRectangleYCoordinateConstraint : Constraint = (self.rectangles[0].leftBottom.Y == self.origin.Y) | "required"
        #self.rectangles[0].FixBottomLeftCorner(xCoordinate, yCoordinate)
    
    def ChangeWidth(self, width: int):
        self.widthValueConstraint = ((self.width == width) | "strong")
    
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
        return result + [(self.width >= 10) | "required"] \
                    + [self.rectangles[i].leftBottom.Y == self.rectangles[i-1].leftBottom.Y for i in range(1,len(self.rectangles))] \
                    + [self.widthValueConstraint, self.spacingValueConstraint] \
                    + [self.originXCoordinateConstraint,self.originYCoordinateConstraint,self.leftRectangleXCoordinateConstraint,self.leftRectangleYCoordinateConstraint]
    
class BarChartSolver:
    def __init__(self, width: int, initialHeights: list[int], spacing: int, xCoordinate: int = 0, yCoordinate: int = 0):
        
        self.solver = Solver()
        self.variableBarChart = VariableBarChart(width, initialHeights, spacing, xCoordinate, yCoordinate)
        self.rectangleData = None

        barChartConstraints = set(self.variableBarChart.GetAllConstraints())
        
        
        for constraint in barChartConstraints:
            self.solver.addConstraint(constraint)

        self.solver.addEditVariable(self.variableBarChart.width, 1e+07)
        self.solver.addEditVariable(self.variableBarChart.spacing, 1e+07)


        for rec in self.variableBarChart.rectangles:
            self.solver.addEditVariable(rec.height, "strong")
        
        self.solver.addEditVariable(self.variableBarChart.origin.X, "strong")
        self.solver.addEditVariable(self.variableBarChart.origin.Y, "strong")
        
        self.Solve()
    
    def GetRectanglePositions(self):
        return self.rectangleData

    def GetSpacing(self):
        return self.variableBarChart.spacing.value()
    
    def GetWidth(self):
        return self.variableBarChart.width.value()
    
    def GetOrigin(self):
        return ValuePoint2D(self.variableBarChart.origin.X.value(),self.variableBarChart.origin.Y.value())
    
    def ChangeRightX(self, rectangleIndex: int, newX: int):
        self.solver.suggestValue(self.variableBarChart.rectangles[rectangleIndex].rightTop.X, newX)
        self.solver.updateVariables()
        self.rectangleData = self.variableBarChart.Value()
    
    def ChangeWidth(self, newWidth: int):
        self.solver.suggestValue(self.variableBarChart.width, newWidth)
        self.solver.updateVariables()
        self.rectangleData = self.variableBarChart.Value()
    
    def ChangeHeight(self, rectangleIndex: int, newHeight: int):
        self.solver.suggestValue(self.variableBarChart.rectangles[rectangleIndex].height, newHeight)
        self.solver.updateVariables()
        self.rectangleData = self.variableBarChart.Value()
    
    def ChangeSpacing(self, newSpacing: int):
        self.solver.suggestValue(self.variableBarChart.spacing, newSpacing)
        self.solver.updateVariables()
        self.rectangleData = self.variableBarChart.Value()
    
    def ChangeOrigin(self, newX: int, newY: int):
        self.solver.suggestValue(self.variableBarChart.origin.X, newX)
        self.solver.suggestValue(self.variableBarChart.origin.Y, newY)
        self.solver.updateVariables()
        self.rectangleData = self.variableBarChart.Value()
    
    def Solve(self):
        self.solver.updateVariables()
        self.rectangleData = self.variableBarChart.Value()


class BarChartCanvas:
    def __init__(self, initialValues: list[float], initialWidth: int, initialSpacing: int, canvasWidth: int, canvasHeight: int, graphTitle: str = "",xCoordinate: int = 50, yCoordinate: int = 30):
        
        self.title = graphTitle
        # rescaling of input data
        self.realValues = initialValues
        self.rescaleFactor = 1

        if not (canvasHeight*0.3 <= max(self.realValues) <= canvasHeight*0.8):
            self.rescaleFactor = canvasHeight*0.8/max(self.realValues)


        initialHeights = [int(self.rescaleFactor*value) for value in self.realValues] # rescaled heights

        self.xCoordinate = xCoordinate
      
        # solver initialisation
        self.canvasHeight = canvasHeight
        self.canvasWidth = canvasWidth
        self.barChart = BarChartSolver(initialWidth, initialHeights, initialSpacing, xCoordinate, yCoordinate)
        
        # UI features initialisation
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.canvas = tk.Canvas(self.frame, width=canvasWidth, height=canvasHeight, bg="white")
        self.canvas.pack()

        self.dataWindow = tk.Text(self.frame, height=5, width=40)
        self.dataWindow.pack()

        self.saveButton = tk.Button(self.frame, text="Save", command=self.on_saveButton_click)
        self.saveButton.pack(pady=5)
        
        # Fields for event register
        self.dragEdge = None
        self.dragStart = ValuePoint2D(0,0)
        self.dragIndex = None
        self.originalLeftX = None
        self.originalSpacing = None
        self.rightEdgeCursorOffset = None
        self.originalHeight = None

        self._drawPlot()
        self._writeValues()

        # binding methods to mouse events
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Motion>", self.check_cursor)
        self.root.mainloop()
    def _report(self):
        print(f"dragEdge: {self.dragEdge}, dragStart: {self.dragStart}, dragIndex: {self.dragIndex}, originalLeftX: {self.originalLeftX}, originalSpacing: {self.originalSpacing}, rightEdgeCursorOffset: {self.rightEdgeCursorOffset}")
    

    @staticmethod
    def _ceilToNearestTen(number: int):
        return ((number // 10) + 1) * 10

    def _drawAxes(self, maximumValue: int, xAxisHeight: int, leftCornerXAxis: int):
        """
        Draws axes on the canvas
        """
        def _divideIntervalFromZeroTo(number: int, parts: int):
            step = number // (parts - 1) 
            return [i * step for i in range(parts)]
        
        xAxisY = self.canvasHeight - xAxisHeight


        topNumber = self._ceilToNearestTen(maximumValue) 

        marks = _divideIntervalFromZeroTo(topNumber, 5)
        origin = self.barChart.GetOrigin()
      
        self.canvas.create_line(origin.X, self.canvasHeight - origin.Y, leftCornerXAxis + 10, self.canvasHeight - origin.Y, fill="black", width=1)
        self.canvas.create_line(origin.X, self.canvasHeight - origin.Y, origin.X, self.canvasHeight - origin.Y - topNumber, fill="black", width=1)

        for mark in marks:
            y = xAxisY - mark
            self.canvas.create_line(35, y, 40, y, fill="black")  
            self.canvas.create_text(30, y, text=f"{(mark/self.rescaleFactor):.2g}", anchor="e") 
    
    def _drawRectangles(self):
        """
        Draws rectangles on the plot and writes their names under them.
        """
        rectangles = self.barChart.GetRectanglePositions()
        for rec in rectangles: 
            x1 = rec.leftBottom.X
            y1 = self.canvasHeight - rec.leftBottom.Y
            
            x2 = rec.rightTop.X
            y2 = self.canvasHeight - rec.rightTop.Y

            self.canvas.create_rectangle(x1,y2,x2,y1, fill=rec.color, outline="black")
            self.canvas.create_text((x1+x2)/2,y1 + 10, text=rec.name)

    def _writePlotTitle(self):
        self.canvas.create_text(self.canvasWidth / 2, 20,text=self.title,font=("Arial", 16, "bold"))


    def _drawPlot(self):
        """
        Draws rectangles and axes on the plot
        """
        self.canvas.delete("all")
        self._writePlotTitle()
        rectangles = self.barChart.GetRectanglePositions()
        for rec in rectangles:
            print(rec)

        self._drawRectangles()
        
        highestRectangleHeight = max([rec.rightTop.Y for rec in self.barChart.GetRectanglePositions()])
        self._drawAxes(highestRectangleHeight, rectangles[0].leftBottom.Y, rectangles[-1].rightTop.X)    

    def _writeValues(self):
        """
        Displays all data for the user and highlights which data is being edited
        """
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        valueEdited = self.dragEdge == "top"
        rectangles = self.barChart.GetRectanglePositions()

        for i in range(len(rectangles)-1, -1, -1):
            rec = rectangles[i]
            if valueEdited and i == self.dragIndex:
                self.dataWindow.insert("1.0",f"{rec.name} = {(rec.GetHeight()/self.rescaleFactor):.4g}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"{rec.name} = {(rec.GetHeight()/self.rescaleFactor):.4g}\n")
        self.dataWindow.config(state="disabled")

    
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
        return self._isNear(event.x, rectangle.rightTop.X,3) and rightTopYNormalized <= event.y <= leftBottomYNormalized
    
    def _isNearLeftEdge(self, event, rectangle: ValueRectangle):
        """
        Returns True, if for given rectangle the event happened near to the left edge of the rectangle.
        For more information, see _isNear method.
        """
        leftBottomYNormalized = self.canvasHeight - rectangle.leftBottom.Y
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        return self._isNear(event.x, rectangle.leftBottom.X, 10) and rightTopYNormalized <= event.y <= leftBottomYNormalized


    def _isNearTopEdge(self, event, rectangle: ValueRectangle):
        """
        Returns True, if for given rectangle the event happened near to the top edge of the rectangle.
        For more information, see _isNear method.
        """
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        return self._isNear(event.y, rightTopYNormalized) and rectangle.leftBottom.X <= event.x <= rectangle.rightTop.X

    def _clickedOnRightEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle):
        """
        Registers that the user clicked on a right edge of some rectangle
        """
        self.dragEdge = 'right'
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = rectangleIndex
        
        self.originalCoordinates = rectangle.rightTop
        self.rightEdgeCursorOffset = event.x - rectangle.rightTop.X
        self.originalLeftX = rectangle.leftBottom.X
    
    def _clickedOnLeftEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle):
        """
        Registers that the user clicked on a left edge of some rectangle
        """
        self.dragEdge = "left"
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = rectangleIndex
        
        self.originalLeftX = rectangle.leftBottom.X
        self.originalSpacing = self.barChart.GetSpacing()
    
    def _clickedOnTopEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle):
        """
        Registers that the user clicked on a top edge of some rectangle
        """
        self.dragEdge = "top"
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = rectangleIndex
        self.originalHeight = rectangle.rightTop.Y - rectangle.leftBottom.Y
    
    def on_mouse_down(self, event):
        """
        This method is triggered when the user clicks on canvas.
        It identifies what the program should do next and registers the event
        """
        for recIndex, rec in enumerate(self.barChart.GetRectanglePositions()): 
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
        """
        If method on_mouse_down registered an event near to some edge of some rectangle, then this method mekes appropriate changes toi the graph if the user has moved with mouse.
        """
        if self.dragEdge is None:
            return
        
        rectangles = self.barChart.GetRectanglePositions()

        if self.dragEdge == "right":
            newWidth = (event.x - self.barChart.GetSpacing()*(self.dragIndex+1)-self.xCoordinate)//(self.dragIndex+1) 
            if newWidth > 10:
                self.barChart.ChangeWidth(newWidth)

        elif self.dragEdge == "top":
            dy = self.dragStart.Y - event.y  # rozdíl v y směru (pozor na orientaci)
            newHeight = self.originalHeight + dy
            if newHeight > 0:
                self.barChart.ChangeHeight(self.dragIndex, newHeight)
            print([rec.GetHeight()/self.rescaleFactor for rec in rectangles])
            self._writeValues()
        elif self.dragEdge == "left" and self.dragIndex > 0:
            newSpacing = (event.x - (self.dragIndex)*self.barChart.GetWidth() - self.xCoordinate)//(self.dragIndex+1)
            if newSpacing > 0:
                self.barChart.ChangeSpacing(newSpacing)
        
        self._drawPlot()

    def on_mouse_up(self, event):
        """
        Unregisteres the click event
        """
        self.dragEdge = None
        self.dragStart = ValuePoint2D(0,0)
        self.dragIndex = None
        self.originalRightCoordinates = None
        self.originalLeftX = None
        self.originalSpacing = None
    
    def check_cursor(self,event):
        """
        Changes cursor according to its position.
        """
        for idx, rec in enumerate(self.barChart.GetRectanglePositions()):
            if idx > 0 and self._isNearLeftEdge(event, rec):
                self.canvas.config(cursor="hand2")
                return
            elif self._isNearRightEdge(event, rec):
                self.canvas.config(cursor="sb_h_double_arrow")
                return
            elif self._isNearTopEdge(event, rec):
                self.canvas.config(cursor="sb_v_double_arrow")
                return
        self.canvas.config(cursor="arrow")
    def on_saveButton_click(self):
        print("Click")

    

if __name__ == "__main__":
    initial_heights = [50,60,70]
    initial_width = 20
    initial_spacing = 10
    canvas_width = 1000
    canvas_height = 500
    print("alive 0")

    BarChartCanvas(initial_heights, initial_width, initial_spacing, canvas_width, canvas_height, "Test values")



