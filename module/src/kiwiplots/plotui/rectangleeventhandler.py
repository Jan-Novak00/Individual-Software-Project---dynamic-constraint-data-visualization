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

class RectangleEventHandler(EventHandler,ABC):
    class RectangleEventRegistersLeftButton(EventHandler.EventRegistersLeftButton):
        class RectangleLeftEvents(Enum):
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
        
        def reset(self) -> None:
            super().reset()
            self.eventType = RectangleEventHandler.RectangleEventRegistersLeftButton.RectangleLeftEvents.nothing
    
    class RectangleEventRegistersRightButton(EventHandler.EventRegistersRightButton):
        pass
    
    LeftEvents: TypeAlias = RectangleEventRegistersLeftButton.RectangleLeftEvents

    def __init__(self, plotMetadata: PlotMetadata, solver: RectangleSolver) -> None:
        """_summary_

        Args:
            plotMetadata (BarChartMetadata): _description_
            solver (BarChartSolver): _description_
        """
        super().__init__(plotMetadata)
        self.plotSolver : RectangleSolver = solver 
        self.canvasHeight : int  = 0
        self._createTranslationTable(solver.GetGroupData()) 
        self.eventRegistersLeft : RectangleEventHandler.RectangleEventRegistersLeftButton = RectangleEventHandler.RectangleEventRegistersLeftButton()
        self.eventRegistersRight : RectangleEventHandler.RectangleEventRegistersRightButton = RectangleEventHandler.RectangleEventRegistersRightButton()

    def _createTranslationTable(self, groups : list[list]):
        self.translationTable = []
        for groupIndex, group in enumerate(groups):
            for itemIndex in range(len(group)):
                self.translationTable.append((groupIndex,itemIndex))
    
    def _isEventTypeValueChange(self) -> bool:
        return self.eventRegistersLeft.eventType == RectangleEventHandler.RectangleEventRegistersLeftButton.RectangleLeftEvents.height

    @abstractmethod
    def initializeDataView(self, textWindow: Text) -> None:
        return
    
    @abstractmethod
    def initializeCanvas(self, canvas: Canvas, width: int, height: int) -> None:
        return
    
    @abstractmethod
    def initializeRightClickMenu(self, menu: tk.Menu) -> None:
        return
    
    @abstractmethod
    def initializeDefaultRightClickMenu(self, menu: tk.Menu) -> None:
        return
    
    ########################
    # Left click handeling #
    ########################
    
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
    
    def on_left_up(self, event: tk.Event):
        self.eventRegistersLeft.reset()
    
    def _clickedOnOrigin(self, event):
        self.eventRegistersLeft.eventType = self.LeftEvents.origin
        
    def _clickedOnRightEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle):
        """
        Registers that the user clicked on a right edge of some rectangle
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.width
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x, event.y)
        self.eventRegistersLeft.dragIndex = rectangleIndex
        self.eventRegistersLeft.originalLeftX = rectangle.leftBottom.X
    
    def _clickedOnLeftEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle): 
        """
        Registers that the user clicked on a left edge of some rectangle
        """
        groupIndex = self._indexToGroupIndex(rectangleIndex)

        self.eventRegistersLeft.eventType = self.LeftEvents.spacing if groupIndex[1] == 0 else self.LeftEvents.innerSpacing #"left" + ("Most" if groupIndex[1] == 0 else "Middle")
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x, event.y)
        self.eventRegistersLeft.dragIndex = rectangleIndex
        
        self.eventRegistersLeft.originalLeftX = rectangle.leftBottom.X
        self.eventRegistersLeft.originalSpacing = self.plotSolver.GetSpacing()
    
    def _clickedOnTopEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle):
        """
        Registers that the user clicked on a top edge of some rectangle
        """
        self.eventRegistersLeft.eventType = self.LeftEvents.height
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x, event.y)
        self.eventRegistersLeft.dragIndex = rectangleIndex
        self.eventRegistersLeft.originalHeight = rectangle.rightTop.Y - rectangle.leftBottom.Y
    
    def _clickedOnTopOfAxis(self, event):
        self.eventRegistersLeft.eventType = self.LeftEvents.axisTop
    
    ########################
    # Right mouse handling #
    ########################
    def on_right_up(self, event: tk.Event) -> None:
        return
    
    def on_right_down(self, event: tk.Event) -> None:
        assert self.elementMenu
        for index, rec in enumerate(self.plotSolver.GetRectangleDataAsList()):
            if self._isInsideOfRectangle(event, rec):
                self.eventRegistersRight.rectangleIndexToChange = index
                self.elementMenu.post(event.x_root, event.y_root)
                return
        super().on_right_down(event) 

    def _changeColor(self):
        groupIndex = self._indexToGroupIndex(self.eventRegistersRight.rectangleIndexToChange)
        color = colorchooser.askcolor(title="Choose different color")
        if color[1] == None:
            return
        self.plotSolver.ChangeColor(groupIndex[0],groupIndex[1],color[1])
        self._updateCanvas()

    def _changeName(self):
        groupIndex = self._indexToGroupIndex(self.eventRegistersRight.rectangleIndexToChange)
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

    def on_mouse_move(self, event):
        """
        If method on_mouse_down registered an event near to some edge of some rectangle, then this method mekes appropriate changes toi the graph if the user has moved with mouse.
        """
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
        return super().check_cursor(event)
    
    ##################################
    # Predicates for locating events #
    ##################################

    def _isNearRightEdge(self, event, rectangle: ValueRectangle):
        """
        Returns True, if for given rectangle the event happened near to the right edge of the rectangle.
        For more information, see _isNear method.
        """
        leftBottomYNormalized = self.canvasHeight - rectangle.leftBottom.Y # Canvas coordinates are flipped, "Normalized" values are real y values on the canvas.
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        return isNear(event.x, rectangle.rightTop.X,3) and rightTopYNormalized <= event.y <= leftBottomYNormalized
    
    def _isNearLeftEdge(self, event, rectangle: ValueRectangle):
        """
        Returns True, if for given rectangle the event happened near to the left edge of the rectangle.
        For more information, see _isNear method.
        """
        leftBottomYNormalized = self.canvasHeight - rectangle.leftBottom.Y
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        return isNear(event.x, rectangle.leftBottom.X, 10) and rightTopYNormalized <= event.y <= leftBottomYNormalized

    def _isNearTopEdge(self, event, rectangle: ValueRectangle):
        """
        Returns True, if for given rectangle the event happened near to the top edge of the rectangle.
        For more information, see _isNear method.
        """
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        return isNear(event.y, rightTopYNormalized) and rectangle.leftBottom.X <= event.x <= rectangle.rightTop.X
    
    def _isNearOrigin(self, event):
        origin = self.plotSolver.GetOrigin()
        return isNear(event.x, origin.X) and isNear(event.y, self.canvasHeight - origin.Y)

    def _isInsideOfRectangle(self,event, rectangle: ValueRectangle):
        rightTopYNormalized = self.canvasHeight - rectangle.rightTop.Y
        leftBottomYNormalized = self.canvasHeight - rectangle.leftBottom.Y
        return (rectangle.leftBottom.X <= event.x <= rectangle.rightTop.X) \
                and (rightTopYNormalized <= event.y <= leftBottomYNormalized)
    
    def _isNearTopOfYAxis(self,event):
        topNormalized = self.canvasHeight - self.plotSolver.GetAxisHeight() - self.plotSolver.GetOrigin().Y
        return isNear(event.y, topNormalized, 10) and isNear(event.x, self.plotSolver.GetOrigin().X, 10)
    
    ##################
    # Logic wrappers #
    ##################
    def _indexToGroupIndex(self, index: int):
        if index >= len(self.translationTable):
            raise Exception(f"Index {index} is too large to translate into group coordinates. There are only {len(self.translationTable)} rectangles.")
        return self.translationTable[index]