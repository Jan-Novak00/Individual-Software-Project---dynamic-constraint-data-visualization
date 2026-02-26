import tkinter as tk
from tkinter import font 
from abc import ABC
from kiwiplots.solvers import *
from .plotmetadata import *
from .plotmath import ceilToNearestTen, divideInterval
from kiwiplots.plotelement import ValuePoint2D

class CanvasDrawer(ABC):
    """
    Abstract class. Contains logic to draw given plot element to canvas (tk.canvas).
    Implementations depend on given type of plot element. 
    """
    def __init__(self, canvas : tk.Canvas, canvasWidth: int, canvasHeight: int) -> None:
        """
        Initializes the CanvasDrawer with a canvas for rendering.
        
        Args:
            canvas: A tkinter Canvas widget where the plot will be drawn.
            canvasWidth: Width of the canvas. It has to be given explicitly, because canvas has incorrect value of width before the first draw.
            canvasHeight: Height of the canvas. It has to be given explicitly, because canvas has incorrect value of height before the first draw.
        """
        self.canvas : tk.Canvas = canvas
        self.canvasWidth : int = canvasWidth
        self.canvasHeight = canvasHeight
    
    def draw(self, plotMetadata: PlotMetadata, solver : ChartSolver)->None:
        """
        Renders the plot data and axes on the canvas.
        
        This method should clear the canvas and redraw all plot elements including
        data visualizations, axes, labels, and titles.
        
        Args:
            plotMetadata: Metadata about the plot including scale factor and axis values.
            solver: The solver containing the plot data to be rendered.
        """
        raise NotImplementedError("Method CanvasDrawer.draw must be declared in subclass")

    def _writePlotTitle(self, title: str):
        self.canvas.create_text(self.canvasWidth / 2, 20,text=title,font=("Arial", 16, "bold")) 

    def _drawAxes(self, maximumValue: float, leftCornerXAxis: int, origin : ValuePoint2D, scaleFactor : float, minimumValue : int, xAxisLabel : str, yAxisLabel : str, xAxisValue : float):
        """
        Draws axes on the canvas
        """
        topNumber = ceilToNearestTen(maximumValue) 

        marks = divideInterval(minimumValue, topNumber, 5)
      
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
    


class CandlesticCanvasDrawer(CanvasDrawer):
    def _drawCandles(self, solver: CandlestickChartSolver): 
        
        origin = solver.GetOrigin()
        candles = solver.GetCandleData()
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

            self.canvas.create_rectangle(x1,y2,x2,y1, fill=candle.color, outline="black") # type: ignore
            self.canvas.create_line(minX, minY, maxX, maxY, fill=candle.color) # type: ignore
            if candle.nameVisible: 
                self.canvas.create_text(candle.wickBottom.X ,self.canvasHeight - origin.Y + 10, text=candle.name)
    
    def draw(self, plotMetadata: CandlesticPlotMetadata, solver : CandlestickChartSolver)->None: # type: ignore #ToDo typing of plot metadata
        """
        Draws candles and axes on the plot
        """
        self.canvas.delete("all")
        self._writePlotTitle(plotMetadata.title)
        origin = solver.GetOrigin()
        candles = solver.GetCandleData()
        
        lowestWickHeight = min([candle.wickBottom.Y for candle in candles])
        self._drawAxes(solver.GetAxisHeight(), int(candles[-1].rightTop.X), origin, plotMetadata.heightScaleFactor, int(min(0, lowestWickHeight)), plotMetadata.xAxisLabel, plotMetadata.yAxisLabel, plotMetadata.xAxisValue)  
        
        self._drawCandles(solver)

class BarChartCanvasDrawer(CanvasDrawer):
    def _drawRectangles(self, solver: BarChartSolver): 
        """
        Draws rectangles on the plot and writes their names under them.
        """
        rectangles = solver.GetRectangleDataAsList()
        for rec in rectangles: 
            x1 = rec.leftBottom.X
            y1 = self.canvasHeight - rec.leftBottom.Y
            
            x2 = rec.rightTop.X
            y2 = self.canvasHeight - rec.rightTop.Y
            self.canvas.create_rectangle(x1,y2,x2,y1, fill=rec.color, outline="black") # pyright: ignore[reportArgumentType]
            self.canvas.create_text((x1+x2)/2,y1 + 10, text=rec.name)


    def draw(self, plotMetadata: BarChartMetadata, solver : BarChartSolver) -> None: # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Draws rectangles and axes on the plot
        """
        self.canvas.delete("all")
        self._writePlotTitle(plotMetadata.title)
        rectangles = solver.GetRectangleDataAsList()
        self._drawRectangles(solver)

        origin = solver.GetOrigin()
        
        #highestRectangleHeight = max([rec.rightTop.Y - origin.Y for rec in rectangles])
        y = solver.GetAxisHeight()

        self._drawAxes(solver.GetAxisHeight(), int(rectangles[-1].rightTop.X), origin, plotMetadata.heightScaleFactor,0,plotMetadata.xAxisLabel,plotMetadata.yAxisLabel,plotMetadata.xAxisValue)

class HistogramCanvasDrawer(BarChartCanvasDrawer):
    def _drawRectangles(self, solver: BarChartSolver): 
        """
        Draws rectangles on the plot and writes their names under them.
        """
        rectangles = solver.GetRectangleDataAsList()
        for rec in rectangles: 
            x1 = rec.leftBottom.X
            y1 = self.canvasHeight - rec.leftBottom.Y
            
            x2 = rec.rightTop.X
            y2 = self.canvasHeight - rec.rightTop.Y
            self.canvas.create_rectangle(x1,y2,x2,y1, fill=rec.color, outline="black") # pyright: ignore[reportArgumentType]
            self.canvas.create_text(x1,y1 + 10, text=rec.leftBottom.secondaryName)
            self.canvas.create_text(x2,y1 + 10, text=rec.rightTop.secondaryName)

class LineChartCanvasDrawer(CanvasDrawer):
    def _drawLines(self, solver: LineChartSolver):
        RADIUS : int = 4
        lines = solver.GetLineData()
        origin = solver.GetOrigin()
        for line in lines:
            x1, y1 = line.leftEnd.X, self.canvasHeight - (line.leftEnd.Y + origin.Y)
            x2, y2 = line.rightEnd.X, self.canvasHeight - (line.rightEnd.Y + origin.Y)
            
            self.canvas.create_line(x1,y1,x2,y2, width = 1)
            self.canvas.create_oval(
            x1 - RADIUS, y1 - RADIUS,
            x1 + RADIUS, y1 + RADIUS,
            fill="black")

            self.canvas.create_oval(
            x2 - RADIUS, y2 - RADIUS,
            x2 + RADIUS, y2 + RADIUS,
            fill="black"
            )

            #text ToDo


    def draw(self, plotMetadata: LineChartMetadata, solver: LineChartSolver)->None:
        self.canvas.delete("all")
        self._writePlotTitle(plotMetadata.title)
        lines = solver.GetLineData()

        origin = solver.GetOrigin()
        y = solver.GetAxisHeight()

        yValues = [line.leftEnd.Y for line in lines]+[line.rightEnd.Y for line in lines]
        #maximum: float = max(yValues)
        minimum: float = min(yValues+[0])

        self._drawAxes(solver.GetAxisHeight(),int(lines[-1].rightEnd.X),origin,plotMetadata.heightScaleFactor,int(minimum),plotMetadata.xAxisLabel,plotMetadata.yAxisLabel,plotMetadata.xAxisValue)
        self._drawLines(solver)
        pass