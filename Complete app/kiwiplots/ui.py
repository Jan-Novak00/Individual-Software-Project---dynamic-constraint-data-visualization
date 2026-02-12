from .plotelement import VariableRectangleGroup, VariablePoint2D, VariableCandle, ValueRectangle, ValuePoint2D, ValueCandle # type: ignore
from .variableplot import VariableBarChart, VariableCandlesticChart, VariableChart # type: ignore
from .solvers import BarChartSolver, CandlestickChartSolver, ChartSolver # type: ignore
from kiwisolver import Variable, Constraint, Solver # type: ignore
from PIL import Image, ImageDraw, ImageFont # type: ignore
import numpy as np # type: ignore
from typing import Union # type: ignore
import tkinter as tk # type: ignore
from tkinter import simpledialog # type: ignore
from tkinter import colorchooser # type: ignore
from tkinter import font # type: ignore
import os # type: ignore
from abc import ABC, abstractmethod # type: ignore

# Note: UI Core should be created by the app after main maenu screen via dependency injection.

# Search for: "move to superclass", "ToDo"

def _isNear(val1: float, val2: float, tolerance : float=5)->bool:
    """
    Returns True, if two values are near to each other with given tolerance
    """
    return abs(val1 - val2) < tolerance



"""
Abstract class. Contains logic to show current data values represented by a graph.
"""
class DataViewer(ABC):
    def __init__(self, textWindow : tk.Text):
        self.dataWindow : tk.Text = textWindow

    def write(self, data)->None: # type: ignore
        raise NotImplementedError("Method DataViewr.write must be declared in subclass")

"""
Abstract class. Contains logic to draw given plot element to canvas (tk.canvas).
Implementations depend on given type of plot element. 
"""
class CanvasDrawer(ABC):
    def __init__(self, canvas : tk.Canvas, scaleFactor : float = 1, xAxisLabel : str = "", yAxisLabel : str = "") -> None:
        self.canvas : tk.Canvas = canvas
        self.scaleFactor: float = scaleFactor # used to calculate values on axies    
        self.xAxisLabel : str = xAxisLabel    # label of x axis
        self.yAxisLabel : str = yAxisLabel    # label of y axis
        self.xAxisValue = 0                   # which y value does x axis represent (usualy 0, in candlestic chart it can be different)
    
    def draw(self, solver : ChartSolver)->None:
        """
        Draw data on the canvas.
        """
        raise NotImplementedError("Method CanvasDrawer.draw must be declared in subclass")
    @staticmethod
    def _ceilToNearestTen(number: float):
        return ((number // 10) + 1) * 10
    @staticmethod
    def _floorToNearestTen(number: float):
        return ((number // 10) - 1) * 10

    @staticmethod
    def _divideInterval(low: float, high: float, parts: int):
        if parts < 2:
            return [low, high]

        step = (high - low) // (parts - 1)
        return [low + i * step for i in range(parts)]


"""
Abstract class. Handles user interaction with the graph on tk.Canvas.
Implementations are based on type of graph user is working with.
Inicialized via dependency injection.
"""
class CanvasHandler(ABC):
    def __init__(self) -> None:
        self.canvas : tk.Canvas = None # type: ignore
        self.drawer : CanvasDrawer = None  # type: ignore
        self.dataViewer : DataViewer = None # type: ignore
        self._setEventRegistersLeftButton()
        self._setEventRegistersRightButton()
    
    def UpdateUI(self):
        self._updateCanvas()
        self._updateDataView()
    
    def _setEventRegistersLeftButton(self):
        """
        Variables which register information about events regarding the left mouse button
        """
        self.dragEdge = None                # which edge is being dragged
        self.dragStart = ValuePoint2D(0,0)  # where draging started
        self.dragIndex = None               # index of plot element which is being dragged
        self.originalLeftX = None           # 
        self.originalSpacing = None         #
        self.rightEdgeCursorOffset = None   #
        self.originalHeight = None          #
    
    def _setEventRegistersRightButton(self):
        """
        Variables which register information about events regarding the right mouse button
        """
        self.rectangleIndexToChange = None
    
    def _updateCanvas(self):
        self.drawer.draw(self.solver) # type: ignore
    
    def _updateDataView(self):
        self.dataViewer.write(self.solver.Value()) # type: ignore
    
    def on_left_down(self, event: tk.Event)->None:
        raise NotImplementedError("Method CanvasHandler.on_left_down must be declared in subclass")
    
    def on_right_down(self, event: tk.Event)->None:
        raise NotImplementedError("Method CanvasHandler.on_right_down must be declared in subclass")

    def on_mouse_move(self,event: tk.Event)->None:
        raise NotImplementedError("Method CanvasHandler.on_mouse_move must be declared in subclass")
    
    def on_left_up(self,event: tk.Event)->None:
        raise NotImplementedError("Method CanvasHandler.on_left_up must be declared in subclass")
    
    def on_right_up(self,event: tk.Event)->None:
        raise NotImplementedError("Method CanvasHandler.on_right_up must be declared in subclass")
    
    def check_cursor(self, event: tk.Event)->None:
        raise NotImplementedError("Method CanvasHandler.check_cursor must be declared in subclass")
    
    def inicializeDataView(self, textWindow: tk.Text)->None:
        raise NotImplementedError("Method CanvasHandler.inicializeDataView must be declared in subclass")
    
    def inicializeCanvas(self, canvas: tk.Canvas)->None:
        raise NotImplementedError("Method CanvasHandler.inicializeCanvas must be declared in subclass")
    

"""
Abstract class. Contains logic to create image of the graph.
"""
class PictureDrawer(ABC):
    
    def draw(self, solver: ChartSolver):
        raise NotImplementedError("Method PictureDrawer.draw must be declared in subclass")

"""
Abstract class. Contains logic to create text output of the data.
"""
class DataWriter(ABC):

    def write(self, solver: ChartSolver):
        raise NotImplementedError("Method DataWriter.write must be declared in subclass")
    pass

"""
Handles communication between UI features.
"""
class UICore:
    def __init__(self, solver : ChartSolver, canvasHandler : CanvasHandler, pictureDrawer : PictureDrawer, dataWriter: DataWriter, plotWidth: int, plotHeight: int):
        self.solver : ChartSolver = solver
        self.canvasHandler : CanvasHandler = canvasHandler
        self.pictureDrawer : PictureDrawer = pictureDrawer
        self.dataWriter : DataWriter = dataWriter
        self.plotWidth = plotWidth
        self.plotHeight = plotHeight


    def inicializeUIElements(self):
        """
        Shows the window, inicializes UI
        """
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.canvas = tk.Canvas(self.frame, width=self.plotWidth, height=self.plotHeight, bg="white")
        self.canvas.pack()

        self.savePictureButton = tk.Button(self.frame, text="Save as png", command=self.on_savePictureButton_click)
        self.savePictureButton.pack(pady=5)

        self.dataWindow = tk.Text(self.frame, height=20, width=40)
        self.dataWindow.pack()

        self.saveDataButton = tk.Button(self.frame, text="Save data as csv", command=self.on_saveDataButton_click)
        self.saveDataButton.pack(pady=5)

        self.defaultMenu = tk.Menu(self.frame,tearoff=0)
        self.defaultMenu.add_command(label = "Change title", command=self._changeTitle)

    def inicializeHandlers(self):
        self.canvasHandler.inicializeCanvas(self.canvas)
        self.canvasHandler.inicializeDataView(self.dataWindow)
    
    def _changeTitle(self):
        print("Title change not yet implemented")
    
    def on_saveDataButton_click(self):
        self.dataWriter.write(self.solver)
    
    def on_savePictureButton_click(self):
        self.pictureDrawer.draw(self.solver)
    
    def View(self):
        self.inicializeUIElements()
        self.inicializeHandlers()

        #self._setRightClickMenu(self.frame)  ToDo - set right click menu

        self.canvasHandler.UpdateUI() #initial draw
        self._UIRun()
    
    def _UIRun(self):
        self.canvas.bind("<Button-1>", self.canvasHandler.on_left_down) # type: ignore
        self.canvas.bind("<B1-Motion>", self.canvasHandler.on_mouse_move) # type: ignore
        self.canvas.bind("<ButtonRelease-1>", self.canvasHandler.on_left_up) # type: ignore
        self.canvas.bind("<Motion>", self.canvasHandler.check_cursor) # type: ignore
        self.canvas.bind("<Button-3>", self.canvasHandler.on_right_down) # type: ignore
        self.canvas.bind("<ButtonRelease-3>", self.canvasHandler.on_right_up) # type: ignore
        self.root.mainloop()


########################################################################################

class CandlesticDataViewer(DataViewer):
    def __init__(self, textWindow: tk.Text):
        super().__init__(textWindow)


class CandlesticCanvasDrawer(CanvasDrawer):
    def __init__(self, canvas : tk.Canvas, scaleFactor : float = 1, xAxisValue : float = 0, xAxisLabel : str = "", yAxisLabel : str = ""):
        super().__init__(canvas,scaleFactor,xAxisLabel,yAxisLabel)
        self.canvasHeight = self.canvas.winfo_height()
        self.xAxisValue = xAxisValue
    
    def _drawCandles(self, solver: CandlestickChartSolver): 
        
        origin = solver.GetOrigin()
        candles = solver.GetCandleData()
        for candle in candles: # type: ignore
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
        print("Write title todo")
        return
        self.canvas.create_text(self.canvasWidth / 2, 20,text=self.title,font=("Arial", 16, "bold")) # problem is with self.title
    
    def _drawAxes(self, maximumValue: float, leftCornerXAxis: int, origin : ValuePoint2D, minimumValue : int = 0):   # move to superclass
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
    
    def draw(self, solver : CandlestickChartSolver)->None:
        """
        Draws candles and axes on the plot
        """
        self.canvas.delete("all")
        self._writePlotTitle()
        self._drawCandles(solver)

        origin = solver.GetOrigin()
        candles = solver.GetCandleData()
        
        lowestWickHeight = min([candle.wickBottom.Y for candle in candles]) # type: ignore
        self._drawAxes(solver.GetAxisHeight(), candles[-1].rightTop.X, origin, min(0, lowestWickHeight))  # type: ignore
        

class CandlesticCanvasHandler(CanvasHandler):

    ###################
    # Inicializastion #
    ###################

    def __init__(self, solver: CandlestickChartSolver) -> None:
        super().__init__()
        self.plotSolver : CandlestickChartSolver = solver 
        self.canvasHeight : int = None # type: ignore
        
    
    def inicializeDataView(self, textWindow: tk.Text):
        self.dataViewer = CandlesticDataViewer(textWindow)
    
    def inicializeCanvas(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.canvasHeight = canvas.winfo_height()
        self.drawer = CandlesticCanvasDrawer(canvas) #ToDo
    
    ##################################
    # Predicates for locating events #
    ##################################
    
    def _isNearClosingEdge(self, event: tk.Event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        closingY = self.canvasHeight - (candle.closingCorner.Y + origin.Y)
        return _isNear(closingY, event.y) and candle.openingCorner.X <= event.x <= candle.closingCorner.X

    def _isNearOpeningEdge(self, event: tk.Event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        openingY = self.canvasHeight - (candle.openingCorner.Y + origin.Y)
        return _isNear(openingY, event.y) and candle.openingCorner.X <= event.x <= candle.closingCorner.X

    def _isNearLeftEdge(self, event: tk.Event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        candleBottomY, candleTopY = self.canvasHeight - (min(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y), self.canvasHeight - (max(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y)
        return _isNear(event.x, candle.openingCorner.X) and candleTopY <= event.y <= candleBottomY
        pass

    def _isNearRightEdge(self, event: tk.Event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        candleBottomY, candleTopY = self.canvasHeight - (min(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y), self.canvasHeight - (max(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y)
        return _isNear(event.x, candle.closingCorner.X) and candleTopY <= event.y <= candleBottomY
      

    def _isNearMaximum(self, event: tk.Event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        maxY = self.canvasHeight - (candle.wickTop.Y + origin.Y)
        return _isNear(maxY, event.y) and _isNear(candle.wickTop.X, event.x)
        

    def _isNearMinimum(self, event: tk.Event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        minY = self.canvasHeight - (candle.wickBottom.Y + origin.Y)
        return _isNear(minY, event.y) and _isNear(candle.wickBottom.X, event.x)
    
    def _isNearOrigin(self, event: tk.Event):
        origin = self.plotSolver.GetOrigin()
        return _isNear(event.x, origin.X) and _isNear(event.y, self.canvasHeight - origin.Y)
    
    def _isNearTopOfYAxis(self,event: tk.Event):
        topNormalized = self.canvasHeight - self.plotSolver.GetAxisHeight() - self.plotSolver.GetOrigin().Y
        return _isNear(event.y, topNormalized, 10) and _isNear(event.x, self.plotSolver.GetOrigin().X, 10)
    
    def _isInsideOfCandle(self,event: tk.Event, candle : ValueCandle):
        originY = self.plotSolver.GetOrigin().Y
        xCoordinateOK = candle.leftBottom.X <= event.x <= candle.rightTop.X
        bottomY = candle.openingCorner.Y if candle.openingCorner.Y <= candle.closingCorner.Y else candle.closingCorner.Y
        topY = candle.closingCorner.Y if candle.openingCorner.Y <= candle.closingCorner.Y else candle.openingCorner.Y
        topY, bottomY = self.canvasHeight - bottomY - originY, self.canvasHeight - topY - originY
        yCoordinateOK = bottomY <= event.y <= topY
        return yCoordinateOK and xCoordinateOK

    ########################
    # Left click handeling #
    ########################
    
    def _clickedOnMaximum(self, event: tk.Event, candleIndex : int, candle : ValueCandle):
        self.dragEdge = "maximum"
        self.dragIndex = candleIndex

    def _clickedOnMinimum(self, event: tk.Event, candleIndex : int, candle : ValueCandle):
        self.dragEdge = "minimum"
        self.dragIndex = candleIndex
    
    def _clickedOnOrigin(self, event: tk.Event):
        self.dragEdge = "origin"
    
    def _clickedOnTopOfAxis(self, event: tk.Event):
        self.dragEdge = "axisTop"
    def _clickedOnOpeningEdge(self, event: tk.Event, candleIndex : int, candle : ValueCandle):
        self.dragEdge = "opening"
        self.dragIndex = candleIndex 
    
    def _clickedOnClosingEdge(self, event: tk.Event, candleIndex: int, candle: ValueCandle):
        """
        Registers that the user clicked on a top edge of some rectangle
        """
        self.dragEdge = "closing"
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = candleIndex
        self.originalHeight = candle.closingCorner.Y - candle.openingCorner.Y
    
    def _clickedOnRightEdge(self, event: tk.Event, candleIndex: int, candle: ValueCandle):
        """
        Registers that the user clicked on a right edge of some rectangle
        """
        self.dragEdge = 'right'
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = candleIndex
        
        self.originalCoordinates = candle.rightTop
        self.rightEdgeCursorOffset = event.x - candle.rightTop.X
        self.originalLeftX = candle.leftBottom.X
    
    def _clickedOnLeftEdge(self, event: tk.Event, candleIndex: int, candle: ValueCandle): 
        """
        Registers that the user clicked on a left edge of some rectangle
        """
        self.dragEdge = "left"
        self.dragStart = ValuePoint2D(event.x, event.y)
        self.dragIndex = candleIndex
        
        self.originalLeftX = candle.leftBottom.X
        self.originalSpacing = self.plotSolver.GetSpacing()
    
    def on_left_down(self, event: tk.Event) -> None:
        for index, candle in enumerate(self.plotSolver.GetCandleData()): # type: ignore
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

    def on_left_up(self, event: tk.Event):
        self.dragEdge = None
        self.dragStart = ValuePoint2D(0,0)
        self.dragIndex = None
        self.originalRightCoordinates = None
        self.originalLeftX = None
        self.originalSpacing = None
    

    #######################
    # Mouse move handling #
    #######################

    def on_mouse_move(self, event: tk.Event):
        if self.dragEdge is None:
            return
        
        origin = self.plotSolver.GetOrigin()

        if self.dragEdge == "right":
            newWidth = (event.x - (self.dragIndex+1)*self.plotSolver.GetSpacing() - origin.X)/(self.dragIndex+1) # type: ignore
            if newWidth >= 5:
                self.plotSolver.ChangeWidth(newWidth) # type: ignore
            pass
        
        elif self.dragEdge == "left":
            newSpacing = (event.x - self.dragIndex*self.plotSolver.GetWidth() - origin.X)/(self.dragIndex+1) # type: ignore
            if newSpacing >=0:
                self.plotSolver.ChangeSpacing(newSpacing) # type: ignore
            pass

        elif self.dragEdge == "closing":
            dy = self.dragStart.Y - event.y  
            newHeight = self.originalHeight + dy
            self.plotSolver.ChangeHeight(self.dragIndex, newHeight) # type: ignore
        
        elif self.dragEdge == "opening":
            self.plotSolver.ChangeOpening(self.dragIndex, self.canvasHeight - event.y - origin.Y) # type: ignore
        
        elif self.dragEdge == "minimum":
            self.plotSolver.ChangeMinimum(self.dragIndex, self.canvasHeight - event.y - origin.Y) # type: ignore
        
        elif self.dragEdge == "maximum":
            self.plotSolver.ChangeMaximum(self.dragIndex, self.canvasHeight - event.y - origin.Y) # type: ignore
        
        elif self.dragEdge == "origin":
            self.plotSolver.ChangeOrigin(event.x, self.canvasHeight - event.y)
        
        elif self.dragEdge == "axisTop":  
            newHeight = self.canvasHeight - event.y - origin.Y
            if newHeight > 10:
                self.plotSolver.ChangeAxisHeight(newHeight)
        
        self._updateCanvas()
        self._updateDataView()
    
    def check_cursor(self,event: tk.Event):
        """
        Changes cursor according to its position.
        """
        for idx, candle in enumerate(self.plotSolver.GetCandleData()): # type: ignore
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
    

    ########################
    # Right mouse handling #
    ########################

    def on_right_up(self, event: tk.Event):
        return
    
    def on_right_down(self, event: tk.Event):
            print("Right mouse click to do")
            return
            for index, candle in enumerate(self.plotSolver.GetCandleData()): # type: ignore
                if self._isInsideOfCandle(event, candle):
                    self.rectangleIndexToChange = index
#                    self.menu.post(event.x_root, event.y_root) # problem here
                    return
            super().on_right_down(event)

