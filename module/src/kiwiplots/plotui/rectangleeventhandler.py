from tkinter import Canvas, Text
from .eventhandlers import EventHandler
from abc import ABC,abstractmethod
from enum import Enum
from typing import TypeAlias
from .plotmetadata import PlotMetadata
from kiwiplots.solvers import RectangleSolver
import tkinter as tk
from kiwiplots.chartelements import ValuePoint2D, ValueRectangle
from .plotmath import isNear
from tkinter import simpledialog
from tkinter import colorchooser
from kiwiplots.utils import inheritdocstring

class RectangleEventHandler(EventHandler,ABC):
    """
    Abstract base class for handling user interactions with rectangle-based plots (bar charts, histograms).
    
    Manages mouse events for resizing, repositioning, and modifying rectangles on the canvas.
    Handles both left-click drag operations (resizing) and right-click context menus (property changes).
    """
    class RectangleEventRegistersLeftButton(EventHandler.EventRegistersLeftButton):
        """Envent registers for left mouse button.
        """
        class RectangleLeftEvents(Enum):
            """Enumeration of possible left-click events for rectangle manipulation."""
            nothing      = 0
            height       = 1
            origin       = 2
            axisTop      = 3
            width        = 4 #aka right
            spacing      = 5 #aka leftMost
            innerSpacing = 6
        
        def __init__(self):
            super().__init__()
            self.eventType: "RectangleEventHandler.RectangleEventRegistersLeftButton.RectangleLeftEvents" = RectangleEventHandler.RectangleEventRegistersLeftButton.RectangleLeftEvents.nothing
        
        @inheritdocstring(EventHandler.EventRegistersLeftButton.reset)
        def reset(self) -> None:
            super().reset()
            self.eventType = RectangleEventHandler.RectangleEventRegistersLeftButton.RectangleLeftEvents.nothing
    
    class RectangleEventRegistersRightButton(EventHandler.EventRegistersRightButton):
        """Envent registers for left mouse button.
        """
        pass
    
    LeftEvents: TypeAlias = RectangleEventRegistersLeftButton.RectangleLeftEvents

    def __init__(self, plotMetadata: PlotMetadata, solver: RectangleSolver) -> None:
        """Initializes the RectangleEventHandler with plot metadata and solver.

        Args:
            plotMetadata (PlotMetadata): Metadata about the plot including scale factor and axis values.
            solver (RectangleSolver): Solver containing rectangle data for the plot.
        """
        super().__init__(plotMetadata)
        self.plotSolver : RectangleSolver = solver 
        self.canvasHeight : int  = 0
        self._createTranslationTable(solver.GetGroupData()) 
        self.eventRegistersLeft : RectangleEventHandler.RectangleEventRegistersLeftButton = RectangleEventHandler.RectangleEventRegistersLeftButton()
        self.eventRegistersRight : RectangleEventHandler.RectangleEventRegistersRightButton = RectangleEventHandler.RectangleEventRegistersRightButton()

    def _createTranslationTable(self, groups : list[list]):
        """Creates a translation table mapping flat indices to group coordinates.
        
        Maps single indices from GetRectangleDataAsList to (groupIndex, itemInGroupIndex) pairs.
        
        Args:
            groups (list[list]): List of rectangle groups from the solver.
        """
        self.translationTable = []
        for groupIndex, group in enumerate(groups):
            for itemIndex in range(len(group)):
                self.translationTable.append((groupIndex,itemIndex))
    
    @inheritdocstring(EventHandler._isEventTypeValueChange)
    def _isEventTypeValueChange(self) -> bool:
        return self.eventRegistersLeft.eventType == RectangleEventHandler.RectangleEventRegistersLeftButton.RectangleLeftEvents.height

    @abstractmethod
    def initializeDataView(self, textWindow: Text) -> None:
        """Initializes the data viewer component with a text window.
        
        Creates the appropriate DataViewer implementation for rectangle-based plots.
        
        Args:
            textWindow (Text): A tkinter Text widget where plot data will be displayed.
        """
        raise NotImplementedError("Method must be declared in a subclass.")
    
    @abstractmethod
    def initializeCanvas(self, canvas: Canvas, width: int, height: int) -> None:
        """Initializes the canvas drawer with the plot canvas and dimensions.
        
        Creates the appropriate CanvasDrawer implementation for rectangle-based plots.
        
        Args:
            canvas (Canvas): The tkinter Canvas widget for drawing.
            width (int): Width of the canvas in pixels.
            height (int): Height of the canvas in pixels.
        """
        raise NotImplementedError("Method must be declared in a subclass.")
    
    @abstractmethod
    def initializeRightClickMenu(self, menu: tk.Menu) -> None:
        """Initializes the element-specific right-click context menu.
        
        Sets up the menu that appears when right-clicking on a rectangle.
        
        Args:
            menu (tk.Menu): The tkinter Menu widget to use as the element context menu.
        """
        raise NotImplementedError("Method must be declared in a subclass.")
    
    @abstractmethod
    def initializeDefaultRightClickMenu(self, menu: tk.Menu) -> None:
        """Initializes the default right-click context menu.
        
        Sets up the menu that appears when right-clicking on empty canvas area.
        
        Args:
            menu (tk.Menu): The tkinter Menu widget to use as the default context menu.
        """
        raise NotImplementedError("Method must be declared in a subclass.")
    
    ########################
    # Left click handeling #
    ########################
    
    @inheritdocstring(EventHandler.on_left_down)
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
    
    @inheritdocstring(EventHandler.on_left_up)
    def on_left_up(self, event: tk.Event):
        self.eventRegistersLeft.reset()
    
    def _clickedOnOrigin(self, event):
        """Registers a click on the chart origin.
        
        Args:
            event (tk.Event): The tkinter Event object containing mouse coordinates.
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.origin
        
    def _clickedOnRightEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle):
        """Registers a click on the right edge of a rectangle for width resizing.
        
        Args:
            event (tk.Event): The tkinter Event object containing mouse coordinates.
            rectangleIndex (int): Index of the rectangle in flat list.
            rectangle (ValueRectangle): The rectangle geometry data.
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.width
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x, event.y)
        self.eventRegistersLeft.dragIndex = rectangleIndex
        self.eventRegistersLeft.originalLeftX = rectangle.leftBottom.X
    
    def _clickedOnLeftEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle):
        """Registers a click on the left edge of a rectangle for spacing/innerSpacing adjustment.
        
        Args:
            event (tk.Event): The tkinter Event object containing mouse coordinates.
            rectangleIndex (int): Index of the rectangle in flat list.
            rectangle (ValueRectangle): The rectangle geometry data.
        """
        groupIndex = self._indexToGroupIndex(rectangleIndex)

        self.eventRegistersLeft.eventType = self.LeftEvents.spacing if groupIndex[1] == 0 else self.LeftEvents.innerSpacing #"left" + ("Most" if groupIndex[1] == 0 else "Middle")
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x, event.y)
        self.eventRegistersLeft.dragIndex = rectangleIndex
        
        self.eventRegistersLeft.originalLeftX = rectangle.leftBottom.X
        self.eventRegistersLeft.originalSpacing = self.plotSolver.GetSpacing()
    
    def _clickedOnTopEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle):
        """Registers a click on the top edge of a rectangle for height resizing.
        
        Args:
            event (tk.Event): The tkinter Event object containing mouse coordinates.
            rectangleIndex (int): Index of the rectangle in flat list.
            rectangle (ValueRectangle): The rectangle geometry data.
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.height
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x, event.y)
        self.eventRegistersLeft.dragIndex = rectangleIndex
        self.eventRegistersLeft.originalHeight = rectangle.rightTop.Y - rectangle.leftBottom.Y
    
    def _clickedOnTopOfAxis(self, event):
        """Registers a click on the top of the Y-axis for axis height adjustment.
        
        Args:
            event (tk.Event): The tkinter Event object containing mouse coordinates.
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.axisTop
    
    ########################
    # Right mouse handling #
    ########################
    @inheritdocstring(EventHandler.on_right_up)
    def on_right_up(self, event: tk.Event) -> None:
        return
    
    @inheritdocstring(EventHandler.on_right_down)
    def on_right_down(self, event: tk.Event) -> None:
        assert self.elementMenu
        for index, rec in enumerate(self.plotSolver.GetRectangleDataAsList()):
            if self._isInsideOfRectangle(event, rec):
                self.eventRegistersRight.indexToChange = index
                self.elementMenu.post(event.x_root, event.y_root)
                return
        super().on_right_down(event) 

    def _changeColor(self):
        """Prompts user to change the color of the selected rectangle.
        
        Opens a color chooser dialog and updates the rectangle color in the solver.
        """
        groupIndex = self._indexToGroupIndex(self.eventRegistersRight.indexToChange)
        color = colorchooser.askcolor(title="Choose different color")
        if color[1] == None:
            return
        self.plotSolver.ChangeColor(groupIndex[0],groupIndex[1],color[1])
        self._updateCanvas()

    def _changeName(self):
        """Prompts user to change the name of the selected rectangle.
        
        Opens a text input dialog and updates the rectangle name in the solver.
        """
        groupIndex = self._indexToGroupIndex(self.eventRegistersRight.indexToChange)
        currentName = self.plotSolver.GetName(groupIndex[0],groupIndex[1])
        newName = simpledialog.askstring("Change name", "New name:", initialvalue=currentName)
        if newName == None:
            return
        self.plotSolver.ChangeName(groupIndex[0], groupIndex[1], newName)
        self._updateCanvas()
        self._updateDataView()
    
    #######################
    # Mouse move handling #
    #######################

    @inheritdocstring(EventHandler.on_mouse_move)
    def on_mouse_move(self, event):
        if self.eventRegistersLeft.eventType is None:
            return
        
        groups = self.plotSolver.GetGroupData()
        origin = self.plotSolver.GetOrigin()

        if self.eventRegistersLeft.dragIndex != None:
            groupDragIndex = self._indexToGroupIndex(self.eventRegistersLeft.dragIndex)
            groupIndex, rectangleInGroupIndex = groupDragIndex[0], groupDragIndex[1]

        if self.eventRegistersLeft.eventType == self.LeftEvents.width:
            self.plotSolver.ChangeWidthX(groupIndex,rectangleInGroupIndex, event.x)

        elif self.eventRegistersLeft.eventType == self.LeftEvents.axisTop:  
            newHeight = self.canvasHeight - event.y - origin.Y
            if newHeight > 10:
                self.plotSolver.ChangeAxisHeight(int(newHeight))


        elif self.eventRegistersLeft.eventType == self.LeftEvents.height:
  
            newHeight = self.canvasHeight - event.y - origin.Y
            if newHeight > 0:
                self.plotSolver.ChangeHeight(groupIndex, rectangleInGroupIndex, int(newHeight))
            self._updateDataView()

        elif self.eventRegistersLeft.eventType == self.LeftEvents.spacing:
            self.plotSolver.ChangeSpacingX(groupIndex,rectangleInGroupIndex, event.x)
        
        elif self.eventRegistersLeft.eventType == self.LeftEvents.innerSpacing and rectangleInGroupIndex > 0:
            self.plotSolver.ChangeInnerSpacingX(groupIndex,rectangleInGroupIndex, event.x)

        elif self.eventRegistersLeft.eventType == self.LeftEvents.origin: #done
            self.plotSolver.ChangeOrigin(event.x, self.canvasHeight - event.y)
        
        self._updateCanvas()
        self._updateDataView()
    
    @abstractmethod
    def check_cursor(self, event: tk.Event) -> None:
        """Updates cursor appearance based on mouse position over rectangle edges.
        
        Changes the cursor to indicate what action is possible at the current location.
        
        Args:
            event (tk.Event): The tkinter Event object containing current mouse coordinates.
        """
        raise NotImplementedError("Method must be declared in a subclass.")
    
    ##################################
    # Predicates for locating events #
    ##################################

    def _isNearRightEdge(self, event, rectangle: ValueRectangle):
        """Checks if the event occurred near the right edge of a rectangle.
        
        Args:
            event (tk.Event): The tkinter Event object containing mouse coordinates.
            rectangle (ValueRectangle): The rectangle to check.
            
        Returns:
            bool: True if event is within 3 pixels of the right edge and within the rectangle's vertical bounds.
        """
        leftBottomYNormalized = self.canvasHeight - rectangle.leftBottom.Y # Canvas coordinates are flipped, "Normalized" values are real y values on the canvas.
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        return isNear(event.x, rectangle.rightTop.X,3) and rightTopYNormalized <= event.y <= leftBottomYNormalized
    
    def _isNearLeftEdge(self, event, rectangle: ValueRectangle):
        """Checks if the event occurred near the left edge of a rectangle.
        
        Args:
            event (tk.Event): The tkinter Event object containing mouse coordinates.
            rectangle (ValueRectangle): The rectangle to check.
            
        Returns:
            bool: True if event is within 10 pixels of the left edge and within the rectangle's vertical bounds.
        """
        leftBottomYNormalized = self.canvasHeight - rectangle.leftBottom.Y
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        return isNear(event.x, rectangle.leftBottom.X, 10) and rightTopYNormalized <= event.y <= leftBottomYNormalized

    def _isNearTopEdge(self, event, rectangle: ValueRectangle):
        """Checks if the event occurred near the top edge of a rectangle.
        
        Args:
            event (tk.Event): The tkinter Event object containing mouse coordinates.
            rectangle (ValueRectangle): The rectangle to check.
            
        Returns:
            bool: True if event is within the default tolerance of the top edge and within the rectangle's horizontal bounds.
        """
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        return isNear(event.y, rightTopYNormalized) and rectangle.leftBottom.X <= event.x <= rectangle.rightTop.X
    
    def _isNearOrigin(self, event):
        """Checks if the event occurred near the chart origin.
        
        Args:
            event (tk.Event): The tkinter Event object containing mouse coordinates.
            
        Returns:
            bool: True if event is within tolerance of the origin point.
        """
        origin = self.plotSolver.GetOrigin()
        return isNear(event.x, origin.X) and isNear(event.y, self.canvasHeight - origin.Y)

    def _isInsideOfRectangle(self, event, rectangle: ValueRectangle):
        """Checks if the event occurred inside the bounds of a rectangle.
        
        Args:
            event (tk.Event): The tkinter Event object containing mouse coordinates.
            rectangle (ValueRectangle): The rectangle to check.
            
        Returns:
            bool: True if event coordinates are within the rectangle's bounds.
        """
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        leftBottomYNormalized = self.canvasHeight - rectangle.leftBottom.Y
        return (rectangle.leftBottom.X <= event.x <= rectangle.rightTop.X) \
                and (rightTopYNormalized <= event.y <= leftBottomYNormalized)
    
    def _isNearTopOfYAxis(self, event):
        """Checks if the event occurred near the top of the Y-axis.
        
        Args:
            event (tk.Event): The tkinter Event object containing mouse coordinates.
            
        Returns:
            bool: True if event is within tolerance of the axis top point.
        """
        topNormalized = self.canvasHeight - self.plotSolver.GetAxisHeight() - self.plotSolver.GetOrigin().Y
        return isNear(event.y, topNormalized, 10) and isNear(event.x, self.plotSolver.GetOrigin().X, 10)
    
    ##################
    # Logic wrappers #
    ##################
    def _indexToGroupIndex(self, index: int):
        """Converts a flat rectangle index to (groupIndex, itemInGroupIndex) coordinates.
        
        Args:
            index (int): Flat index from GetRectangleDataAsList.
            
        Returns:
            tuple: (groupIndex, itemInGroupIndex) coordinates.
            
        Raises:
            Exception: If index is out of range for the translation table.
        """
        if index >= len(self.translationTable):
            raise Exception(f"Index {index} is too large to translate into group coordinates. There are only {len(self.translationTable)} rectangles.")
        return self.translationTable[index]