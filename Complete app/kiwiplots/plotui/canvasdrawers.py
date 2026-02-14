import tkinter as tk
from tkinter import font 
from abc import ABC
from kiwiplots.solvers import ChartSolver, CandlestickChartSolver
from .plotmetadata import PlotMetadata, CandlesticPlotMetadata
from .plotmath import ceilToNearestTen, divideInterval
from kiwiplots.plotelement import ValuePoint2D

class CanvasDrawer(ABC):
    """
    Abstract class. Contains logic to draw given plot element to canvas (tk.canvas).
    Implementations depend on given type of plot element. 
    """
    def __init__(self, canvas : tk.Canvas) -> None:
        """
        Initializes the CanvasDrawer with a canvas for rendering.
        
        Args:
            canvas: A tkinter Canvas widget where the plot will be drawn.
        """
        self.canvas : tk.Canvas = canvas
    
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
