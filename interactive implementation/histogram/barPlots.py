import kiwisolver
from kiwisolver import Variable, Constraint, Solver
import random
from typing import Union
import warnings
import functools
import tkinter as tk
from tkinter import simpledialog
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tkinter import colorchooser
import os

class ValuePoint2D:
    """
    Holds information about 2D points.
    """
    def __init__(self, X: int, Y: int, name: str = "", secondaryName: str = ""):
        self.X = X
        self.Y = Y
        self.name = name
        self.secondaryName = secondaryName
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
  def __init__(self, name: str = "", secondaryName = ""):
        self.X = Variable(f"{name}.X")
        self.Y = Variable(f"{name}.Y")
        self.name = name
        self.secondaryName = secondaryName
  def Value(self):
        return ValuePoint2D(self.X.value(), self.Y.value(), self.name, self.secondaryName)


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
        self.leftBottom = VariablePoint2D(name+".leftBottom")
        self.rightTop = VariablePoint2D(name+".rightTop")

        self.heightConstraint : Constraint = (self.height == float(height)) | "strong"
        self.horizontalPositionConstraint : Constraint = ((self.leftBottom.X + self.width == self.rightTop.X) | "required")
        self.verticalPositionConstraint : Constraint = ((self.leftBottom.Y + self.height == self.rightTop.Y) | "required")

        self.bottomLeftXPositionConstraint : Constraint = None
        self.bottomLeftYPositionConstraint : Constraint = None

        self.spacingConstraint : Constraint = None

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
    
   
    def FixBottomLeftCorner(self, X: int, Y: int):
        self.bottomLeftXPositionConstraint = ((self.leftBottom.X == X) | "weak")
        self.bottomLeftYPositionConstraint = ((self.leftBottom.Y == Y) | "weak")
    
    def SetSpacingConstraint(self, spacingConstraint : Constraint):
        self.spacingConstraint = spacingConstraint
    
    def GetAllConstraints(self):
        constraints = [constraint for constraint in self] + [(self.height >= 0)|"required",(self.leftBottom.X >= 0) | "required", (self.leftBottom.Y >= 0) | "required", (self.rightTop.X >= 0) | "required", (self.rightTop.Y >= 0) | "required"]
        return constraints
    
    def Value(self):
        return ValueRectangle(self.leftBottom.Value(), self.rightTop.Value(), self.color, self.name)

class VariableRectangleGroup:
    def __init__(self, rectangleWidth: Variable, heights: list[int], innerSpacing: Variable, groupName: str = "", color: str = "blue"):
        self.rectangles = [VariableRectangle(rectangleWidth, height, groupName+f"_{i}", color) for i,height in enumerate(heights)]
        self.innerSpacing = innerSpacing

        self.groupName = groupName

        for i in range(1,len(self.rectangles)):
            self.rectangles[i].SetSpacingConstraint((self.rectangles[i-1].rightTop.X + self.innerSpacing == self.rectangles[i].leftBottom.X) | "required")

        self.leftMostX : Variable = self.rectangles[0].leftBottom.X
        self.rightMostX : Variable = self.rectangles[-1].rightTop.X
        self.bottomY : Variable = self.rectangles[0].leftBottom.Y

        self.spacingConstraint : Constraint = None
    
    def __iter__(self):
        return iter(self.rectangles)

    def SetSpacingConstraint(self, constraint: Constraint):
        self.spacingConstraint = constraint
    
    def GetAllConstraints(self):
        result = []
        for rec in self.rectangles:
            constraints = rec.GetAllConstraints()
            result += constraints
        return result \
                    + [self.rectangles[i-1].leftBottom.Y == self.rectangles[i].leftBottom.Y for i in range(1,len(self.rectangles))] \
                    + ([] if self.spacingConstraint == None else [self.spacingConstraint])
    
    def Value(self):
        return [rec.Value() for rec in self.rectangles]
    
    def Max(self):
        return max([rec.rightTop.Y - rec.leftBottom.Y for rec in self.Value()])

    def NumberOfRectangles(self):
        return len(self.rectangles)
    
        

class VariableBarChart:
    def __init__(self, width: int, initialHeights: Union[list[int], list[list[int]]], spacing: int, innerSpacing: int, xCoordinate: int = 0, yCoordinate: int = 0):
        
        if all(isinstance(item, int) for item in initialHeights):
            initialHeights = [(value,) for value in initialHeights]
        
        
        self.width = Variable("global_width")
        self.widthValueConstraint : Constraint = ((self.width == width) | "strong")

        self.innerSpacing = Variable("global_inner_spacing")
        self.innerSpacingValueConstraint : Constraint = (self.innerSpacing == innerSpacing) | "strong"

        self.spacing = Variable("global_spacing")
        self.spacingValueConstraint : Constraint = ((self.spacing == spacing) | "strong")
        

        self.groups = [VariableRectangleGroup(self.width,heights,self.innerSpacing,f"group_{i}") for i, heights in enumerate(initialHeights)]
        self._createGroupSpacingConstraints()

        self.origin: VariablePoint2D = VariablePoint2D("origin")

        self.originXCoordinateConstraint : Constraint = (self.origin.X == xCoordinate) | "strong"
        self.originYCoordinateConstraint : Constraint = (self.origin.Y == yCoordinate) | "strong"
        self.leftRectangleXCoordinateConstraint : Constraint = (self.groups[0].leftMostX == self.origin.X + self.spacing) | "required"
        self.leftRectangleYCoordinateConstraint : Constraint = (self.groups[0].bottomY == self.origin.Y) | "required"
    
    def SetIntervalValues(self, intervals: list[list[float,float]]):
        firstGroup = self.groups[0]
        for index, rec in enumerate(firstGroup.rectangles):
            interval = intervals[index]
            rec.leftBottom.secondaryName, rec.rightTop.secondaryName = f"{interval[0]}", f"{interval[1]}"

    def ChangeColor(self, groupIndex: int, rectangleIndex: int, color: str):
        self.groups[groupIndex].rectangles[rectangleIndex].color = color
    
    def ChangeName(self, groupIndex: int, rectangleIndex: int, name: str):
        self.groups[groupIndex].rectangles[rectangleIndex].name = name
    
    
    def _createGroupSpacingConstraints(self):
        for index in range(1,len(self.groups)):
            if index != 0:
                self.groups[index].SetSpacingConstraint((self.groups[index-1].rightMostX + self.spacing == self.groups[index].leftMostX) | "required")
    
    
    def Value(self):
        return [group.Value() for group in self.groups]

    def GetAllConstraints(self):
        result = []
        for group in self.groups:
            result.extend(group.GetAllConstraints())
        return result + [(self.width >= 10) | "required", (self.spacing >= 0) | "required", (self.innerSpacing >= 0) | "required"] \
                    + [(self.groups[i-1].bottomY == self.groups[i].bottomY) | "required" for i in range(1,len(self.groups))] \
                    + [self.widthValueConstraint, self.spacingValueConstraint, self.innerSpacingValueConstraint] \
                    + [self.originXCoordinateConstraint,self.originYCoordinateConstraint,self.leftRectangleXCoordinateConstraint,self.leftRectangleYCoordinateConstraint]
    
class BarChartSolver:
    def __init__(self, width: int, initialHeights: Union[list[int], list[list[int]]], spacing: int, innerSpacing: int, xCoordinate: int = 0, yCoordinate: int = 0):
        
        self.solver = Solver()
        self.variableBarChart = VariableBarChart(width, initialHeights, spacing, innerSpacing, xCoordinate, yCoordinate)
        self.rectangleData = None

        barChartConstraints = set(self.variableBarChart.GetAllConstraints())
        
        
        for constraint in barChartConstraints:
            self.solver.addConstraint(constraint)

        self.solver.addEditVariable(self.variableBarChart.width, "strong")
        self.solver.addEditVariable(self.variableBarChart.spacing, "strong")
        self.solver.addEditVariable(self.variableBarChart.innerSpacing, "strong")


        for group in self.variableBarChart.groups:
            for rec in group:
                self.solver.addEditVariable(rec.height, "strong")
        
        self.solver.addEditVariable(self.variableBarChart.origin.X, "strong")
        self.solver.addEditVariable(self.variableBarChart.origin.Y, "strong")
        
        self.Solve()
    
    def SetIntervalValues(self, intervals: list[list[float,float]]):
        self.variableBarChart.SetIntervalValues(intervals)

    def GetRectangleData(self):
        return self.rectangleData
    
    def GetRectangleDataAsList(self) -> list[ValueRectangle]:
        result = []
        data = self.GetRectangleData()
        for group in data:
            result.extend(group)
        return result

    def GetSpacing(self):
        return self.variableBarChart.spacing.value()
    
    def GetWidth(self):
        return self.variableBarChart.width.value()
    
    def GetOrigin(self):
        return ValuePoint2D(self.variableBarChart.origin.X.value(),self.variableBarChart.origin.Y.value())

    def GetInnerSpacing(self):
        return self.variableBarChart.innerSpacing.value()
    
    def GetName(self, groupIndex: int, rectangleIndex: int):
        return self.variableBarChart.groups[groupIndex].rectangles[rectangleIndex].name
    
    
    def ChangeWidth(self, newWidth: int):
        self.solver.suggestValue(self.variableBarChart.width, newWidth)
        self.Solve()
    
    def ChangeHeight(self, groupIndex: int, rectangleIndex: int, newHeight: int):
        self.solver.suggestValue(self.variableBarChart.groups[groupIndex].rectangles[rectangleIndex].height, newHeight)
        self.Solve()
    
    def ChangeSpacing(self, newSpacing: int):
        self.solver.suggestValue(self.variableBarChart.spacing, newSpacing)
        self.Solve()
    
    def ChangeInnerSpacing(self, newInnerSpacing: int):
        self.solver.suggestValue(self.variableBarChart.innerSpacing, newInnerSpacing)
        self.Solve()
    
    def ChangeOrigin(self, newX: int, newY: int):
        self.solver.suggestValue(self.variableBarChart.origin.X, newX)
        self.solver.suggestValue(self.variableBarChart.origin.Y, newY)
        self.Solve()
    
    def ChangeColor(self, groupIndex: int, rectangleIndex: int, newColor: str):
        self.variableBarChart.ChangeColor(groupIndex,rectangleIndex, newColor)
        self.Update()
    
    def ChangeName(self,groupIndex: int, rectangleIndex: int, newColor: str):
        self.variableBarChart.ChangeName(groupIndex,rectangleIndex, newColor)
        self.Update()
    
    def Solve(self):
        self.solver.updateVariables()
        self.Update()
    
    def Update(self):
        self.rectangleData = self.variableBarChart.Value()
        



class BarChartCanvas:
    def __init__(self, initialValues:  Union[list[float], list[list[float]]], initialWidth: int, initialSpacing: int, initialInnerSpacing: int, canvasWidth: int, canvasHeight: int, graphTitle: str = "",xCoordinate: int = 50, yCoordinate: int = 30):
        
        self.picturePathBuffer = None
        self.dataPathBuffer = None
        self.realValues = None
        self.title = graphTitle

        # rescaling of input data
        self.scaleFactor = 1
        self.canvasHeight = canvasHeight
        self.canvasWidth = canvasWidth
        self.xCoordinate = xCoordinate

        if all(isinstance(value,(float,int)) for value in initialValues):
            self.realValues = [[value,] for value in initialValues]
        else: 
            self.realValues = initialValues


        self._createTranslationTable(self.realValues)

        self._setScaleFactor()

        # solver initialisation
        self.plotSolver = self._createSolver(initialWidth, initialSpacing, initialInnerSpacing, xCoordinate, yCoordinate)

        # Fields for event register
        #left button
        self.dragEdge = None
        self.dragStart = ValuePoint2D(0,0)
        self.dragIndex = None
        self.originalLeftX = None
        self.originalSpacing = None
        self.rightEdgeCursorOffset = None
        self.originalHeight = None

        #right button
        self.rectangleIndexToChange = None
    
    def _setScaleFactor(self):
        maxValue = float("-inf")
        for group in self.realValues:
            maximum = max(group)
            if maxValue <= maximum:
                maxValue = maximum

        if not (self.canvasHeight*0.3 <= maxValue <= self.canvasHeight*0.8):
            self.scaleFactor = self.canvasHeight*0.8/maxValue
    
    def _createSolver(self, initialBarWidth: int, initialSpacing: int, initialInnerSpacing: int, xCoordinate: int, yCoordinate: int):
        initialHeights = [] # rescaled heights
        for group in self.realValues:
            initialHeights.append([int(value*self.scaleFactor) for value in group])
        return BarChartSolver(initialBarWidth, initialHeights, initialSpacing, initialInnerSpacing, xCoordinate, yCoordinate)

    def _setRightClickMenu(self, frame: tk.Frame):
        self.menu = tk.Menu(frame, tearoff=0)
        self.menu.add_command(label="Change color", command=self._changeColor)
        self.menu.add_command(label="Change name", command=self._changeName)

    def View(self):        
        # UI features initialisation
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.canvas = tk.Canvas(self.frame, width=self.canvasWidth, height=self.canvasHeight, bg="white")
        self.canvas.pack()

        self.savePictureButton = tk.Button(self.frame, text="Save as png", command=self.on_savePictureButton_click)
        self.savePictureButton.pack(pady=5)

        self.dataWindow = tk.Text(self.frame, height=5, width=40)
        self.dataWindow.pack()

        self.saveDataButton = tk.Button(self.frame, text="Save data as csv", command=self.on_saveDataButton_click)
        self.saveDataButton.pack(pady=5)

        self._setRightClickMenu(self.frame)
        

        self._drawPlot()
        self._writeValues() 

        # binding methods to mouse events
        self.canvas.bind("<Button-1>", self.on_left_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_up)
        self.canvas.bind("<Motion>", self.check_cursor)
        self.canvas.bind("<Button-3>", self.on_right_down)
        self.root.mainloop()
    

    def _createTranslationTable(self, heights: Union[list[float], list[tuple[float, ...]]]):
        self.translationTable = []
        for groupIndex, group in enumerate(heights):
            for itemIndex in range(len(group)):
                self.translationTable.append((groupIndex,itemIndex))
    
    def _indexToGroupIndex(self, index: int):
        if index >= len(self.translationTable):
            raise Exception(f"Index {index} is too large to translate into group coordinates. There are only {len(self.translationTable)} rectangles.")
        return self.translationTable[index]


    @staticmethod
    def _ceilToNearestTen(number: int):
        return ((number // 10) + 1) * 10

    @staticmethod
    def _divideIntervalFromZeroTo(number: int, parts: int):
            step = number // (parts - 1) 
            return [i * step for i in range(parts)]

    def _drawAxes(self, maximumValue: int, leftCornerXAxis: int):  
        """
        Draws axes on the canvas
        """

        topNumber = self._ceilToNearestTen(maximumValue) 

        marks = self._divideIntervalFromZeroTo(topNumber, 5)
        origin = self.plotSolver.GetOrigin()
      
        self.canvas.create_line(origin.X, self.canvasHeight - origin.Y, leftCornerXAxis + 10, self.canvasHeight - origin.Y, fill="black", width=1)
        self.canvas.create_line(origin.X, self.canvasHeight - origin.Y, origin.X, self.canvasHeight - origin.Y - topNumber, fill="black", width=1)

        for mark in marks:
            y = self.canvasHeight - origin.Y - mark
            self.canvas.create_line(origin.X - 5, y, origin.X, y, fill="black")

            trueValue = mark/self.scaleFactor
            valueString = f"{(trueValue):.2g}" if (trueValue <= 1e-04 or trueValue >= 1e06) else f"{(trueValue):.2f}"

            self.canvas.create_text(origin.X - 10, y, text=f"{valueString}", anchor="e") 
    
    def _drawRectangles(self): 
        """
        Draws rectangles on the plot and writes their names under them.
        """
        rectangles = self.plotSolver.GetRectangleDataAsList()
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
        rectangles = self.plotSolver.GetRectangleDataAsList()
        self._drawRectangles()

        originY = self.plotSolver.GetOrigin().Y
        
        highestRectangleHeight = max([rec.rightTop.Y - originY for rec in rectangles])
        self._drawAxes(highestRectangleHeight, rectangles[-1].rightTop.X)    

    def _writeValues(self):
        """
        Displays all data for the user and highlights which data is being edited
        """
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        valueEdited = self.dragEdge == "top"
        rectangles = self.plotSolver.GetRectangleDataAsList()

        for i in range(len(rectangles)-1, -1, -1):
            rec = rectangles[i]
            trueValue = rec.GetHeight()/self.scaleFactor
            valueString = ""
            if ((trueValue >= 1e+06) or (trueValue <= 1e-04)):
                valueString = f"{trueValue:.4g}"
            else:
                valueString = str(trueValue)


            if valueEdited and i == self.dragIndex:
                self.dataWindow.insert("1.0",f"{rec.name} = {valueString}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"{rec.name} = {valueString}\n")
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
    
    def _isNearOrigin(self, event):
        origin = self.plotSolver.GetOrigin()
        return self._isNear(event.x, origin.X) and self._isNear(event.y, self.canvasHeight - origin.Y)

    def _isInsideOfRectangle(self,event, rectangle: ValueRectangle):
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        leftBottomYNormalized = self.canvasHeight - rectangle.leftBottom.Y
        return (rectangle.leftBottom.X <= event.x <= rectangle.rightTop.X) \
                and (rightTopYNormalized <= event.y <= leftBottomYNormalized)

    def _clickedOnOrigin(self, event):
        self.dragEdge = "origin"
        
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
        groupIndex = self._indexToGroupIndex(rectangleIndex)

        self.dragEdge = "left" + ("Most" if groupIndex[1] == 0 else "Middle")
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = rectangleIndex
        
        self.originalLeftX = rectangle.leftBottom.X
        self.originalSpacing = self.plotSolver.GetSpacing()
    
    def _clickedOnTopEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle):
        """
        Registers that the user clicked on a top edge of some rectangle
        """
        self.dragEdge = "top"
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = rectangleIndex
        self.originalHeight = rectangle.rightTop.Y - rectangle.leftBottom.Y

    def _changeColor(self):
        groupIndex = self._indexToGroupIndex(self.rectangleIndexToChange)
        color = colorchooser.askcolor(title="Choose different color")
        if color[1] == None:
            return
        self.plotSolver.ChangeColor(groupIndex[0],groupIndex[1],color[1])
        self._drawPlot()
    
    def _changeName(self):
        groupIndex = self._indexToGroupIndex(self.rectangleIndexToChange)
        currentName = self.plotSolver.GetName(groupIndex[0],groupIndex[1])
        newName = simpledialog.askstring("Change name", "New name:", initialvalue=currentName)
        if newName == None:
            return
        self.plotSolver.ChangeName(groupIndex[0], groupIndex[1], newName)
        self._drawPlot()
        self._writeValues()
        pass

    def on_right_down(self, event):
        for index, rec in enumerate(self.plotSolver.GetRectangleDataAsList()):
            if self._isInsideOfRectangle(event, rec):
                self.rectangleIndexToChange = index
                self.menu.post(event.x_root, event.y_root)
                break
    
    def on_left_down(self, event):
        """
        This method is triggered when the user clicks on canvas.
        It identifies what the program should do next and registers the event
        """
        for recIndex, rec in enumerate(self.plotSolver.GetRectangleDataAsList()):
            if self._isNearLeftEdge(event, rec): # change in spacing
                self._clickedOnLeftEdge(event, recIndex, rec)
                return
            elif self._isNearRightEdge(event, rec): # change in width
                self._clickedOnRightEdge(event, recIndex, rec)
                return
            elif self._isNearTopEdge(event, rec): # change in height
                self._clickedOnTopEdge(event, recIndex, rec)
                return
            elif self._isNearOrigin(event):
                self._clickedOnOrigin(event)
            else:
                continue

    def on_mouse_move(self, event):
        """
        If method on_mouse_down registered an event near to some edge of some rectangle, then this method mekes appropriate changes toi the graph if the user has moved with mouse.
        """
        if self.dragEdge is None:
            return
        
        groups = self.plotSolver.GetRectangleData()
        origin = self.plotSolver.GetOrigin()

        if self.dragIndex != None:
            groupDragIndex = self._indexToGroupIndex(self.dragIndex)
            groupIndex, rectangleInGroupIndex = groupDragIndex[0], groupDragIndex[1]

        if self.dragEdge == "right":
            newWidth = (event.x - self.plotSolver.GetSpacing()*(groupIndex+1) - rectangleInGroupIndex*self.plotSolver.GetInnerSpacing() - sum([self.plotSolver.GetInnerSpacing()*(len(groups[i])-1) for i in range(0,groupIndex)]) - origin.X)//(self.dragIndex+1)
            if newWidth > 10:
                self.plotSolver.ChangeWidth(newWidth)



        elif self.dragEdge == "top":
            dy = self.dragStart.Y - event.y  
            newHeight = self.originalHeight + dy
            if newHeight > 0:
                self.plotSolver.ChangeHeight(groupIndex, rectangleInGroupIndex, newHeight)
            self._writeValues()

        elif self.dragEdge == "leftMost":
            if self.dragIndex == 0:
                newSpacing = event.x - origin.X
            else:
                newSpacing = (event.x - sum([groups[i][-1].rightTop.X - groups[i][0].leftBottom.X for i in range(0,groupIndex)]) - origin.X) // (1+groupIndex)  
            if newSpacing > 0:
                self.plotSolver.ChangeSpacing(newSpacing)
        
        elif self.dragEdge == "leftMiddle" and rectangleInGroupIndex > 0:
            newInnerSpacing = (event.x - self.dragIndex*self.plotSolver.GetWidth() - (1+groupIndex)*self.plotSolver.GetSpacing() - origin.X) // (sum([(len(groups[k])-1) for k in range(0,groupIndex)])+rectangleInGroupIndex)
            if newInnerSpacing > 0:
                self.plotSolver.ChangeInnerSpacing(newInnerSpacing)

        elif self.dragEdge == "origin": #done
            self.plotSolver.ChangeOrigin(event.x, self.canvasHeight - event.y)
        
        self._drawPlot()

    def on_left_up(self, event):
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
        for idx, rec in enumerate(self.plotSolver.GetRectangleDataAsList()):
            if self._isNearLeftEdge(event, rec):
                self.canvas.config(cursor="hand2")
                return
            elif self._isNearRightEdge(event, rec):
                self.canvas.config(cursor="sb_h_double_arrow")
                return
            elif self._isNearTopEdge(event, rec):
                self.canvas.config(cursor="sb_v_double_arrow")
                return
            elif self._isNearOrigin(event):
                self.canvas.config(cursor="fleur")
                return
        self.canvas.config(cursor="arrow")

    def _drawRectanglesPNG(self, draw: ImageDraw):
        rectangles = self.plotSolver.GetRectangleDataAsList()
        for rec in rectangles:
            x1 = rec.leftBottom.X
            y1 = self.canvasHeight - rec.leftBottom.Y
            
            x2 = rec.rightTop.X
            y2 = self.canvasHeight - rec.rightTop.Y
            draw.rectangle((x1,y2,x2,y1), fill=rec.color, outline="black")
            font = ImageFont.load_default()
            text = rec.name

            # get text size
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # text position
            x_center = (x1 + x2) / 2
            y_text = (y1 + 10)

            draw.text(
                (x_center - text_width / 2, y_text - text_height/2),
                text,
                fill="black",
                font=font)

    def _drawAxesPNG(self, draw: ImageDraw, maximumValue: int, leftCornerXAxis: int):  
        """
        Draws axes on the PNG output
        """
        topNumber = self._ceilToNearestTen(maximumValue) 

        marks = self._divideIntervalFromZeroTo(topNumber, 5)
        origin = self.plotSolver.GetOrigin()
      
        draw.line((origin.X, self.canvasHeight - origin.Y, leftCornerXAxis + 10, self.canvasHeight - origin.Y), fill=(0,0,0), width=1)
        draw.line((origin.X, self.canvasHeight - origin.Y, origin.X, self.canvasHeight - origin.Y - topNumber), fill=(0,0,0), width=1)

        for mark in marks:
            y = self.canvasHeight - origin.Y - mark
            draw.line((origin.X - 5, y, origin.X, y), fill=(0,0,0))

            trueValue = mark/self.scaleFactor
            valueString = f"{(trueValue):.2g}" if (trueValue <= 1e-04 or trueValue >= 1e06) else f"{(trueValue):.2f}"
            font = ImageFont.load_default()

            # get text size
            bbox = font.getbbox(valueString)
            textWidth = bbox[2] - bbox[0]
            textHeight = bbox[3] - bbox[1]

            draw.text((origin.X - 10 - textWidth, y - textHeight/2), text=f"{valueString}", fill = (0,0,0))
    
    def _writePlotTitlePNG(self, draw: ImageDraw):
        font = ImageFont.truetype("arialbd.ttf", 16)
        text = self.title
        bbox = font.getbbox(text)
        textWidth = bbox[2] - bbox[0]
        draw.text((self.canvasWidth / 2 - textWidth, 20),text=text,font=font,fill = (0,0,0))

    def _makePNG(self, name: str):
        rectangles = self.plotSolver.GetRectangleDataAsList()
        highestRectangleHeight = max([rec.rightTop.Y - self.plotSolver.GetOrigin().Y for rec in rectangles])
        img = Image.new("RGB", (self.canvasWidth, self.canvasHeight), color="white")
        draw = ImageDraw.Draw(img)
        self._drawRectanglesPNG(draw)
        self._drawAxesPNG(draw, highestRectangleHeight, rectangles[-1].rightTop.X)
        self._writePlotTitlePNG(draw)
        img.save(f"{name}.png")

    def on_savePictureButton_click(self):
        self.frame.update()
        self.canvas.update()

        if self.picturePathBuffer == None:
            self.picturePathBuffer = os.path.join(os.getcwd(), self.title)

        pictureName = simpledialog.askstring("Save plot", "Image name (without extension): ", initialvalue=self.picturePathBuffer)

        if pictureName == None:
            return
        else:
            self.picturePathBuffer = pictureName 
        
        print("saving canvas to", pictureName + ".png")
        self._makePNG(pictureName)

    def _saveDataAsCSV(self, file: str):
        with open(file,"w") as output:
            groups = self.plotSolver.GetRectangleData()
            for group in groups:
                for i in range(len(group)):
                    rec = group[i]
                    if i != 0:
                        output.write(",")
                    height = rec.GetHeight()
                    value = height/self.scaleFactor
                    output.write(f"{rec.name},{value}")
                output.write("\n")

    def on_saveDataButton_click(self):
        if self.dataPathBuffer == None:
            self.picturePathBuffer = os.path.join(os.getcwd(), self.title)
        fileName = simpledialog.askstring("Save data", "File name (without extension): ", initialvalue=self.picturePathBuffer) + ".csv"
        if fileName == None:
            return
        else:
            self._saveDataAsCSV(fileName)

        pass

#def __init__(self, initialValues:  Union[list[float], list[list[float]]], initialWidth: int, initialSpacing: int, initialInnerSpacing: int, canvasWidth: int, canvasHeight: int, graphTitle: str = "",xCoordinate: int = 50, yCoordinate: int = 30):
        

class HistogramCanvas(BarChartCanvas):
    def __init__(self, initialValues: list[list[float,float,float]], initialWidth: int, initialPadding: int, canvasWidth: int, canvasHeight: int, graphTitle: str = "",xCoordinate: int = 50, yCoordinate: int = 30):
        self.picturePathBuffer = None
        self.dataPathBuffer = None
        self.realValues = []
        self.title = graphTitle
        
        # rescaling of input data
        self.scaleFactor = 1
        self.canvasHeight = canvasHeight
        self.canvasWidth = canvasWidth
        self.xCoordinate = xCoordinate

        self.intervals = []
        histogramGroup = []
        for value in initialValues:
            self.intervals.append([value[0],value[1]])
            histogramGroup.append(value[2])
        self.realValues.append(histogramGroup)
        

        self._createTranslationTable(self.realValues)
        self._setScaleFactor()

        self.plotSolver = self._createSolver(initialWidth, initialPadding, 0, xCoordinate, yCoordinate)
        self.plotSolver.SetIntervalValues(self.intervals)
        self.plotSolver.Update()

        # Fields for event register
        #left button
        self.dragEdge = None
        self.dragStart = ValuePoint2D(0,0)
        self.dragIndex = None
        self.originalLeftX = None
        self.originalSpacing = None
        self.rightEdgeCursorOffset = None
        self.originalHeight = None

        #right button
        self.rectangleIndexToChange = None
    
    def _setRightClickMenu(self, frame: tk.Frame):
        self.menu = tk.Menu(frame, tearoff=0)
        self.menu.add_command(label="Change color", command=self._changeColor)

    def _drawRectangles(self): 
        """
        Draws rectangles on the plot and writes their names under them.
        """
        rectangles = self.plotSolver.GetRectangleDataAsList()
        for rec in rectangles: 
            x1 = rec.leftBottom.X
            y1 = self.canvasHeight - rec.leftBottom.Y
            
            x2 = rec.rightTop.X
            y2 = self.canvasHeight - rec.rightTop.Y
            self.canvas.create_rectangle(x1,y2,x2,y1, fill=rec.color, outline="black")
            self.canvas.create_text(x1,y1 + 10, text=rec.leftBottom.secondaryName)
            self.canvas.create_text(x2,y1 + 10, text=rec.rightTop.secondaryName)

    def _writeValues(self):
        """
        Displays all data for the user and highlights which data is being edited
        """
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        valueEdited = self.dragEdge == "top"
        rectangles = self.plotSolver.GetRectangleDataAsList()

        for i in range(len(rectangles)-1, -1, -1):
            rec = rectangles[i]
            trueValue = rec.GetHeight()/self.scaleFactor
            valueString = ""
            if ((trueValue >= 1e+06) or (trueValue <= 1e-04)):
                valueString = f"{trueValue:.4g}"
            else:
                valueString = str(trueValue)


            if valueEdited and i == self.dragIndex:
                self.dataWindow.insert("1.0",f"({rec.leftBottom.secondaryName}, {rec.rightTop.secondaryName}) = {valueString}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"({rec.leftBottom.secondaryName}, {rec.rightTop.secondaryName}) = {valueString}\n")
        self.dataWindow.config(state="disabled")

    def _clickedOnLeftEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle): 
        """
        Registers that the user clicked on a left edge of some rectangle
        """
        groupIndex = self._indexToGroupIndex(rectangleIndex)
        if groupIndex[1] != 0:
            return
        self.dragEdge = "leftMost"
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = rectangleIndex
        
        self.originalLeftX = rectangle.leftBottom.X
        self.originalSpacing = self.plotSolver.GetSpacing()

    def check_cursor(self,event):
        """
        Changes cursor according to its position.
        """
        for index, rec in enumerate(self.plotSolver.GetRectangleDataAsList()):
            groupIndex = self._indexToGroupIndex(index)
            if self._isNearLeftEdge(event, rec) and groupIndex[1] == 0:
                self.canvas.config(cursor="hand2")
                return
            elif self._isNearRightEdge(event, rec):
                self.canvas.config(cursor="sb_h_double_arrow")
                return
            elif self._isNearTopEdge(event, rec):
                self.canvas.config(cursor="sb_v_double_arrow")
                return
            elif self._isNearOrigin(event):
                self.canvas.config(cursor="fleur")
                return
        self.canvas.config(cursor="arrow")

    def _drawRectanglesPNG(self, draw: ImageDraw):
        rectangles = self.plotSolver.GetRectangleDataAsList()
        for rec in rectangles:
            x1 = rec.leftBottom.X
            y1 = self.canvasHeight - rec.leftBottom.Y
            
            x2 = rec.rightTop.X
            y2 = self.canvasHeight - rec.rightTop.Y
            draw.rectangle((x1,y2,x2,y1), fill=rec.color, outline="black")
            font = ImageFont.load_default()
            textLeft = rec.leftBottom.secondaryName
            textRight = rec.rightTop.secondaryName

            # get text size
            bboxLeft = font.getbbox(textLeft)
            textLeft_width = bboxLeft[2] - bboxLeft[0]
            textLeft_height = bboxLeft[3] - bboxLeft[1]

            bboxRight = font.getbbox(textRight)
            textRight_width = bboxRight[2] - bboxRight[0]
            textRight_height = bboxRight[3] - bboxRight[1]

            y_text = (y1 + 10)

            draw.text(
                (x1 - textLeft_width / 2, y_text - textLeft_height/2),
                textLeft,
                fill="black",
                font=font)
            draw.text(
                (x2 - textRight_width / 2, y_text - textRight_height/2),
                textRight,
                fill="black",
                font=font)

    def _saveDataAsCSV(self, file: str):
        with open(file,"w") as output:
            rectangles = self.plotSolver.GetRectangleDataAsList()
            for rec in rectangles:
                height = rec.GetHeight()
                value = height/self.scaleFactor
                output.write(f"{rec.leftBottom.secondaryName},{rec.rightTop.secondaryName},{value}\n")

if __name__ == "__main__":
    initial_heights = [[0,1.5,9],[1.5,3,7],[3,4.5,8]]
    initial_width = 40
    initial_spacing = 100
    innerSpacing = 5
    canvas_width = 1000
    canvas_height = 500
    

    barchart = HistogramCanvas(initial_heights, initial_width, initial_spacing, canvas_width, canvas_height, "Test values")
    barchart.View()


