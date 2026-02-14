import tkinter as tk
from .canvasdrawers import CandlesticCanvasDrawer
from .eventhandlers import EventHandler
from kiwiplots.solvers import CandlestickChartSolver
from .plotmetadata import CandlesticPlotMetadata
from .plotmath import isNear
from .dataviewers import CandlesticDataViewer
from kiwiplots.plotelement import ValueCandle, ValuePoint2D
from tkinter import simpledialog
from tkinter import colorchooser 

class CandlesticEventHandler(EventHandler):
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
        self.drawer = CandlesticCanvasDrawer(canvas, width, height)
    
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
        return isNear(closingY, event.y) and candle.openingCorner.X <= event.x <= candle.closingCorner.X

    def _isNearOpeningEdge(self, event: tk.Event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        openingY = self.canvasHeight - (candle.openingCorner.Y + origin.Y)
        return isNear(openingY, event.y) and candle.openingCorner.X <= event.x <= candle.closingCorner.X

    def _isNearLeftEdge(self, event: tk.Event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        candleBottomY, candleTopY = self.canvasHeight - (min(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y), self.canvasHeight - (max(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y)
        return isNear(event.x, candle.openingCorner.X) and candleTopY <= event.y <= candleBottomY
        pass

    def _isNearRightEdge(self, event: tk.Event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        candleBottomY, candleTopY = self.canvasHeight - (min(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y), self.canvasHeight - (max(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y)
        return isNear(event.x, candle.closingCorner.X) and candleTopY <= event.y <= candleBottomY
      

    def _isNearMaximum(self, event: tk.Event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        maxY = self.canvasHeight - (candle.wickTop.Y + origin.Y)
        return isNear(maxY, event.y) and isNear(candle.wickTop.X, event.x)
        

    def _isNearMinimum(self, event: tk.Event, candle : ValueCandle):
        origin = self.plotSolver.GetOrigin()
        minY = self.canvasHeight - (candle.wickBottom.Y + origin.Y)
        return isNear(minY, event.y) and isNear(candle.wickBottom.X, event.x)
    
    def _isNearOrigin(self, event: tk.Event):
        origin = self.plotSolver.GetOrigin()
        return isNear(event.x, origin.X) and isNear(event.y, self.canvasHeight - origin.Y)
    
    def _isNearTopOfYAxis(self,event: tk.Event):
        topNormalized = self.canvasHeight - self.plotSolver.GetAxisHeight() - self.plotSolver.GetOrigin().Y
        return isNear(event.y, topNormalized, 10) and isNear(event.x, self.plotSolver.GetOrigin().X, 10)
    
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