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
from enum import Enum
from typing import TypeAlias


class CandlesticEventHandler(EventHandler):
    ###################
    # Initialization #
    ###################

    class CandleEventRegistersLeftButton(EventHandler.EventRegistersLeftButton):
        class CandleLeftEvents(Enum):
            nothing = 0
            minimum = 1
            maximum = 2
            opening = 3
            closing = 4
            origin  = 5
            axisTop = 6
            width   = 7 #aka right
            spacing = 8 #aka left
            pass
        
        
        def __init__(self):
            super().__init__()
            self.eventType: "CandlesticEventHandler.CandleEventRegistersLeftButton.CandleLeftEvents" = CandlesticEventHandler.CandleEventRegistersLeftButton.CandleLeftEvents.nothing
        
        def reset(self) -> None:
            super().reset()
            self.eventType = CandlesticEventHandler.CandleEventRegistersLeftButton.CandleLeftEvents.nothing
    
    class CandleEventRegistersRightButton(EventHandler.EventRegistersRightButton):
        pass
    
    LeftEvents: TypeAlias = CandleEventRegistersLeftButton.CandleLeftEvents

    def __init__(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver) -> None:
        super().__init__(plotMetadata)
        self.plotSolver : CandlestickChartSolver = solver
        self.canvasHeight : int = None  # pyright: ignore[reportAttributeAccessIssue]
        self.eventRegistersLeft : CandlesticEventHandler.CandleEventRegistersLeftButton = CandlesticEventHandler.CandleEventRegistersLeftButton()
        self.eventRegistersRight : CandlesticEventHandler.CandleEventRegistersRightButton = CandlesticEventHandler.CandleEventRegistersRightButton()
    
    def initializeDataView(self, textWindow: tk.Text):
        self.dataViewer = CandlesticDataViewer(textWindow)
    
    def initializeCanvas(self, canvas: tk.Canvas, width: int, height : int):
        self.canvas = canvas
        self.canvasHeight = height
        self.drawer = CandlesticCanvasDrawer(canvas, width, height)
    
    def initializeRightClickMenu(self, menu: tk.Menu) -> None:
        self.elementMenu = menu
        self.elementMenu.add_command(label="Change positive color", command=self._changePositiveColor)
        self.elementMenu.add_command(label="Change negative color", command=self._changeNegativeColor)
        self.elementMenu.add_command(label="Change name", command=self._changeName)
        self.elementMenu.add_command(label="Switch name visibility", command=self._switchNameVisibility)
    
    def initializeDefaultRightClickMenu(self, menu: tk.Menu) -> None:
        super().initializeDefaultRightClickMenu(menu)
        self.defaultMenu.add_command(label="Add candle TEST", command=self._addCandleTEST)
    
    def _addCandleTEST(self):
        print("adding candle!")
        self.plotSolver.AddCandle("newOne", 2* self.plotMetadata.heightScaleFactor,8* self.plotMetadata.heightScaleFactor,1* self.plotMetadata.heightScaleFactor,11* self.plotMetadata.heightScaleFactor)
        print("updating UI")
        self.UpdateUI()
        print("candle added")
    
    ########################
    # Left click handeling #
    ########################
    
    def _clickedOnMaximum(self, event: tk.Event, candleIndex : int, candle : ValueCandle):
        self.eventRegistersLeft.eventType = self.LeftEvents.maximum
        self.eventRegistersLeft.dragIndex = candleIndex

    def _clickedOnMinimum(self, event: tk.Event, candleIndex : int, candle : ValueCandle):
        self.eventRegistersLeft.eventType = self.LeftEvents.minimum
        self.eventRegistersLeft.dragIndex = candleIndex
    
    def _clickedOnOrigin(self, event: tk.Event):
        self.eventRegistersLeft.eventType = self.LeftEvents.origin
    
    def _clickedOnTopOfAxis(self, event: tk.Event):
        self.eventRegistersLeft.eventType = self.LeftEvents.axisTop
    def _clickedOnOpeningEdge(self, event: tk.Event, candleIndex : int, candle : ValueCandle):
        self.eventRegistersLeft.eventType = self.LeftEvents.opening
        self.eventRegistersLeft.dragIndex = candleIndex 
    
    def _clickedOnClosingEdge(self, event: tk.Event, candleIndex: int, candle: ValueCandle):
        """
        Registers that the user clicked on a top edge of some rectangle
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.closing
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x, event.y)
        self.eventRegistersLeft.dragIndex = candleIndex
        self.eventRegistersLeft.originalHeight = candle.closingCorner.Y - candle.openingCorner.Y
    
    def _clickedOnRightEdge(self, event: tk.Event, candleIndex: int, candle: ValueCandle):
        """
        Registers that the user clicked on a right edge of some rectangle
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.width
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x, event.y)
        self.eventRegistersLeft.dragIndex = candleIndex
        
        self.originalCoordinates = candle.rightTop
        self.eventRegistersLeft.originalLeftX = candle.leftBottom.X
    
    def _clickedOnLeftEdge(self, event: tk.Event, candleIndex: int, candle: ValueCandle): 
        """
        Registers that the user clicked on a left edge of some rectangle
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.spacing
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x, event.y)
        self.eventRegistersLeft.dragIndex = candleIndex
        
        self.eventRegistersLeft.originalLeftX = candle.leftBottom.X
        self.eventRegistersLeft.originalSpacing = self.plotSolver.GetSpacing()
    
    def on_left_down(self, event: tk.Event) -> None:

        if self._isNearOrigin(event):
                self._clickedOnOrigin(event)
                return
        elif self._isNearTopOfYAxis(event):
                self._clickedOnTopOfAxis(event)
                return

        for index, candle in enumerate(self.plotSolver.GetCandleData()): 
            if self._isNearMaximum(event, candle):
                print(f"maximum {index}")
                self._clickedOnMaximum(event, index, candle)
                break
            elif self._isNearMinimum(event, candle):
                print(f"minimum {index}")
                self._clickedOnMinimum(event, index, candle)
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
        self.eventRegistersLeft.reset()
    
    #######################
    # Mouse move handling #
    #######################

    def on_mouse_move(self, event: tk.Event):
        if self.eventRegistersLeft.eventType is None:
            return
        
        origin = self.plotSolver.GetOrigin()

        if self.eventRegistersLeft.eventType == self.LeftEvents.width:
            self.plotSolver.ChangeWidthX(self.eventRegistersLeft.dragIndex,event.x)
        
        elif self.eventRegistersLeft.eventType == self.LeftEvents.spacing:
            self.plotSolver.ChangeSpacingX(self.eventRegistersLeft.dragIndex,event.x)

        elif self.eventRegistersLeft.eventType == self.LeftEvents.closing:
            dy = self.eventRegistersLeft.dragStart.Y - event.y  
            newHeight = self.eventRegistersLeft.originalHeight + dy
            self.plotSolver.ChangeHeight(self.eventRegistersLeft.dragIndex, newHeight)  # pyright: ignore[reportArgumentType]
        
        elif self.eventRegistersLeft.eventType == self.LeftEvents.opening:
            self.plotSolver.ChangeOpening(self.eventRegistersLeft.dragIndex, self.canvasHeight - event.y - origin.Y)  # pyright: ignore[reportArgumentType]
        
        elif self.eventRegistersLeft.eventType == self.LeftEvents.minimum:
            self.plotSolver.ChangeMinimum(self.eventRegistersLeft.dragIndex, self.canvasHeight - event.y - origin.Y)  # pyright: ignore[reportArgumentType]
        
        elif self.eventRegistersLeft.eventType == self.LeftEvents.maximum:
            self.plotSolver.ChangeMaximum(self.eventRegistersLeft.dragIndex, self.canvasHeight - event.y - origin.Y)  # pyright: ignore[reportArgumentType]
        
        elif self.eventRegistersLeft.eventType == self.LeftEvents.origin:
            self.plotSolver.ChangeOrigin(event.x, self.canvasHeight - event.y)
        
        elif self.eventRegistersLeft.eventType == self.LeftEvents.axisTop:  
            newHeight = self.canvasHeight - event.y - origin.Y
            if newHeight > 10:
                self.plotSolver.ChangeAxisHeight(int(newHeight))
        
        self._updateCanvas()
        self._updateDataView()
    
    def check_cursor(self,event: tk.Event):
        """
        Changes cursor according to its position.
        """
        if self._isNearOrigin(event):
            self.canvas.config(cursor="fleur")
            return
        elif self._isNearTopOfYAxis(event):
            self.canvas.config(cursor="sb_v_double_arrow")
            return

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
            

        self.canvas.config(cursor="arrow")
    
    ########################
    # Right mouse handling #
    ########################

    def on_right_up(self, event: tk.Event):
        return
    
    def on_right_down(self, event: tk.Event):
            for index, candle in enumerate(self.plotSolver.GetCandleData()):
                if self._isInsideOfCandle(event, candle):
                    self.eventRegistersRight.rectangleIndexToChange = index
                    self.elementMenu.post(event.x_root, event.y_root) 
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
        currentName = self.plotSolver.GetName(self.eventRegistersRight.rectangleIndexToChange)
        newName = simpledialog.askstring("Change name", "New name:", initialvalue=currentName)
        if newName == None:
            return
        self.plotSolver.ChangeName(self.eventRegistersRight.rectangleIndexToChange, newName)
        self._updateCanvas()
        self._updateDataView()
        pass

    def _switchNameVisibility(self):
        self.plotSolver.SwitchNameVisibility(self.eventRegistersRight.rectangleIndexToChange)
        self._updateCanvas()
    
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
