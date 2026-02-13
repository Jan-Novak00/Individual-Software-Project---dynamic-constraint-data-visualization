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


def _ceilToNearestTen(number: float):
    return ((number // 10) + 1) * 10

def _floorToNearestTen(number: float):
    return ((number // 10) - 1) * 10

def _divideInterval(low: float, high: float, parts: int):
    if parts < 2:
        return [low, high]

    step = (high - low) // (parts - 1)
    return [low + i * step for i in range(parts)]


"""
Abstract class. Caries shared metadata about plot data, such as scale factor etc., which are used to convert pixel dimension into data dimension. 
"""
class PlotMetadata(ABC):
    def __init__(self, scaleFactor: float, xAxisValue: float):
        self.scaleFactor : float = scaleFactor
        self.xAxisValue : float = xAxisValue


"""
Abstract class. Contains logic to show current data values represented by a graph.
"""
class DataViewer(ABC):
    def __init__(self, textWindow : tk.Text):
        self.dataWindow : tk.Text = textWindow

    def write(self, plotMetadata: PlotMetadata, solver: ChartSolver, changedIndex: int, changedStatus: str = "")->None: # type: ignore
        raise NotImplementedError("Method DataViewr.write must be declared in subclass")

"""
Abstract class. Contains logic to draw given plot element to canvas (tk.canvas).
Implementations depend on given type of plot element. 
"""
class CanvasDrawer(ABC):
    def __init__(self, canvas : tk.Canvas) -> None:
        self.canvas : tk.Canvas = canvas
    
    def draw(self, plotMetadata: PlotMetadata, solver : ChartSolver)->None:
        """
        Draw data on the canvas.
        """
        raise NotImplementedError("Method CanvasDrawer.draw must be declared in subclass")
    


"""
Abstract class. Handles user interaction with the graph on tk.Canvas.
Implementations are based on type of graph user is working with.
Inicialized via dependency injection.
"""
class CanvasHandler(ABC):
    def __init__(self, plotMetadata: PlotMetadata) -> None:
        self.canvas : tk.Canvas = None # type: ignore
        self.defaultMenu : tk.Menu = None # type: ignore
        self.elementMenu : tk.Menu = None # type: ignore
        self.drawer : CanvasDrawer = None  # type: ignore
        self.dataViewer : DataViewer = None # type: ignore
        self.plotSolver : ChartSolver = None  # type: ignore
        self.plotMetada = plotMetadata                           #ToDo  typovani
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
        self.drawer.draw(self.plotMetada,self.plotSolver) 
    
    def _updateDataView(self):
        self.dataViewer.write(self.plotMetada, self.plotSolver, self.dragIndex, self.dragEdge) # type: ignore
    
    def _changeTitle(self):
        """
        Plot title change using UI
        """
        newTitle = simpledialog.askstring("Enter new title","New title: ")
        if newTitle is None:
            return
        else:
            self.plotSolver.ChangeTitle(newTitle)
            self._updateCanvas()

    
    def on_left_down(self, event: tk.Event)->None:
        raise NotImplementedError("Method CanvasHandler.on_left_down must be declared in subclass")
    
    def on_right_down(self, event: tk.Event)->None:
        self.defaultMenu.post(event.x_root,event.y_root)

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
    
    def inicializeCanvas(self, canvas: tk.Canvas, width:int, height: int)->None:
        raise NotImplementedError("Method CanvasHandler.inicializeCanvas must be declared in subclass")
    
    def inicializeDefaultRightClickMenu(self, menu: tk.Menu)->None:
        self.defaultMenu = menu
        self.defaultMenu.add_command(label = "Change title", command=self._changeTitle)
    
    def inicializeRightClickMenu(self, menu: tk.Menu)->None:
        raise NotImplementedError("Method CanvasHandler.inicializeRightClickMenu must be declared in subclass")
        
    

"""
Abstract class. Contains logic to create image of the graph.
"""
class PictureDrawer(ABC):
    
    def draw(self, plotMetada : PlotMetadata, solver: ChartSolver, width: int, height: int):
        raise NotImplementedError("Method PictureDrawer.draw must be declared in subclass")

"""
Abstract class. Contains logic to create text output of the data.
"""
class DataWriter(ABC):

    def write(self, plotMetada : PlotMetadata, solver: ChartSolver):
        raise NotImplementedError("Method DataWriter.write must be declared in subclass")
    pass

"""
Handles communication between UI features.
"""
class UICore:
    def __init__(self, plotMetadata: PlotMetadata, solver : ChartSolver, canvasHandler : CanvasHandler, pictureDrawer : PictureDrawer, dataWriter: DataWriter, plotWidth: int, plotHeight: int):
        self.solver : ChartSolver = solver
        self.canvasHandler : CanvasHandler = canvasHandler
        self.pictureDrawer : PictureDrawer = pictureDrawer
        self.dataWriter : DataWriter = dataWriter
        self.plotWidth = plotWidth
        self.plotHeight = plotHeight
        self.picturePathBuffer : Union[str,None] = None
        self.dataPathBuffer : Union[str,None] = None
        self.plotMetadata : PlotMetadata = plotMetadata 


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
        self.elementMenu = tk.Menu(self.frame,tearoff=0)

    def inicializeHandlers(self):
        self.canvasHandler.inicializeCanvas(self.canvas, self.plotWidth, self.plotHeight)
        self.canvasHandler.inicializeDataView(self.dataWindow)
        self.canvasHandler.inicializeDefaultRightClickMenu(self.defaultMenu)
        self.canvasHandler.inicializeRightClickMenu(self.elementMenu)
    
    
    def on_saveDataButton_click(self):
        if self.dataPathBuffer == None:
            self.dataPathBuffer = os.path.join(os.getcwd(), self.solver.GetTitle())
        fileName = simpledialog.askstring("Save data", "File name (without extension): ", initialvalue=self.dataPathBuffer)
        if fileName == None:
            return
        else:
            self.dataPathBuffer = fileName

        self.dataWriter.write(self.plotMetadata, self.solver, self.dataPathBuffer + ".csv") # type: ignore    
    
    def on_savePictureButton_click(self):
        self.canvasHandler.UpdateUI()
        if self.picturePathBuffer == None:
            self.picturePathBuffer = os.path.join(os.getcwd(), self.solver.GetTitle())  
        
        pictureName = simpledialog.askstring("Save plot", "Image name (without extension): ", initialvalue=self.picturePathBuffer)

        if pictureName == None:
            return
        else:
            self.picturePathBuffer = pictureName 

        print("Saving canvas to", pictureName + ".png")
        self.pictureDrawer.draw(self.plotMetadata, self.solver, self.plotWidth, self.plotHeight)
    
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

class CandlesticPlotMetadata(PlotMetadata):
    def __init__(self, scaleFactor: float, xAxisValue: float, xAxisLabel : str, yAxisLabel : str):
        self.scaleFactor : float = scaleFactor
        self.xAxisValue : float = xAxisValue
        self.xAxisLabel : str = xAxisLabel
        self.yAxisLabel : str = yAxisLabel


class CandlesticDataViewer(DataViewer):
    def __init__(self, textWindow: tk.Text):
        super().__init__(textWindow)

    def write(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver, changedIndex: int, changedStatus: str = ""):
        """
        Displays all data for the user and highlights which data is being edited
        """
        xAxisValue = plotMetadata.xAxisValue
        scaleFactor = plotMetadata.scaleFactor
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        valueEdited = changedStatus in ["opening", "closing", "maximum", "minimum"]
        candles = solver.GetCandleData()

        for i in range(len(candles)-1, -1, -1):
            candle = candles[i]
            openingValue = candle.openingCorner.Y/scaleFactor + xAxisValue
            closingValue = candle.closingCorner.Y/scaleFactor + xAxisValue
            maximumValue = candle.wickTop.Y/scaleFactor + xAxisValue
            minimumValue = candle.wickBottom.Y/scaleFactor + xAxisValue
            
            string = f"{candle.name}:\n\topening = {openingValue:.4f},\n\tclosing = {closingValue:.4f},\n\tmin = {minimumValue:.4f},\n\tmax = {maximumValue:.4f}\n\n"
            if valueEdited and i == changedIndex:
                self.dataWindow.insert("1.0",f"{string}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"{string}\n")
        self.dataWindow.config(state="disabled")

class CandlesticCanvasDrawer(CanvasDrawer):
    def __init__(self, canvas : tk.Canvas, canvasWidth : int, canvasHeight : int):
        super().__init__(canvas)
        self.canvasHeight = canvasHeight
        self.canvasWidth = canvasWidth
    
    def _drawCandles(self, solver: CandlestickChartSolver, scaleFactor : float, xAxisValue : float): 
        
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

            self.canvas.create_rectangle(x1,y2,x2,y1, fill=candle.color, outline="black") # type: ignore
            self.canvas.create_line(minX, minY, maxX, maxY, fill=candle.color) # type: ignore
            if candle.nameVisible: 
                self.canvas.create_text(candle.wickBottom.X ,self.canvasHeight - origin.Y + 10, text=candle.name)
    
    def _writePlotTitle(self, solver: CandlestickChartSolver):

        self.canvas.create_text(self.canvasWidth / 2, 20,text=solver.GetTitle(),font=("Arial", 16, "bold")) 
    
    def _drawAxes(self, maximumValue: float, leftCornerXAxis: int, origin : ValuePoint2D, scaleFactor : float, minimumValue : int, xAxisLabel : str, yAxisLabel : str, xAxisValue : float):   # move to superclass
        """
        Draws axes on the canvas
        """
        topNumber = _ceilToNearestTen(maximumValue) 

        marks = _divideInterval(minimumValue, topNumber, 5)
      
        self.canvas.create_line(origin.X, self.canvasHeight - origin.Y, leftCornerXAxis + 10, self.canvasHeight - origin.Y, fill="black", width=1)
        self.canvas.create_line(origin.X, self.canvasHeight - origin.Y - minimumValue, origin.X, self.canvasHeight - origin.Y - topNumber, fill="black", width=1)

        for mark in marks:
            y = self.canvasHeight - origin.Y - mark
            self.canvas.create_line(origin.X - 5, y, origin.X, y, fill="black")

            trueValue = mark/scaleFactor + xAxisValue
            valueString = f"{(trueValue):.2g}" if (trueValue <= 1e-04 or trueValue >= 1e06) else f"{(trueValue):.2f}"

            self.canvas.create_text(origin.X - 10, y, text=f"{valueString}", anchor="e")

        
        boldFont = font.Font(family="Helvetica", size=10, weight="bold")
        self.canvas.create_text(leftCornerXAxis + 20, self.canvasHeight - origin.Y + 10, text=xAxisLabel, anchor="n",font=boldFont)
        self.canvas.create_text(origin.X, self.canvasHeight - origin.Y - topNumber - 10, text=yAxisLabel, anchor="s",font=boldFont)
    
    def draw(self, plotMetadata: CandlesticPlotMetadata, solver : CandlestickChartSolver)->None:
        """
        Draws candles and axes on the plot
        """
        print("Debug: drawing candles")
        self.canvas.delete("all")
        self._writePlotTitle(solver)
        self._drawCandles(solver, plotMetadata.scaleFactor, plotMetadata.xAxisValue)

        origin = solver.GetOrigin()
        candles = solver.GetCandleData()
        
        lowestWickHeight = min([candle.wickBottom.Y for candle in candles])
        self._drawAxes(solver.GetAxisHeight(), candles[-1].rightTop.X, origin, plotMetadata.scaleFactor, min(0, lowestWickHeight), plotMetadata.xAxisLabel, plotMetadata.yAxisLabel, plotMetadata.xAxisValue)  

class CandlesticPictureDrawer(PictureDrawer):

    def _drawCandlesPNG(self, solver: CandlestickChartSolver, draw : ImageDraw.ImageDraw, height: int):
        candles = solver.GetCandleData()
        origin = solver.GetOrigin()
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
            y1 = height - leftBottomY - origin.Y
            
            x2 = rightTopX
            y2 = height - rightTopY - origin.Y

            draw.rectangle((x1,y2,x2,y1), fill=candle.color, outline="black")

            xMax, yMax = candle.wickTop.X, height - candle.wickTop.Y - origin.Y
            xMin, yMin = candle.wickBottom.X, height - candle.wickBottom.Y - origin.Y
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
                y_text = height - origin.Y + 10

                draw.text(
                    (x_center - text_width / 2, y_text - text_height/2),
                    text,
                    fill="black",
                    font=font)
    
    def _drawAxesPNG(self, scaleFactor:float, height: int, xAxisValue: float, draw: ImageDraw.ImageDraw, maximumValue: float, leftCornerXAxis: int, origin : ValuePoint2D, minimumValue : int = 0, xAxisLabel:str = "", yAxisLabel: str = ""):  
        """
        Draws axes on the PNG output
        """
        topNumber = _ceilToNearestTen(maximumValue) 

        marks = _divideInterval(minimumValue,topNumber, 5)
      
        draw.line((origin.X, height - origin.Y, leftCornerXAxis + 10, height - origin.Y), fill=(0,0,0), width=1)
        draw.line((origin.X, height - origin.Y - minimumValue, origin.X, height - origin.Y - topNumber), fill=(0,0,0), width=1)

        for mark in marks:
            y = height - origin.Y - mark
            draw.line((origin.X - 5, y, origin.X, y), fill=(0,0,0))

            trueValue = mark/scaleFactor + xAxisValue
            valueString = f"{(trueValue):.2g}" if (trueValue <= 1e-04 or trueValue >= 1e06) else f"{(trueValue):.2f}"
            font = ImageFont.load_default()

            # get text size
            bbox = font.getbbox(valueString)
            textWidth = bbox[2] - bbox[0]
            textHeight = bbox[3] - bbox[1]

            draw.text((origin.X - 10 - textWidth, y - textHeight/2), text=f"{valueString}", fill = (0,0,0))
        
        #Axis labels
        font = ImageFont.truetype("arialbd.ttf", 12)
        bbox = font.getbbox(xAxisLabel)
        textW = bbox[2] - bbox[0]
        textH = bbox[3] - bbox[1]
        draw.text(
            (leftCornerXAxis + 10 - textW/2, height - origin.Y + 10), 
            text=xAxisLabel, fill=(0,0,0), font=font
        )

        bbox = font.getbbox(yAxisLabel)
        textW = bbox[2] - bbox[0]
        textH = bbox[3] - bbox[1]
        draw.text(
            (origin.X - textW/2, height - origin.Y - topNumber - textH - 5), 
            text=yAxisLabel, fill=(0,0,0), font=font
        )
    
    def _writePlotTitlePNG(self, draw: ImageDraw.ImageDraw, solver:CandlestickChartSolver, width: int):
        font = ImageFont.truetype("arialbd.ttf", 16)
        text = solver.GetTitle()
        bbox = font.getbbox(text)
        textWidth = bbox[2] - bbox[0]
        draw.text((width / 2 - textWidth, 20),text=text,font=font,fill = (0,0,0))

    def draw(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver, width: int, height: int):
        candles = solver.GetCandleData()
        lowestWickHeight = min([candle.wickBottom.Y for candle in candles])
        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)
        self._drawCandlesPNG(solver, draw, height)
        self._drawAxesPNG(plotMetadata.scaleFactor,height, plotMetadata.xAxisValue,draw, solver.GetAxisHeight(), candles[-1].rightTop.X, solver.GetOrigin(), min(0, lowestWickHeight))
        self._writePlotTitlePNG(draw,solver,width)
        img.save(f"{solver.GetTitle()}.png")

class CandlesticDataWriter(DataWriter):
    def write(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver, file: str):
        with open(file,"w") as output:
            candles = solver.GetCandleData()
            for candle in candles:
                output.write(f"{candle.name},{candle.openingCorner.Y/plotMetadata.scaleFactor + plotMetadata.xAxisValue},{candle.closingCorner.Y/plotMetadata.scaleFactor + plotMetadata.xAxisValue},{candle.wickBottom.Y/plotMetadata.scaleFactor + plotMetadata.xAxisValue},{candle.wickTop.Y/plotMetadata.scaleFactor + plotMetadata.xAxisValue}")
                output.write("\n")

class CandlesticCanvasHandler(CanvasHandler):

    ###################
    # Inicializastion #
    ###################

    def __init__(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver) -> None:
        super().__init__(plotMetadata)
        self.plotSolver : CandlestickChartSolver = solver 
        self.canvasHeight : int = None # type: ignore
    
    def inicializeDataView(self, textWindow: tk.Text):
        self.dataViewer = CandlesticDataViewer(textWindow)
    
    def inicializeCanvas(self, canvas: tk.Canvas, width: int, height : int):
        self.canvas = canvas
        self.canvasHeight = height
        self.drawer = CandlesticCanvasDrawer(canvas, width, height) #ToDo
    
    def inicializeRightClickMenu(self, menu: tk.Menu) -> None:
        self.elementMenu = menu
        self.elementMenu.add_command(label="Change positive color", command=self._changePositiveColor)
        self.elementMenu.add_command(label="Change negative color", command=self._changeNegativeColor)
        self.elementMenu.add_command(label="Change name", command=self._changeName)
        self.elementMenu.add_command(label="Switch name visibility", command=self._switchNameVisibility)
    
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
            for index, candle in enumerate(self.plotSolver.GetCandleData()): # type: ignore
                if self._isInsideOfCandle(event, candle):
                    self.rectangleIndexToChange = index
                    self.elementMenu.post(event.x_root, event.y_root) # problem here
                    return
            super().on_right_down(event)
    
    def _changePositiveColor(self):
        color = colorchooser.askcolor(title="Choose different color")
        if color[1] == None:
            return
        self.plotSolver.ChangePositiveColor(color[1])
        self._updateCanvas()
    
    def _changeNegativeColor(self):
        color = colorchooser.askcolor(title="Choose different color")
        if color[1] == None:
            return
        self.plotSolver.ChangeNegativeColor(color[1])
        self._updateCanvas()

    def _changeName(self):
        currentName = self.plotSolver.GetName(self.rectangleIndexToChange)
        newName = simpledialog.askstring("Change name", "New name:", initialvalue=currentName)
        if newName == None:
            return
        self.plotSolver.ChangeName(self.rectangleIndexToChange, newName)
        self._updateCanvas()
        self._updateDataView()
        pass

    def _switchNameVisibility(self):
        self.plotSolver.SwitchNameVisibility(self.rectangleIndexToChange)
        self._updateCanvas()
    


