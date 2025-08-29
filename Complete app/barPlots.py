import kiwisolver
from kiwisolver import Variable, Constraint, Solver,  strength
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
from tkinter import font

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
    def __init__(self, width: Variable, height: int, name: str, color = "blue", widthScale : float = 1):
        self.height = Variable(f"{name}_height")
        self.width = width
        self.widthScale = widthScale
        self.name = name
        self.color = color
        self.leftBottom = VariablePoint2D(name+".leftBottom")
        self.rightTop = VariablePoint2D(name+".rightTop")

        self.heightConstraint : Constraint = (self.height == float(height)) | "strong"
        self.horizontalPositionConstraint : Constraint = ((self.leftBottom.X + self.width * self.widthScale == self.rightTop.X) | "required")
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
   
    
    def SetSpacingConstraint(self, spacingConstraint : Constraint):
        self.spacingConstraint = spacingConstraint
    
    def GetAllConstraints(self):
        constraints = [constraint for constraint in self] + [(self.height >= 0)|"required",(self.leftBottom.X >= 0) | "required", (self.leftBottom.Y >= 0) | "required", (self.rightTop.X >= 0) | "required", (self.rightTop.Y >= 0) | "required"]
        return constraints
    
    def Value(self):
        return ValueRectangle(self.leftBottom.Value(), self.rightTop.Value(), self.color, self.name)

class VariableRectangleGroup:
    def __init__(self, rectangleWidth: Variable, heights: list[int], innerSpacing: Variable, names: list[str], color: str = "blue", widthScales : list[float] = None):
        self.rectangles = [VariableRectangle(rectangleWidth, height, names[i] if names is not None else "", color, (1 if widthScales is None else widthScales[i])) for i,height in enumerate(heights)]
        self.innerSpacing = innerSpacing


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


class VariableChart:
    def __init__(self, width : int, spacing : int, xCoordinate : int, yCoordinate : int):
        self.width = Variable("global_width")
        self.widthValueConstraint : Constraint = ((self.width == width) | "strong")

        self.spacing = Variable("global_spacing")
        self.spacingValueConstraint : Constraint = ((self.spacing == spacing) | "strong")

        self.origin: VariablePoint2D = VariablePoint2D("origin")
        self.yAxisHeight: Variable = Variable("axisTop")


        #self.originXCoordinateConstraint : Constraint = (self.origin.X == xCoordinate)
        #self.originXCoordinateConstraint = self.originXCoordinateConstraint | "strong" 
        #self.originYCoordinateConstraint : Constraint = (self.origin.Y == yCoordinate)
        #self.originYCoordinateConstraint = self.originYCoordinateConstraint | "strong"
        self.originXCoordinateConstraint: Constraint = Constraint(self.origin.X - xCoordinate, "==", "strong")

        self.originYCoordinateConstraint: Constraint = Constraint(self.origin.Y - yCoordinate, "==", "strong")

class VariableBarChart(VariableChart):
    def __init__(self, width: int, initialHeights: list[list[int]], spacing: int, innerSpacing: int, rectangleNames : list[list[str]], xCoordinate: int = 0, yCoordinate: int = 0, widthScalesForGroups : list[list[float]] = None):
        
        super().__init__(width, spacing, xCoordinate, yCoordinate)

        self.innerSpacing = Variable("global_inner_spacing")
        self.innerSpacingValueConstraint : Constraint = (self.innerSpacing == innerSpacing) | "strong"
        
        self.groups = [VariableRectangleGroup(self.width,heights,self.innerSpacing, rectangleNames[i] if rectangleNames is not None else None, "blue" ,None if widthScalesForGroups is None else widthScalesForGroups[i]) for i, heights in enumerate(initialHeights)]
        self._createGroupSpacingConstraints()

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
                    + [self.originXCoordinateConstraint,self.originYCoordinateConstraint,self.leftRectangleXCoordinateConstraint,self.leftRectangleYCoordinateConstraint] \

class BarChartSolver:
    def __init__(self, width: int, initialHeights: Union[list[int], list[list[int]]], spacing: int, innerSpacing: int, rectangleNames : list[list[str]], xCoordinate: int = 0, yCoordinate: int = 0, widthScalesForGroups : list[list[float]] = None):
        
        self.solver = Solver()
        self.variableBarChart = VariableBarChart(width, initialHeights, spacing, innerSpacing, rectangleNames, xCoordinate, yCoordinate, widthScalesForGroups)
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

        self.solver.addEditVariable(self.variableBarChart.yAxisHeight, "strong")
        self.solver.suggestValue(self.variableBarChart.yAxisHeight, max(max(group) for group in initialHeights)+10)
        
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
    
    def GetAxisHeight(self):
        return self.variableBarChart.yAxisHeight.value()
    
    def ChangeAxisHeight(self, newY : float):
        self.solver.suggestValue(self.variableBarChart.yAxisHeight,newY)
        self.Solve()
    
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
        



class PlotCanvas:
    def __init__(self,canvasWidth : int, canvasHeight : int, title : str, xAxisLabel : str, yAxisLabel : str):
        self.canvasWidth : int = canvasWidth
        self.canvasHeight : int = canvasHeight
        self.title = title
        self.picturePathBuffer = None
        self.dataPathBuffer = None
        self.xAxisValue = 0
        self.xAxisLabel = xAxisLabel
        self.yAxisLabel = yAxisLabel
        self._setEventRegistersLeftButton()
        self._setEventRegistersRightButton()    

    def _setEventRegistersLeftButton(self):
        self.dragEdge = None
        self.dragStart = ValuePoint2D(0,0)
        self.dragIndex = None
        self.originalLeftX = None
        self.originalSpacing = None
        self.rightEdgeCursorOffset = None
        self.originalHeight = None
    
    def _setEventRegistersRightButton(self):
        self.rectangleIndexToChange = None

    def _setScaleFactor(self):
        self.scaleFactor = 1

    def View(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.canvas = tk.Canvas(self.frame, width=self.canvasWidth, height=self.canvasHeight, bg="white")
        self.canvas.pack()

        self.savePictureButton = tk.Button(self.frame, text="Save as png", command=self.on_savePictureButton_click)
        self.savePictureButton.pack(pady=5)

        self.dataWindow = tk.Text(self.frame, height=20, width=40)
        self.dataWindow.pack()

        self.saveDataButton = tk.Button(self.frame, text="Save data as csv", command=self.on_saveDataButton_click)
        self.saveDataButton.pack(pady=5)

        self.defaultMenu = tk.Menu(self.frame,tearoff=0)
        self.defaultMenu.add_command(label = "Change title", command=self.ChangeTitle)
        
    
    def ChangeTitle(self):
        newTitle = simpledialog.askstring("Enter new title","New title: ")
        if newTitle is None:
            return
        else:
            self.title = newTitle
            self._drawPlot()

    def _UIRun(self):
        self.canvas.bind("<Button-1>", self.on_left_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_up)
        self.canvas.bind("<Motion>", self.check_cursor)
        self.canvas.bind("<Button-3>", self.on_right_down)
        self.root.mainloop()
    
    def on_left_down(self,event):
        raise NotImplementedError("Method on_left_down must be declared in subclass")

    def on_right_down(self, event):
        self.defaultMenu.post(event.x_root, event.y_root)
    
    def on_mouse_move(self, event):
        raise NotImplementedError("Method on_mouse_move must be declared in subclass")
    
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
    
    @staticmethod
    def _ceilToNearestTen(number: int):
        return ((number // 10) + 1) * 10

    def _writePlotTitle(self):  
        self.canvas.create_text(self.canvasWidth / 2, 20,text=self.title,font=("Arial", 16, "bold"))
    
    @staticmethod
    def _floorToNearestTen(number: int):
        return ((number // 10) - 1) * 10

    @staticmethod
    def _divideInterval(low: int, high: int, parts: int):
        if parts < 2:
            return [low, high]

        step = (high - low) // (parts - 1)
        return [low + i * step for i in range(parts)]



    def _drawAxes(self, maximumValue: int, leftCornerXAxis: int, origin : ValuePoint2D, minimumValue : int = 0):  
        """
        Draws axes on the canvas
        """
        topNumber = self._ceilToNearestTen(maximumValue) 

        marks = self._divideInterval(minimumValue, topNumber, 5)
      
        self.canvas.create_line(origin.X, self.canvasHeight - origin.Y, leftCornerXAxis + 10, self.canvasHeight - origin.Y, fill="black", width=1)
        self.canvas.create_line(origin.X, self.canvasHeight - origin.Y - minimumValue, origin.X, self.canvasHeight - origin.Y - topNumber, fill="black", width=1)

        for mark in marks:
            y = self.canvasHeight - origin.Y - mark
            self.canvas.create_line(origin.X - 5, y, origin.X, y, fill="black")

            trueValue = mark/self.scaleFactor + self.xAxisValue
            valueString = f"{(trueValue):.2g}" if (trueValue <= 1e-04 or trueValue >= 1e06) else f"{(trueValue):.2f}"

            self.canvas.create_text(origin.X - 10, y, text=f"{valueString}", anchor="e")

        
        boldFont = font.Font(family="Helvetica", size=10, weight="bold")
        self.canvas.create_text(leftCornerXAxis + 20, self.canvasHeight - origin.Y + 10, text=self.xAxisLabel, anchor="n",font=boldFont)
        self.canvas.create_text(origin.X, self.canvasHeight - origin.Y - topNumber - 10, text=self.yAxisLabel, anchor="s",font=boldFont)
    
    def _drawAxesPNG(self, draw: ImageDraw, maximumValue: int, leftCornerXAxis: int, origin : ValuePoint2D, minimumValue : int = 0):  
        """
        Draws axes on the PNG output
        """
        topNumber = self._ceilToNearestTen(maximumValue) 

        marks = self._divideInterval(minimumValue,topNumber, 5)
      
        draw.line((origin.X, self.canvasHeight - origin.Y, leftCornerXAxis + 10, self.canvasHeight - origin.Y), fill=(0,0,0), width=1)
        draw.line((origin.X, self.canvasHeight - origin.Y - minimumValue, origin.X, self.canvasHeight - origin.Y - topNumber), fill=(0,0,0), width=1)

        for mark in marks:
            y = self.canvasHeight - origin.Y - mark
            draw.line((origin.X - 5, y, origin.X, y), fill=(0,0,0))

            trueValue = mark/self.scaleFactor + self.xAxisValue
            valueString = f"{(trueValue):.2g}" if (trueValue <= 1e-04 or trueValue >= 1e06) else f"{(trueValue):.2f}"
            font = ImageFont.load_default()

            # get text size
            bbox = font.getbbox(valueString)
            textWidth = bbox[2] - bbox[0]
            textHeight = bbox[3] - bbox[1]

            draw.text((origin.X - 10 - textWidth, y - textHeight/2), text=f"{valueString}", fill = (0,0,0))
        
        #Axis labels
        font = ImageFont.truetype("arialbd.ttf", 12)
        bbox = font.getbbox(self.xAxisLabel)
        textW = bbox[2] - bbox[0]
        textH = bbox[3] - bbox[1]
        draw.text(
            (leftCornerXAxis + 10 - textW/2, self.canvasHeight - origin.Y + 10), 
            text=self.xAxisLabel, fill=(0,0,0), font=font
        )

        bbox = font.getbbox(self.yAxisLabel)
        textW = bbox[2] - bbox[0]
        textH = bbox[3] - bbox[1]
        draw.text(
            (origin.X - textW/2, self.canvasHeight - origin.Y - topNumber - textH - 5), 
            text=self.yAxisLabel, fill=(0,0,0), font=font
        )

    def _writePlotTitle(self):  
        self.canvas.create_text(self.canvasWidth / 2, 20,text=self.title,font=("Arial", 16, "bold"))
    
    def _drawPlot(self):
        raise NotImplementedError("Method _drawPlot must be declared in subclass")
    def _writeValues(self):
        raise NotImplementedError("Method _writeValues must be declared in subclass")

    @staticmethod
    def _isNear(val1, val2, tolerance=5):
        """
        Returns True, if two values are near to each other with given tolerance
        """
        return abs(val1 - val2) < tolerance

    def check_cursor(self,event):
        self.canvas.config(cursor="arrow")
    
    def _writePlotTitlePNG(self, draw: ImageDraw):
        font = ImageFont.truetype("arialbd.ttf", 16)
        text = self.title
        bbox = font.getbbox(text)
        textWidth = bbox[2] - bbox[0]
        draw.text((self.canvasWidth / 2 - textWidth, 20),text=text,font=font,fill = (0,0,0))
    
    def _makePNG(self, name : str):
        raise NotImplementedError("Method _makePNG must be declared in subclass")

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
    
    def _saveDataAsCSV(self, file : str):
        raise NotImplementedError("Method _saveDataAsCSV must be declared in subclass")
    
    def on_saveDataButton_click(self):
        if self.dataPathBuffer == None:
            self.picturePathBuffer = os.path.join(os.getcwd(), self.title)
        fileName = simpledialog.askstring("Save data", "File name (without extension): ", initialvalue=self.picturePathBuffer)
        if fileName == None:
            return
        else:
            self._saveDataAsCSV(fileName + ".csv")

class BarChartCanvas(PlotCanvas):
    def __init__(self, initialValues:  Union[list[float], list[list[float]]], initialWidth: int, initialSpacing: int, initialInnerSpacing: int, canvasWidth: int, canvasHeight: int, rectangleNames : list[list[str]], graphTitle: str = "",xCoordinate: int = 50, yCoordinate: int = 30, xAxisLabel : str = "", yAxisLabel : str = ""):
        
        super().__init__(canvasWidth,canvasHeight,graphTitle, xAxisLabel, yAxisLabel)

        self.realValues = None

        if all(isinstance(value,(float,int)) for value in initialValues):
            self.realValues = [[value,] for value in initialValues]
        else: 
            self.realValues = initialValues

        self._createTranslationTable(self.realValues)

        # solver initialisation
        self._setScaleFactor()
        self.plotSolver = self._createSolver(initialWidth, initialSpacing, initialInnerSpacing, xCoordinate, yCoordinate, rectangleNames)

    
    def _setScaleFactor(self):
        super()._setScaleFactor()
        maxValue = float("-inf")
        for group in self.realValues:
            maximum = max(group)
            if maxValue <= maximum:
                maxValue = maximum

        if not (self.canvasHeight*0.3 <= maxValue <= self.canvasHeight*0.8):
            self.scaleFactor = self.canvasHeight*0.8/maxValue
    
    def _createSolver(self, initialBarWidth: int, initialSpacing: int, initialInnerSpacing: int, xCoordinate: int, yCoordinate: int, names : list[list[str]] = None, widthScalesForGroups : list[list[float]] = None):
        initialHeights = [] # rescaled heights
        for group in self.realValues:
            initialHeights.append([int(value*self.scaleFactor) for value in group])
        return BarChartSolver(initialBarWidth, initialHeights, initialSpacing, initialInnerSpacing, names, xCoordinate, yCoordinate, widthScalesForGroups)

    def _setRightClickMenu(self, frame: tk.Frame):
        self.menu = tk.Menu(frame, tearoff=0)
        self.menu.add_command(label="Change color", command=self._changeColor)
        self.menu.add_command(label="Change name", command=self._changeName)

    def View(self):        
        # UI features initialisation
        super().View()

        self._setRightClickMenu(self.frame)

        self._drawPlot()
        self._writeValues() 

        # binding methods to mouse events
        super()._UIRun()
    
    def _createTranslationTable(self, heights: Union[list[float], list[tuple[float, ...]]]):
        self.translationTable = []
        for groupIndex, group in enumerate(heights):
            for itemIndex in range(len(group)):
                self.translationTable.append((groupIndex,itemIndex))
    
    def _indexToGroupIndex(self, index: int):
        if index >= len(self.translationTable):
            raise Exception(f"Index {index} is too large to translate into group coordinates. There are only {len(self.translationTable)} rectangles.")
        return self.translationTable[index]

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

    def _drawPlot(self):
        """
        Draws rectangles and axes on the plot
        """
        self.canvas.delete("all")
        self._writePlotTitle()
        rectangles = self.plotSolver.GetRectangleDataAsList()
        self._drawRectangles()

        origin = self.plotSolver.GetOrigin()
        
        #highestRectangleHeight = max([rec.rightTop.Y - origin.Y for rec in rectangles])
        y = self.plotSolver.GetAxisHeight()

        self._drawAxes(self.plotSolver.GetAxisHeight(), rectangles[-1].rightTop.X, origin)


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
    
    def _isNearTopOfYAxis(self,event):
        topNormalized = self.canvasHeight - self.plotSolver.GetAxisHeight() - self.plotSolver.GetOrigin().Y
        return self._isNear(event.y, topNormalized, 10) and self._isNear(event.x, self.plotSolver.GetOrigin().X, 10)

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
    
    def _clickedOnTopOfAxis(self, event):
        self.dragEdge = "axisTop"

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
                return
        super().on_right_down(event) 
    
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
            elif self._isNearTopOfYAxis(event):
                self._clickedOnTopOfAxis(event)
            elif self._isNearTopEdge(event, rec): # change in height
                self._clickedOnTopEdge(event, recIndex, rec)
                return
            elif self._isNearOrigin(event):
                self._clickedOnOrigin(event)
            else:
                continue
    
    def _getNewWidth(self,event,groupIndex: int, rectangleInGroupIndex: int, groups: list[list[ValueRectangle]], origin: ValuePoint2D):
        return (event.x - self.plotSolver.GetSpacing()*(groupIndex+1) - rectangleInGroupIndex*self.plotSolver.GetInnerSpacing() - sum([self.plotSolver.GetInnerSpacing()*(len(groups[i])-1) for i in range(0,groupIndex)]) - origin.X)//(self.dragIndex+1)

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
            newWidth = self._getNewWidth(event,groupIndex, rectangleInGroupIndex, groups, origin)
            if newWidth > 10:
                self.plotSolver.ChangeWidth(newWidth)

        elif self.dragEdge == "axisTop":  
            newHeight = self.canvasHeight - event.y - origin.Y
            if newHeight > 10:
                self.plotSolver.ChangeAxisHeight(newHeight)


        elif self.dragEdge == "top":
  
            newHeight = self.canvasHeight - event.y - origin.Y
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
            elif self._isNearTopOfYAxis(event):
                self.canvas.config(cursor="sb_v_double_arrow")
                return
        super().check_cursor(event)

    def _drawRectanglesPNG(self, draw: ImageDraw):
        rectangles = self.plotSolver.GetRectangleDataAsList()
        origin = self.plotSolver.GetOrigin()
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


    def _makePNG(self, name: str):
        rectangles = self.plotSolver.GetRectangleDataAsList()
        img = Image.new("RGB", (self.canvasWidth, self.canvasHeight), color="white")
        draw = ImageDraw.Draw(img)
        self._drawRectanglesPNG(draw)
        self._drawAxesPNG(draw, self.plotSolver.GetAxisHeight(), rectangles[-1].rightTop.X, self.plotSolver.GetOrigin())
        self._writePlotTitlePNG(draw)
        img.save(f"{name}.png")


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

class HistogramCanvas(BarChartCanvas):
    def __init__(self, initialValues: list[list[float,float,float]], initialWidth: int, initialPadding: int, canvasWidth: int, canvasHeight: int, graphTitle: str = "",xCoordinate: int = 50, yCoordinate: int = 30, xAxisLabel : str = "", yAxisLabel : str = ""):
        
        PlotCanvas.__init__(self,canvasWidth,canvasHeight,graphTitle, xAxisLabel, yAxisLabel)

        self.realValues = []
        
        # rescaling of input data
        self.scaleFactor = 1

        self.intervals : list[list[float]]= []
        histogramGroup : list[float] = []
        for value in initialValues:
            self.intervals.append([value[0],value[1]])
            histogramGroup.append(value[2])
        self.realValues.append(histogramGroup)
        

        self._createTranslationTable(self.realValues)
        self._setScaleFactor()

        self.intervalScales = [self._createIntervalScales(self.intervals)]

        self.plotSolver = self._createSolver(initialWidth, initialPadding, 0, xCoordinate, yCoordinate, None, self.intervalScales)
        self.plotSolver.SetIntervalValues(self.intervals)
        self.plotSolver.Update()

        # Fields for event register
        PlotCanvas._setEventRegistersLeftButton(self)
        PlotCanvas._setEventRegistersRightButton(self)

    def _createIntervalScales(self,intervals : list[list[float]]):
        intervalLengths : list[float] = [interval[1]-interval[0] for interval in intervals]
        minimum = min([length for length in intervalLengths if length > 0], default=1)
        scales = [length/minimum for length in intervalLengths]
        return scales
    
    def _getNewWidth(self,event,groupIndex: int, rectangleInGroupIndex: int, groups: list[list[ValueRectangle]], origin: ValuePoint2D):
        return (event.x - self.plotSolver.GetSpacing()*(groupIndex+1) - rectangleInGroupIndex*self.plotSolver.GetInnerSpacing() - sum([self.plotSolver.GetInnerSpacing()*(len(groups[i])-1) for i in range(0,groupIndex)]) - origin.X)//(sum([self.intervalScales[0][i] for i in range(self.dragIndex+1)]))
        
    
    
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
            elif self._isNearTopOfYAxis(event):
                self.canvas.config(cursor="sb_v_double_arrow")
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

class ValueCandle(ValueRectangle):
    def __init__(self, openingCorner : ValuePoint2D, closingCorner : ValuePoint2D, wickBottom : ValuePoint2D, wickTop : ValuePoint2D, color = "blue", name = "", nameVisible : bool = False):
        super().__init__(openingCorner, closingCorner, color, name)
        self.openingCorner : ValuePoint2D = self.leftBottom
        self.closingCorner : ValuePoint2D = self.rightTop

        self.wickBottom : ValuePoint2D = wickBottom
        self.wickTop : ValuePoint2D = wickTop
        self.nameVisible = nameVisible
    def __str__(self):
        return f"{self.name} opening: ({self.leftBottom.X}, {self.leftBottom.Y}), closing: ({self.rightTop.X}, {self.rightTop.Y}) Wick: bottom: ({self.wickBottom.X}, {self.wickBottom.Y}) top: ({self.wickTop.X}, {self.wickTop.Y})"

class VariableCandle(VariableRectangle):
    def __init__(self, width: Variable, height: int, openingPosition: int, minPosition: int, maxPosition: int, name: str = "candle", positiveColor="green", negativeColor="red"):
        
        super().__init__(width, height, name, positiveColor if height >= 0 else negativeColor)


        self.openingCorner : VariablePoint2D = self.leftBottom
        self.closingCorner : VariablePoint2D = self.rightTop

        self.wickBottom : VariablePoint2D = VariablePoint2D(self.name+".wickBottom")
        self.wickTop : VariablePoint2D = VariablePoint2D(self.name+".wickTop")
        
        self.wickXConstraint : Constraint = ((self.wickBottom.X == (self.leftBottom.X + self.rightTop.X)/2) | "required")
        self.straightWickConstraint : Constraint = ((self.wickBottom.X == self.wickTop.X) | "required")
        
        #change when min or max changes
        self.wickBottomConstraint : Constraint = ((self.wickBottom.Y == minPosition) | "weak")
        self.wickTopConstraint : Constraint = ((self.wickTop.Y == maxPosition) | "weak")

        self.wickBottomTrueMinimumConstraints : list[Constraint] = [((self.wickBottom.Y <= self.closingCorner.Y) | "required"), ((self.wickBottom.Y <= self.openingCorner.Y) | "required")]
        self.wickTopTrueMaximumConstraints : list[Constraint] = [((self.wickTop.Y >= self.closingCorner.Y) | "required"), ((self.wickTop.Y >= self.openingCorner.Y) | "required")]

        self.openingCornerConstraint : Constraint = ((self.openingCorner.Y == openingPosition) | "weak")

        self.positiveColor = positiveColor
        self.negativeColor = negativeColor
        self.nameVisible : bool = False

    def __iter__(self):
        result = list(super().__iter__())
        result.extend([self.wickXConstraint, self.straightWickConstraint])
        result.extend([self.wickBottomConstraint, self.wickTopConstraint])
        result.append(self.openingCornerConstraint)
        return iter(result)
        
    def GetAllConstraints(self):
        return [constraint for constraint in self] + [(self.closingCorner.X >= 0) | "required", (self.openingCorner.X >= 0) | "required", (self.wickBottom.X >= 0) | "required", (self.wickTop.X >= 0) | "required"] \
                +self.wickBottomTrueMinimumConstraints+self.wickTopTrueMaximumConstraints
    
    def Value(self):
        return ValueCandle(self.openingCorner.Value(), self.closingCorner.Value(), self.wickBottom.Value(), self.wickTop.Value(), self.positiveColor if self.height.value() >= 0 else self.negativeColor, self.name, self.nameVisible)
        
    def ChangePositiveColor(self, color: str):
        self.positiveColor = color
    def ChangeNegativeColor(self, color: str):
        self.negativeColor = color
    def SwitchNameVisibility(self):
        self.nameVisible = not self.nameVisible

class VariableCandlesticChart(VariableChart):
    def __init__(self, width : int, initialOpening : list[int], initialClosing : list[int], initialMinimum : list[int], initialMaximum : list[int], spacing : int, names : list[str], xCoordinate : int = 0, yCoordinate : int = 0):
        super().__init__(width, spacing, xCoordinate, yCoordinate)

        self.candles = [VariableCandle(self.width, initialClosing[i] - initialOpening[i], initialOpening[i], initialMinimum[i], initialMaximum[i],names[i]) for i in range(len(initialOpening))]
        
        self.leftMostCandleConstriant : Constraint = (self.candles[0].openingCorner.X >= self.origin.X) | "required"

        self._createCandleSpacingConstraints()

    def _createCandleSpacingConstraints(self):
        self.candles[0].SetSpacingConstraint((self.candles[0].openingCorner.X - self.spacing == self.origin.X) | "required")
        for index in range(1, len(self.candles)):
            self.candles[index].SetSpacingConstraint((self.candles[index-1].closingCorner.X + self.spacing == self.candles[index].openingCorner.X) | "required")
    
    def Value(self):
        return [candle.Value() for candle in self.candles]

    def GetAllConstraints(self):
        result = []
        for candle in self.candles:
            result.extend(candle.GetAllConstraints())
        return result + [(self.width >= 10) | "required", (self.spacing >= 0) | "required"] \
                      + [self.widthValueConstraint, self.spacingValueConstraint] \
                      + [self.originXCoordinateConstraint,self.originYCoordinateConstraint,self.leftMostCandleConstriant]
    
    def ChangePositiveColor(self, color : Union[str,int]):
        for candle in self.candles:
            candle.positiveColor = color
    
    def ChangeNegativeColor(self, color : Union[str,int]):
        for candle in self.candles:
            candle.negativeColor = color
    
    def SwitchNameVisibility(self, index : int):
        self.candles[index].SwitchNameVisibility()

class CandlestickChartSolver:
    def __init__(self, width : int, initialOpening : list[int], initialClosing : list[int], initialMinimum : list[int], initialMaximum : list[int], spacing : int, names : list[str], xCoordinate : int = 0, yCoordinate : int = 0):
        self.solver : Solver = Solver()
        self.variableCandlestickChart : VariableCandlesticChart = VariableCandlesticChart(width,initialOpening,initialClosing,initialMinimum,initialMaximum,spacing,names,xCoordinate,yCoordinate)
        self.candleData = None

        for constraint in self.variableCandlestickChart.GetAllConstraints():
            self.solver.addConstraint(constraint)

        self.solver.addEditVariable(self.variableCandlestickChart.width, "strong")
        self.solver.addEditVariable(self.variableCandlestickChart.spacing, "strong")
        self.solver.addEditVariable(self.variableCandlestickChart.origin.X, "strong")
        self.solver.addEditVariable(self.variableCandlestickChart.origin.Y, "strong")

        for index, candle in enumerate(self.variableCandlestickChart.candles):
            self.solver.addEditVariable(candle.height, "strong")
            self.solver.addEditVariable(candle.wickBottom.Y, "strong")
            self.solver.addEditVariable(candle.wickTop.Y, "strong")
            self.solver.addEditVariable(candle.openingCorner.Y, "strong")

            self.solver.suggestValue(candle.wickBottom.Y, initialMinimum[index])
            self.solver.suggestValue(candle.wickTop.Y, initialMaximum[index])
            self.solver.suggestValue(candle.openingCorner.Y, initialOpening[index])

        self.solver.addEditVariable(self.variableCandlestickChart.yAxisHeight, "strong")
        self.solver.suggestValue(self.variableCandlestickChart.yAxisHeight, max(initialMaximum))
        
        
        self.Solve()
    
    def ChangeWidth(self, width : int):
        self.solver.suggestValue(self.variableCandlestickChart.width, width)
        self.Solve()
    
    def ChangeSpacing(self, spacing : int):
        self.solver.suggestValue(self.variableCandlestickChart.spacing, spacing)
        self.Solve()
    
    def ChangeHeight(self, candleIndex : int, height : int):
        self.solver.suggestValue(self.variableCandlestickChart.candles[candleIndex].height, height)
        self.Solve()
    
    def ChangeMaximum(self, candleIndex : int, yValue : int):
        topOfCandle = max(self.variableCandlestickChart.candles[candleIndex].openingCorner.Y.value(), self.variableCandlestickChart.candles[candleIndex].closingCorner.Y.value())
        self.solver.suggestValue(self.variableCandlestickChart.candles[candleIndex].wickTop.Y, yValue if (yValue >= topOfCandle) else topOfCandle)
        self.Solve()

    def ChangeMinimum(self, candleIndex : int, yValue : int):
        self.solver.suggestValue(self.variableCandlestickChart.candles[candleIndex].wickBottom.Y, yValue)
        self.Solve()

    def ChangeOpening(self, candleIndex: int, yValue : int):
        self.solver.suggestValue(self.variableCandlestickChart.candles[candleIndex].openingCorner.Y, yValue)
        self.Solve()
    
    def ChangeOrigin(self, newX: int, newY: int):
        self.solver.suggestValue(self.variableCandlestickChart.origin.X, newX)
        self.solver.suggestValue(self.variableCandlestickChart.origin.Y, newY)
        self.Solve()
    
    def ChangeAxisHeight(self, newHeight : int):
        self.solver.suggestValue(self.variableCandlestickChart.yAxisHeight, newHeight)
        self.Solve()
    
    def SwitchNameVisibility(self, index : int):
        self.variableCandlestickChart.SwitchNameVisibility(index)
        self.Update()

    def Solve(self):
        self.solver.updateVariables()
        self.Update()

    def Update(self):
        self.candleData = self.variableCandlestickChart.Value()
        pass
    
    def ChangePositiveColor(self, color : Union[str, int]):
        self.variableCandlestickChart.ChangePositiveColor(color)
        self.Update()

    def ChangeNegativeColor(self, color : Union[str, int]):
        self.variableCandlestickChart.ChangeNegativeColor(color)
        self.Update()
    
    def ChangeName(self, candleIndex : int, name : str):
        self.variableCandlestickChart.candles[candleIndex].name = name
        self.Update()

    def GetCandleData(self):
        return self.candleData
    
    def GetOrigin(self):
        return ValuePoint2D(self.variableCandlestickChart.origin.X.value(),self.variableCandlestickChart.origin.Y.value())

    def GetSpacing(self):
        return self.variableCandlestickChart.spacing.value()
    
    def GetWidth(self):
        return self.variableCandlestickChart.width.value()
    
    def GetAxisHeight(self):
        return self.variableCandlestickChart.yAxisHeight.value()
    
    def GetName(self, candleIndex : int):
        return self.variableCandlestickChart.candles[candleIndex].name

class CandlestickChartCanvas(PlotCanvas):
    def __init__(self, width : int, initialOpening : list[float], initialClosing : list[float], initialMinimum : list[float], initialMaximum : list[float], spacing : int, canvasWidth: int, canvasHeight: int, names : list[str], xAxisValue : float = 0, graphTitle: str = "", xCoordinate : int = 50, yCoordinate : int = 30, xAxisLabel : str = "", yAxisLabel : str = ""):
        
        super().__init__(canvasWidth, canvasHeight, graphTitle, xAxisLabel, yAxisLabel)
        self.scaleFactor = 1
        self.realOpeningValues = initialOpening
        self.realClosingValues = initialClosing
        self.realMaximumValues = initialMaximum
        self.realMinimumValues = initialMinimum
        self.xAxisValue : float = xAxisValue

        self._setScaleFactor()

        scaledXAxis = self.xAxisValue*self.scaleFactor
        self.plotSolver : CandlestickChartSolver = CandlestickChartSolver(width,[value*self.scaleFactor-scaledXAxis  for value in initialOpening], [value*self.scaleFactor-scaledXAxis for value in initialClosing],[value*self.scaleFactor-scaledXAxis for value in initialMinimum],[value*self.scaleFactor-scaledXAxis for value in initialMaximum],spacing,names,xCoordinate,yCoordinate)

    def _setScaleFactor(self):
        realValues = np.abs(self.realMinimumValues) + np.abs(self.realMaximumValues) + np.abs(self.realClosingValues) + np.abs(self.realOpeningValues)
        maxValue = max(realValues,default=1) 
        if not (self.canvasHeight*0.3 <= maxValue <= self.canvasHeight*0.8):
            self.scaleFactor = self.canvasHeight*0.8/maxValue
    
    def _setRightClickMenu(self, frame: tk.Frame):
        self.menu = tk.Menu(frame, tearoff=0)
        self.menu.add_command(label="Change positive color", command=self._changePositiveColor)
        self.menu.add_command(label="Change negative color", command=self._changeNegativeColor)
        self.menu.add_command(label="Change name", command=self._changeName)
        self.menu.add_command(label="Switch name visibility", command=self._switchNameVisibility)

    def View(self):        
        # UI features initialisation
        super().View()

        self._setRightClickMenu(self.frame)

        self._drawPlot()
        self._writeValues() 

        # binding methods to mouse events
        super()._UIRun()

    def _writeValues(self):
        return

    def _drawCandles(self): 
        
        origin = self.plotSolver.GetOrigin()
        candles = self.plotSolver.GetCandleData()
        for candle in candles:
            leftBottomX, leftBottomY = None, None
            rightTopX, rightTopY = None, None

            if candle.closingCorner.Y - candle.openingCorner.Y >= 0:
                leftBottomX, leftBottomY = candle.openingCorner.X, candle.openingCorner.Y
                rightTopX, rightTopY = candle.closingCorner.X, candle.closingCorner.Y
            else:
                leftBottomX, leftBottomY = candle.openingCorner.X, candle.closingCorner.Y
                rightTopX, rightTopY = candle.closingCorner.X, candle.openingCorner.Y


            x1 = leftBottomX
            y1 = self.canvasHeight - (leftBottomY + origin.Y)
            
            x2 = rightTopX
            y2 = self.canvasHeight - (rightTopY + origin.Y)

            minX = candle.wickBottom.X
            minY = self.canvasHeight - (candle.wickBottom.Y + origin.Y)

            maxX = candle.wickTop.X
            maxY = self.canvasHeight - (candle.wickTop.Y + origin.Y)

            self.canvas.create_rectangle(x1,y2,x2,y1, fill=candle.color, outline="black")
            self.canvas.create_line(minX, minY, maxX, maxY, fill=candle.color)
            if candle.nameVisible: 
                self.canvas.create_text(candle.wickBottom.X ,self.canvasHeight - origin.Y + 10, text=candle.name)

    def _writePlotTitle(self):  
        self.canvas.create_text(self.canvasWidth / 2, 20,text=self.title,font=("Arial", 16, "bold"))
    
    @staticmethod
    def _ceilToNearestTen(number: int):
        return ((number // 10) + 1) * 10

    @staticmethod
    def _divideInterval(low: int, high: int, parts: int):
        if parts < 2:
            return [low, high]

        step = (high - low) // (parts - 1)
        return [low + i * step for i in range(parts)]

    
    def _drawPlot(self):
        """
        Draws rectangles and axes on the plot
        """
        self.canvas.delete("all")
        self._writePlotTitle()
        self._drawCandles()

        origin = self.plotSolver.GetOrigin()

        candles = self.plotSolver.GetCandleData()
        
        lowestWickHeight = min([candle.wickBottom.Y for candle in candles])
        self._drawAxes(self.plotSolver.GetAxisHeight(), candles[-1].rightTop.X, origin, min(0, lowestWickHeight)) 
    
    def _writeValues(self):
        """
        Displays all data for the user and highlights which data is being edited
        """
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        valueEdited = self.dragEdge in ["opening", "closing", "maximum", "minimum"]
        candles = self.plotSolver.GetCandleData()

        for i in range(len(candles)-1, -1, -1):
            candle = candles[i]
            openingValue = candle.openingCorner.Y/self.scaleFactor + self.xAxisValue
            closingValue = candle.closingCorner.Y/self.scaleFactor + self.xAxisValue
            maximumValue = candle.wickTop.Y/self.scaleFactor + self.xAxisValue
            minimumValue = candle.wickBottom.Y/self.scaleFactor + self.xAxisValue
            
            string = f"{candle.name}:\n\topening = {openingValue:.4f},\n\tclosing = {closingValue:.4f},\n\tmin = {minimumValue:.4f},\n\tmax = {maximumValue:.4f}\n\n"
            if valueEdited and i == self.dragIndex:
                self.dataWindow.insert("1.0",f"{string}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"{string}\n")
        self.dataWindow.config(state="disabled")
        
    
    def _isNearClosingEdge(self, event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        closingY = self.canvasHeight - (candle.closingCorner.Y + origin.Y)
        return self._isNear(closingY, event.y) and candle.openingCorner.X <= event.x <= candle.closingCorner.X

    def _isNearOpeningEdge(self, event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        openingY = self.canvasHeight - (candle.openingCorner.Y + origin.Y)
        return self._isNear(openingY, event.y) and candle.openingCorner.X <= event.x <= candle.closingCorner.X

    def _isNearLeftEdge(self, event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        candleBottomY, candleTopY = self.canvasHeight - (min(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y), self.canvasHeight - (max(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y)
        return self._isNear(event.x, candle.openingCorner.X) and candleTopY <= event.y <= candleBottomY
        pass

    def _isNearRightEdge(self, event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        candleBottomY, candleTopY = self.canvasHeight - (min(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y), self.canvasHeight - (max(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y)
        return self._isNear(event.x, candle.closingCorner.X) and candleTopY <= event.y <= candleBottomY
      

    def _isNearMaximum(self, event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        maxY = self.canvasHeight - (candle.wickTop.Y + origin.Y)
        return self._isNear(maxY, event.y) and self._isNear(candle.wickTop.X, event.x)
        

    def _isNearMinimum(self, event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        minY = self.canvasHeight - (candle.wickBottom.Y + origin.Y)
        return self._isNear(minY, event.y) and self._isNear(candle.wickBottom.X, event.x)
    
    def _isNearOrigin(self, event):
        origin = self.plotSolver.GetOrigin()
        return self._isNear(event.x, origin.X) and self._isNear(event.y, self.canvasHeight - origin.Y)
    
    def _isNearTopOfYAxis(self,event):
        topNormalized = self.canvasHeight - self.plotSolver.GetAxisHeight() - self.plotSolver.GetOrigin().Y
        return self._isNear(event.y, topNormalized, 10) and self._isNear(event.x, self.plotSolver.GetOrigin().X, 10)
    
    def _isInsideOfCandle(self,event, candle : ValueCandle):
        originY = self.plotSolver.GetOrigin().Y
        xCoordinateOK = candle.leftBottom.X <= event.x <= candle.rightTop.X
        bottomY = candle.openingCorner.Y if candle.openingCorner.Y <= candle.closingCorner.Y else candle.closingCorner.Y
        topY = candle.closingCorner.Y if candle.openingCorner.Y <= candle.closingCorner.Y else candle.openingCorner.Y
        topY, bottomY = self.canvasHeight - bottomY - originY, self.canvasHeight - topY - originY
        yCoordinateOK = bottomY <= event.y <= topY
        return yCoordinateOK and xCoordinateOK


    
    def _clickedOnRightEdge(self, event, candleIndex: int, candle: ValueCandle):
        """
        Registers that the user clicked on a right edge of some rectangle
        """
        self.dragEdge = 'right'
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = candleIndex
        
        self.originalCoordinates = candle.rightTop
        self.rightEdgeCursorOffset = event.x - candle.rightTop.X
        self.originalLeftX = candle.leftBottom.X
    
    def _clickedOnLeftEdge(self, event, candleIndex: int, candle: ValueCandle): 
        """
        Registers that the user clicked on a left edge of some rectangle
        """
        self.dragEdge = "left"
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = candleIndex
        
        self.originalLeftX = candle.leftBottom.X
        self.originalSpacing = self.plotSolver.GetSpacing()
    
    def _clickedOnClosingEdge(self, event, candleIndex: int, candle: ValueCandle):
        """
        Registers that the user clicked on a top edge of some rectangle
        """
        self.dragEdge = "closing"
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = candleIndex
        self.originalHeight = candle.closingCorner.Y - candle.openingCorner.Y
    
    def _clickedOnOpeningEdge(self, event, candleIndex : int, candle : ValueCandle):
        self.dragEdge = "opening"
        self.dragIndex = candleIndex 
    
    def _clickedOnMaximum(self, event, candleIndex : int, candle : ValueCandle):
        self.dragEdge = "maximum"
        self.dragIndex = candleIndex

    def _clickedOnMinimum(self, event, candleIndex : int, candle : ValueCandle):
        self.dragEdge = "minimum"
        self.dragIndex = candleIndex
    
    def _clickedOnOrigin(self, event):
        self.dragEdge = "origin"
    
    def _clickedOnTopOfAxis(self, event):
        self.dragEdge = "axisTop"
    

    def _changePositiveColor(self):
        color = colorchooser.askcolor(title="Choose different color")
        if color[1] == None:
            return
        self.plotSolver.ChangePositiveColor(color[1])
        self._drawPlot()
    
    def _changeNegativeColor(self):
        color = colorchooser.askcolor(title="Choose different color")
        if color[1] == None:
            return
        self.plotSolver.ChangeNegativeColor(color[1])
        self._drawPlot()

    def _changeName(self):
        currentName = self.plotSolver.GetName(self.rectangleIndexToChange)
        newName = simpledialog.askstring("Change name", "New name:", initialvalue=currentName)
        if newName == None:
            return
        self.plotSolver.ChangeName(self.rectangleIndexToChange, newName)
        self._drawPlot()
        self._writeValues()
        pass

    def _switchNameVisibility(self):
        self.plotSolver.SwitchNameVisibility(self.rectangleIndexToChange)
        self._drawPlot()

    def on_right_down(self, event):
            for index, candle in enumerate(self.plotSolver.GetCandleData()):
                if self._isInsideOfCandle(event, candle):
                    self.rectangleIndexToChange = index
                    self.menu.post(event.x_root, event.y_root)
                    return
            super().on_right_down(event)
    


    def on_left_down(self, event):
        for index, candle in enumerate(self.plotSolver.GetCandleData()):
            if self._isNearMaximum(event, candle):
                print(f"maximum {index}")
                self._clickedOnMaximum(event, index, candle)
                break
            elif self._isNearMinimum(event, candle):
                print(f"minimum {index}")
                self._clickedOnMinimum(event, index, candle)
                break
            
            elif self._isNearTopOfYAxis(event):
                self._clickedOnTopOfAxis(event)
                break

            elif self._isNearClosingEdge(event, candle):
                print(f"closing edge {index}")
                self._clickedOnClosingEdge(event, index, candle)
                break      
            elif self._isNearOpeningEdge(event, candle):
                print(f"opening edge {index}")
                self._clickedOnOpeningEdge(event, index, candle)
                break
            elif self._isNearLeftEdge(event, candle):
                print(f"left edge {index}")
                self._clickedOnLeftEdge(event,index, candle)
                break
            elif self._isNearRightEdge(event, candle):
                print(f"right edge {index}")
                self._clickedOnRightEdge(event,index, candle)
                break
            
            elif self._isNearOrigin(event):
                self._clickedOnOrigin(event)


    def on_mouse_move(self, event):
        if self.dragEdge is None:
            return
        
        origin = self.plotSolver.GetOrigin()

        if self.dragEdge == "right":
            newWidth = (event.x - (self.dragIndex+1)*self.plotSolver.GetSpacing() - origin.X)/(self.dragIndex+1)
            if newWidth >= 5:
                self.plotSolver.ChangeWidth(newWidth)
            pass
        
        elif self.dragEdge == "left":
            newSpacing = (event.x - self.dragIndex*self.plotSolver.GetWidth() - origin.X)/(self.dragIndex+1)
            if newSpacing >=0:
                self.plotSolver.ChangeSpacing(newSpacing)
            pass

        elif self.dragEdge == "closing":
            dy = self.dragStart.Y - event.y  
            newHeight = self.originalHeight + dy
            self.plotSolver.ChangeHeight(self.dragIndex, newHeight)
        
        elif self.dragEdge == "opening":
            self.plotSolver.ChangeOpening(self.dragIndex, self.canvasHeight - event.y - origin.Y)
        
        elif self.dragEdge == "minimum":
            self.plotSolver.ChangeMinimum(self.dragIndex, self.canvasHeight - event.y - origin.Y)
        
        elif self.dragEdge == "maximum":
            self.plotSolver.ChangeMaximum(self.dragIndex, self.canvasHeight - event.y - origin.Y)
        
        elif self.dragEdge == "origin": #done
            self.plotSolver.ChangeOrigin(event.x, self.canvasHeight - event.y)
        
        elif self.dragEdge == "axisTop":  
            newHeight = self.canvasHeight - event.y - origin.Y
            if newHeight > 10:
                self.plotSolver.ChangeAxisHeight(newHeight)


        self._drawPlot()
        self._writeValues() 


    def on_left_up(self, event):
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
        for idx, candle in enumerate(self.plotSolver.GetCandleData()):
            if self._isNearMaximum(event,candle):
                self.canvas.config(cursor="cross")
                return
            elif self._isNearMinimum(event,candle):
                self.canvas.config(cursor="cross")
                return
            elif self._isNearLeftEdge(event, candle):
                self.canvas.config(cursor="hand2")
                return
            elif self._isNearRightEdge(event, candle):
                self.canvas.config(cursor="sb_h_double_arrow")
                return
            elif self._isNearClosingEdge(event, candle):
                self.canvas.config(cursor="sb_v_double_arrow")
                return
            elif self._isNearOpeningEdge(event, candle):
                self.canvas.config(cursor="sb_v_double_arrow")
                return
            elif self._isNearOrigin(event):
                self.canvas.config(cursor="fleur")
                return
            elif self._isNearTopOfYAxis(event):
                self.canvas.config(cursor="sb_v_double_arrow")
                return

        self.canvas.config(cursor="arrow")

    def _drawCandlesPNG(self, draw : ImageDraw):
        candles = self.plotSolver.GetCandleData()
        origin = self.plotSolver.GetOrigin()
        for candle in candles:
            leftBottomX, leftBottomY = None, None
            rightTopX, rightTopY = None, None

            if candle.closingCorner.Y - candle.openingCorner.Y >= 0:
                leftBottomX, leftBottomY = candle.openingCorner.X, candle.openingCorner.Y
                rightTopX, rightTopY = candle.closingCorner.X, candle.closingCorner.Y
            else:
                leftBottomX, leftBottomY = candle.openingCorner.X, candle.closingCorner.Y
                rightTopX, rightTopY = candle.closingCorner.X, candle.openingCorner.Y


            x1 = leftBottomX
            y1 = self.canvasHeight - leftBottomY - origin.Y
            
            x2 = rightTopX
            y2 = self.canvasHeight - rightTopY - origin.Y

            draw.rectangle((x1,y2,x2,y1), fill=candle.color, outline="black")

            xMax, yMax = candle.wickTop.X, self.canvasHeight - candle.wickTop.Y - origin.Y
            xMin, yMin = candle.wickBottom.X, self.canvasHeight - candle.wickBottom.Y - origin.Y
            draw.line((xMax,yMax,xMin,yMin), fill=candle.color, width=1) 

            if candle.nameVisible:
                font = ImageFont.load_default()
                text = candle.name

                # get text size
                bbox = font.getbbox(text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # text position
                x_center = (x1 + x2) / 2
                y_text = self.canvasHeight - origin.Y + 10

                draw.text(
                    (x_center - text_width / 2, y_text - text_height/2),
                    text,
                    fill="black",
                    font=font)

    def _makePNG(self, name: str):
        candles = self.plotSolver.GetCandleData()
        lowestWickHeight = min([candle.wickBottom.Y for candle in candles])
        img = Image.new("RGB", (self.canvasWidth, self.canvasHeight), color="white")
        draw = ImageDraw.Draw(img)
        self._drawCandlesPNG(draw)
        self._drawAxesPNG(draw, self.plotSolver.GetAxisHeight(), candles[-1].rightTop.X, self.plotSolver.GetOrigin(), min(0, lowestWickHeight))
        self._writePlotTitlePNG(draw)
        img.save(f"{name}.png")
    
    def _saveDataAsCSV(self, file: str):
        with open(file,"w") as output:
            candles = self.plotSolver.GetCandleData()
            for candle in candles:
                output.write(f"{candle.name},{candle.openingCorner.Y/self.scaleFactor + self.xAxisValue},{candle.closingCorner.Y/self.scaleFactor + self.xAxisValue},{candle.wickBottom.Y/self.scaleFactor + self.xAxisValue},{candle.wickTop.Y/self.scaleFactor + self.xAxisValue}")
                output.write("\n")





