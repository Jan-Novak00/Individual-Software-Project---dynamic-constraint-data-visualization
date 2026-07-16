import tkinter as tk
from .canvasdrawers import CandlesticCanvasDrawer
from .eventhandlers import EventHandler
from kiwiplots.solvers import CandlestickChartSolver
from .plotmetadata import CandlesticPlotMetadata
from .plotmath import isNear
from .dataviewers import CandlesticDataViewer
from kiwiplots.chartelements import ValueCandle, ValuePoint2D
from tkinter import simpledialog
from tkinter import colorchooser
from kiwiplots.utils import inheritdocstring
from enum import Enum
from typing import TypeAlias
from tkinter import messagebox


class CandlesticEventHandler(EventHandler):
    """Event handler for candlestick chart user interactions.
    
    Manages mouse events for modifying candle properties (open, close, min, max values)
    and context menus for changing colors and names.
    
    Attributes:
        plotSolver (CandlestickChartSolver): The solver containing candlestick data.
        canvasHeight (int): Height of the canvas in pixels.
    """
    ###################
    # Initialization #
    ###################

    class CandleEventRegistersLeftButton(EventHandler.EventRegistersLeftButton):
        """Event registers for left mouse button.
        """
        class CandleLeftEvents(Enum):
            """Enumeration for event types.
            """
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
        """Event registers for left mouse button.
        """
        pass
    
    LeftEvents: TypeAlias = CandleEventRegistersLeftButton.CandleLeftEvents

    def __init__(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver) -> None:
        """Initializes the CandlesticEventHandler with plot metadata and solver.

        Args:
            plotMetadata (CandlesticPlotMetadata): Metadata about the candlestick chart including scale factor and axis values.
            solver (CandlestickChartSolver): Solver containing candlestick data.
        """
        super().__init__(plotMetadata)
        self.plotSolver : CandlestickChartSolver = solver
        self.canvasHeight : int = None  # pyright: ignore[reportAttributeAccessIssue]
        self.eventRegistersLeft : CandlesticEventHandler.CandleEventRegistersLeftButton = CandlesticEventHandler.CandleEventRegistersLeftButton()
        self.eventRegistersRight : CandlesticEventHandler.CandleEventRegistersRightButton = CandlesticEventHandler.CandleEventRegistersRightButton()
    
    def _isEventTypeValueChange(self) -> bool:
        return self.eventRegistersLeft.eventType in [self.LeftEvents.maximum, self.LeftEvents.minimum, self.LeftEvents.opening, self.LeftEvents.closing]

    @inheritdocstring(EventHandler.initializeDataView)
    def initializeDataView(self, textWindow: tk.Text):
        """Initializes the data viewer for candlestick chart display.
        
        Creates a CandlesticDataViewer to display candle values in the text window.
        """
        self.dataViewer = CandlesticDataViewer(textWindow)
    
    @inheritdocstring(EventHandler.initializeCanvas)
    def initializeCanvas(self, canvas: tk.Canvas, width: int, height : int):
        """Initializes the canvas drawer for candlestick chart visualization.
        
        Creates a CandlesticCanvasDrawer for rendering candles on the canvas.
        """
        self.canvas = canvas
        self.canvasHeight = height
        self.drawer = CandlesticCanvasDrawer(canvas, width, height)
    
    @inheritdocstring(EventHandler.initializeRightClickMenu)
    def initializeRightClickMenu(self, menu: tk.Menu) -> None:
        """Initializes the right-click context menu for candle operations.
        
        Adds commands to change positive/negative colors, change name, and toggle name visibility.
        """
        self.elementMenu = menu
        self.elementMenu.add_command(label="Change positive color", command=self._changePositiveColor)
        self.elementMenu.add_command(label="Change negative color", command=self._changeNegativeColor)
        self.elementMenu.add_command(label="Change name", command=self._changeName)
        self.elementMenu.add_command(label="Switch name visibility", command=self._switchNameVisibility)
    
    @inheritdocstring(EventHandler.initializeDefaultRightClickMenu)
    def initializeDefaultRightClickMenu(self, menu: tk.Menu) -> None:
        """Initializes the default right-click context menu for empty canvas area.
        
        Adds commands to add new candles to the chart.
        """
        super().initializeDefaultRightClickMenu(menu)
        assert self.defaultMenu
        self.defaultMenu.add_command(label="Add candle TEST", command=self._addCandleTEST)
        self.defaultMenu.add_command(label="Add candle", command=self._addCandle)
    
    def _addCandleTEST(self):
        """Adds a test candle with predefined values for debugging purposes."""
        self.plotSolver.AddCandle("newOne", 2* self.plotMetadata.heightScaleFactor,8* self.plotMetadata.heightScaleFactor,1* self.plotMetadata.heightScaleFactor,11* self.plotMetadata.heightScaleFactor)
        self.UpdateUI()
    
    def _addCandle(self):
        """Prompts user to add a new candle with opening, closing, minimum, and maximum values.
        
        Opens a dialog for entering the candle's name and four price values.
        Updates the chart visualization after adding the candle.
        """
        def createPopUp():
            assert self.canvas
            popup = tk.Toplevel()
            popup.resizable(True, False)
            popup.title("Add new candle")
            tk.Label(popup, text="Name:").pack(anchor="w", padx=10, pady=(10,0))
            nameEntry = tk.Entry(popup)
            nameEntry.pack(fill="x", padx=10)
            
            tk.Label(popup, text="Opening:").pack(anchor="w", padx=10, pady=(10,0))
            openingEntry = tk.Entry(popup)
            openingEntry.pack(fill="x", padx=10)
            tk.Label(popup, text="Closing:").pack(anchor="w", padx=10, pady=(10,0))
            closingEntry = tk.Entry(popup)
            closingEntry.pack(fill="x", padx=10)
            tk.Label(popup, text="Minimum:").pack(anchor="w", padx=10, pady=(10,0))
            minEntry = tk.Entry(popup)
            minEntry.pack(fill="x", padx=10)
            tk.Label(popup, text="Maximum:").pack(anchor="w", padx=10, pady=(10,0))
            maxEntry = tk.Entry(popup)
            maxEntry.pack(fill="x", padx=10)

            name = None
            opening = None
            closing = None
            minimum = None
            maximum = None

            def commit():
                nonlocal name, opening, closing, minimum, maximum
                name = nameEntry.get()
                try:
                    opening = float(openingEntry.get())
                    closing = float(closingEntry.get())
                    minimum = float(minEntry.get())
                    maximum = float(maxEntry.get())
                    if name == "":
                        name = None
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error","Invalid name or value.")
                else:
                    popup.destroy()
            def cancel():
                nonlocal name, opening, closing, minimum, maximum
                name, opening, closing, minimum, maximum = None, None, None, None, None
                popup.destroy()
            buttonFrame = tk.Frame(popup)
            buttonFrame.pack(pady=10)
            tk.Button(buttonFrame, text="OK", command=commit).pack(side="left", padx=5)
            tk.Button(buttonFrame, text="Cancel",command=cancel).pack(side="right", padx=5)
            popup.grab_set()
            self.canvas.wait_window(popup)
            return name, opening, closing, minimum, maximum
        name, opening, closing, minimum, maximum = createPopUp()
        if name == None or opening == None or closing == None or minimum == None or maximum == None:
            return
        self.plotSolver.AddCandle(name=name,
                                  opening=opening* self.plotMetadata.heightScaleFactor,
                                  closing=closing* self.plotMetadata.heightScaleFactor,
                                  minimum=minimum* self.plotMetadata.heightScaleFactor,
                                  maximum=maximum* self.plotMetadata.heightScaleFactor
                                  )
        self.UpdateUI()

    
    ########################
    # Left click handeling #
    ########################
    
    def _clickedOnMaximum(self, event: tk.Event, candleIndex : int, candle : ValueCandle):
        """Registers that the user clicked a candle's maximum.

        Args:
            event (tk.Event): Mouse event that triggered the interaction.
            candleIndex (int): Index of the selected candle in the solver data.
            candle (ValueCandle): Candle whose maximum was clicked.
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.maximum
        self.eventRegistersLeft.dragIndex = candleIndex

    def _clickedOnMinimum(self, event: tk.Event, candleIndex : int, candle : ValueCandle):
        """Registers that the user clicked a candle's minimum.

        Args:
            event (tk.Event): Mouse event that triggered the interaction.
            candleIndex (int): Index of the selected candle in the solver data.
            candle (ValueCandle): Candle whose minimum was clicked.
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.minimum
        self.eventRegistersLeft.dragIndex = candleIndex
    
    def _clickedOnOrigin(self, event: tk.Event):
        """Registers that the user started interacting with the chart origin.

        Args:
            event (tk.Event): Mouse event that triggered the interaction.
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.origin
    
    def _clickedOnTopOfAxis(self, event: tk.Event):
        """Registers that the user clicked on the chart's vertical axis.

        Args:
            event (tk.Event): Mouse event that triggered the interaction.
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.axisTop

    def _clickedOnOpeningEdge(self, event: tk.Event, candleIndex : int, candle : ValueCandle):
        """Registers that the user clicked a candle's opening edge.

        Args:
            event (tk.Event): Mouse event that triggered the interaction.
            candleIndex (int): Index of the selected candle in the solver data.
            candle (ValueCandle): Candle whose opening edge was clicked.
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.opening
        self.eventRegistersLeft.dragIndex = candleIndex 
    
    def _clickedOnClosingEdge(self, event: tk.Event, candleIndex: int, candle: ValueCandle):
        """Registers that the user clicked a candle's closing edge.

        Args:
            event (tk.Event): Mouse event that triggered the interaction.
            candleIndex (int): Index of the selected candle in the solver data.
            candle (ValueCandle): Candle whose closing edge was clicked.
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.closing
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x, event.y)
        self.eventRegistersLeft.dragIndex = candleIndex
        self.eventRegistersLeft.originalHeight = candle.closingCorner.Y - candle.openingCorner.Y
    
    def _clickedOnRightEdge(self, event: tk.Event, candleIndex: int, candle: ValueCandle):
        """Registers that the user clicked a candle's right edge.

        Args:
            event (tk.Event): Mouse event that triggered the interaction.
            candleIndex (int): Index of the selected candle in the solver data.
            candle (ValueCandle): Candle whose right edge was clicked.
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.width
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x, event.y)
        self.eventRegistersLeft.dragIndex = candleIndex
        
        self.originalCoordinates = candle.rightTop
        self.eventRegistersLeft.originalLeftX = candle.leftBottom.X
    
    def _clickedOnLeftEdge(self, event: tk.Event, candleIndex: int, candle: ValueCandle): 
        """Registers that the user clicked a candle's left edge.

        Args:
            event (tk.Event): Mouse event that triggered the interaction.
            candleIndex (int): Index of the selected candle in the solver data.
            candle (ValueCandle): Candle whose left edge was clicked.
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.spacing
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x, event.y)
        self.eventRegistersLeft.dragIndex = candleIndex
        
        self.eventRegistersLeft.originalLeftX = candle.leftBottom.X
        self.eventRegistersLeft.originalSpacing = self.plotSolver.GetSpacing()
    
    @inheritdocstring(EventHandler.on_left_down)
    def on_left_down(self, event: tk.Event) -> None:

        if self._isNearOrigin(event):
                self._clickedOnOrigin(event)
                return
        elif self._isNearTopOfYAxis(event):
                self._clickedOnTopOfAxis(event)
                return

        for index, candle in enumerate(self.plotSolver.GetCandleData()): 
            if self._isNearMaximum(event, candle):
                self._clickedOnMaximum(event, index, candle)
                break
            elif self._isNearMinimum(event, candle):
                self._clickedOnMinimum(event, index, candle)
                break
            elif self._isNearClosingEdge(event, candle):
                self._clickedOnClosingEdge(event, index, candle)
                break      
            elif self._isNearOpeningEdge(event, candle):
                self._clickedOnOpeningEdge(event, index, candle)
                break
            elif self._isNearLeftEdge(event, candle):
                self._clickedOnLeftEdge(event,index, candle)
                break
            elif self._isNearRightEdge(event, candle):
                self._clickedOnRightEdge(event,index, candle)
                break
            elif self._isNearOrigin(event):
                self._clickedOnOrigin(event)

    @inheritdocstring(EventHandler.on_left_up)
    def on_left_up(self, event: tk.Event):
        self.eventRegistersLeft.reset()
    
    #######################
    # Mouse move handling #
    #######################

    @inheritdocstring(EventHandler.on_mouse_move)
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
        """Updates cursor appearance based on mouse position over candlestick elements.
        
        Changes the cursor to indicate what action is possible at the current location:
        - fleur: Near the chart origin (pan operation)
        - sb_v_double_arrow: Near Y-axis top (resize axis height)
        - cross: Near candle min/max points (adjust extremes)
        - hand2: Near left edge of candle (adjust spacing)
        - sb_h_double_arrow: Near right edge of candle (adjust width)
        - sb_v_double_arrow: Near opening/closing edges (adjust values)
        - arrow: Default cursor for empty areas
        """
        assert self.canvas
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

    @inheritdocstring(EventHandler.on_right_up)
    def on_right_up(self, event: tk.Event):
        return
    
    @inheritdocstring(EventHandler.on_right_down)
    def on_right_down(self, event: tk.Event):
        assert self.elementMenu
        for index, candle in enumerate(self.plotSolver.GetCandleData()):
            if self._isInsideOfCandle(event, candle):
                self.eventRegistersRight.indexToChange = index
                self.elementMenu.post(event.x_root, event.y_root) 
                return
        super().on_right_down(event)
    
    def _changePositiveColor(self):
        """Shows the user the option to change positive colors of candlesticks.
        """
        color = colorchooser.askcolor(title="Choose different color")
        if color[1] == None:
            return
        self.plotSolver.ChangePositiveColor(color[1])
        self._updateCanvas()
    
    def _changeNegativeColor(self):
        """Shows the user the option to change negative colors of candlesticks.
        """
        color = colorchooser.askcolor(title="Choose different color")
        if color[1] == None:
            return
        self.plotSolver.ChangeNegativeColor(color[1])
        self._updateCanvas()

    def _changeName(self):
        """Shows dialog to the user for changing candlestick name. 
        """
        currentName = self.plotSolver.GetName(self.eventRegistersRight.indexToChange)
        newName = simpledialog.askstring("Change name", "New name:", initialvalue=currentName)
        if newName == None:
            return
        self.plotSolver.ChangeName(self.eventRegistersRight.indexToChange, newName)
        self._updateCanvas()
        self._updateDataView()
        pass

    def _switchNameVisibility(self):
        """Allows the user to change visibility of candlesticks's name.
        """
        self.plotSolver.SwitchNameVisibility(self.eventRegistersRight.indexToChange)
        self._updateCanvas()
    
    ##################################
    # Predicates for locating events #
    ##################################
    
    def _isNearClosingEdge(self, event: tk.Event, candle : ValueCandle):
        """Is cursor near closing edge of the candle?

        Args:
            event (tk.Event): Cursor position
            candle (ValueCandle): Candle to test

        Returns:
            bool: True if cursor is near the clsoing edge of the candle.
        """
        origin = self.plotSolver.GetOrigin()
        closingY = self.canvasHeight - (candle.closingCorner.Y + origin.Y)
        return isNear(closingY, event.y) and candle.openingCorner.X <= event.x <= candle.closingCorner.X

    def _isNearOpeningEdge(self, event: tk.Event, candle : ValueCandle):
        """Is cursor near opening edge of the candle?

        Args:
            event (tk.Event): Cursor position
            candle (ValueCandle): Candle to test

        Returns:
            bool: True if cursor is near the opening edge of the candle.
        """
        origin = self.plotSolver.GetOrigin()
        openingY = self.canvasHeight - (candle.openingCorner.Y + origin.Y)
        return isNear(openingY, event.y) and candle.openingCorner.X <= event.x <= candle.closingCorner.X

    def _isNearLeftEdge(self, event: tk.Event, candle : ValueCandle):
        """Checks whether the cursor is close to a candle's left edge.

        Args:
            event (tk.Event): Mouse event to evaluate.
            candle (ValueCandle): Candle to test against.

        Returns:
            bool: True if the cursor is near the candle's left edge.
        """
        origin = self.plotSolver.GetOrigin()
        candleBottomY, candleTopY = self.canvasHeight - (min(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y), self.canvasHeight - (max(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y)
        return isNear(event.x, candle.openingCorner.X) and candleTopY <= event.y <= candleBottomY

    def _isNearRightEdge(self, event: tk.Event, candle : ValueCandle):
        """Checks whether the cursor is close to a candle's right edge.

        Args:
            event (tk.Event): Mouse event to evaluate.
            candle (ValueCandle): Candle to test against.

        Returns:
            bool: True if the cursor is near the candle's right edge.
        """
        origin = self.plotSolver.GetOrigin()
        candleBottomY, candleTopY = self.canvasHeight - (min(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y), self.canvasHeight - (max(candle.openingCorner.Y, candle.closingCorner.Y)+origin.Y)
        return isNear(event.x, candle.closingCorner.X) and candleTopY <= event.y <= candleBottomY
      
    def _isNearMaximum(self, event: tk.Event, candle : ValueCandle):
        """Checks whether the cursor is close to a candle's maximum.

        Args:
            event (tk.Event): Mouse event to evaluate.
            candle (ValueCandle): Candle to test against.

        Returns:
            bool: True if the cursor is near the maximum point.
        """
        origin = self.plotSolver.GetOrigin()
        maxY = self.canvasHeight - (candle.wickTop.Y + origin.Y)
        return isNear(maxY, event.y) and isNear(candle.wickTop.X, event.x)
        

    def _isNearMinimum(self, event: tk.Event, candle : ValueCandle):
        """Checks whether the cursor is close to a candle's minimum.

        Args:
            event (tk.Event): Mouse event to evaluate.
            candle (ValueCandle): Candle to test against.

        Returns:
            bool: True if the cursor is near the minimum point.
        """
        origin = self.plotSolver.GetOrigin()
        minY = self.canvasHeight - (candle.wickBottom.Y + origin.Y)
        return isNear(minY, event.y) and isNear(candle.wickBottom.X, event.x)
    
    def _isNearOrigin(self, event: tk.Event):
        """Checks whether the cursor is close to the chart origin.

        Args:
            event (tk.Event): Mouse event to evaluate.

        Returns:
            bool: True if the cursor is near the origin point.
        """
        origin = self.plotSolver.GetOrigin()
        return isNear(event.x, origin.X) and isNear(event.y, self.canvasHeight - origin.Y)
    
    def _isNearTopOfYAxis(self,event: tk.Event):
        """Checks whether the cursor is near the top of the vertical axis.

        Args:
            event (tk.Event): Mouse event to evaluate.

        Returns:
            bool: True if the cursor is near the axis top handle.
        """
        topNormalized = self.canvasHeight - self.plotSolver.GetAxisHeight() - self.plotSolver.GetOrigin().Y
        return isNear(event.y, topNormalized, 10) and isNear(event.x, self.plotSolver.GetOrigin().X, 10)
    
    def _isInsideOfCandle(self,event: tk.Event, candle : ValueCandle):
        """Checks whether the cursor is inside a candle's bounding area.

        Args:
            event (tk.Event): Mouse event to evaluate.
            candle (ValueCandle): Candle to test against.

        Returns:
            bool: True if the cursor lies within the candle area.
        """
        originY = self.plotSolver.GetOrigin().Y
        xCoordinateOK = candle.leftBottom.X <= event.x <= candle.rightTop.X
        bottomY = candle.openingCorner.Y if candle.openingCorner.Y <= candle.closingCorner.Y else candle.closingCorner.Y
        topY = candle.closingCorner.Y if candle.openingCorner.Y <= candle.closingCorner.Y else candle.openingCorner.Y
        topY, bottomY = self.canvasHeight - bottomY - originY, self.canvasHeight - topY - originY
        yCoordinateOK = bottomY <= event.y <= topY
        return yCoordinateOK and xCoordinateOK
