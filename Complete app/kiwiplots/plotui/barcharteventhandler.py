import tkinter as tk
from typing import Union
from .canvasdrawers import BarChartCanvasDrawer
from .eventhandlers import EventHandler
from kiwiplots.solvers import BarChartSolver
from .plotmetadata import BarChartMetadata
from .plotmath import isNear
from .dataviewers import BarChartDataViewer
from kiwiplots.plotelement import ValueRectangle, ValuePoint2D
from tkinter import simpledialog
from tkinter import colorchooser
from enum import Enum
from typing import TypeAlias

class BarChartEventHandler(EventHandler):
    class BarEventRegistersLeftButton(EventHandler.EventRegistersLeftButton):
        class BarLeftEvents(Enum):
            nothing      = 0
            height       = 1
            origin       = 2
            axisTop      = 3
            width        = 4 #aka right
            spacing      = 5 #aka leftMost
            innerSpacing = 6
        
        def __init__(self):
            super().__init__()
            self.eventType: "BarChartEventHandler.BarEventRegistersLeftButton.BarLeftEvents" = BarChartEventHandler.BarEventRegistersLeftButton.BarLeftEvents.nothing
        
        def reset(self) -> None:
            super().reset()
            self.eventType = BarChartEventHandler.BarEventRegistersLeftButton.BarLeftEvents.nothing
    
    class BarEventRegistersRightButton(EventHandler.EventRegistersRightButton):
        pass
    
    LeftEvents: TypeAlias = BarEventRegistersLeftButton.BarLeftEvents

    ###################
    # Inicialization #
    ###################

    def __init__(self, plotMetadata: BarChartMetadata, solver: BarChartSolver) -> None:
        super().__init__(plotMetadata)
        self.plotSolver : BarChartSolver = solver  # type: ignore
        self.canvasHeight : int = None # type: ignore
        self._createTranslationTable(solver.GetRectangleData()) # type: ignore
        self.eventRegistersLeft : BarChartEventHandler.BarEventRegistersLeftButton = BarChartEventHandler.BarEventRegistersLeftButton()
        self.eventRegistersRight : BarChartEventHandler.BarEventRegistersRightButton = BarChartEventHandler.BarEventRegistersRightButton()

    def initializeDataView(self, textWindow: tk.Text) -> None:
        self.dataViewer = BarChartDataViewer(textWindow)
    
    def initializeCanvas(self, canvas: tk.Canvas, width: int, height: int) -> None:
        self.canvas = canvas
        self.canvasHeight = height
        self.drawer = BarChartCanvasDrawer(canvas,width,height)
    
    def initializeRightClickMenu(self, menu: tk.Menu) -> None:
        self.elementMenu = menu
        self.elementMenu.add_command(label="Change color", command=self._changeColor)
        self.elementMenu.add_command(label="Change name", command=self._changeName)
    
    def _createTranslationTable(self, heights: Union[list[float], list[tuple[float, ...]]]): # ToDo better system required - will stop working once ability to change number of rectangles is added
        self.translationTable = []
        for groupIndex, group in enumerate(heights):
            for itemIndex in range(len(group)): # pyright: ignore[reportArgumentType]
                self.translationTable.append((groupIndex,itemIndex))
    
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
        
        groups = self.plotSolver.GetRectangleData()
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
                self.plotSolver.ChangeHeight(groupIndex, rectangleInGroupIndex, int(newHeight)) # pyright: ignore[reportPossiblyUnboundVariable]
            self._updateDataView()

        elif self.eventRegistersLeft.eventType == self.LeftEvents.spacing:
            self.plotSolver.ChangeSpacingX(groupIndex,rectangleInGroupIndex, event.x)
        
        elif self.eventRegistersLeft.eventType == self.LeftEvents.innerSpacing and rectangleInGroupIndex > 0: # pyright: ignore[reportPossiblyUnboundVariable]
            self.plotSolver.ChangeInnerSpacingX(groupIndex,rectangleInGroupIndex, event.x)

        elif self.eventRegistersLeft.eventType == self.LeftEvents.origin: #done
            self.plotSolver.ChangeOrigin(event.x, self.canvasHeight - event.y)
        
        self._updateCanvas()
        self._updateDataView()
    
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
        self.canvas.config(cursor="arrow")

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
    def _getNewWidth(self,event,groupIndex: int, rectangleInGroupIndex: int, groups: list[list[ValueRectangle]], origin: ValuePoint2D): #THIS IS THE PROBLEMATIC FUNCTION
        return (event.x - self.plotSolver.GetSpacing()*(groupIndex+1) - rectangleInGroupIndex*self.plotSolver.GetInnerSpacing() - sum([self.plotSolver.GetInnerSpacing()*(len(groups[i])-1) for i in range(0,groupIndex)]) - origin.X)//(self.eventRegistersLeft.dragIndex+1)
    
    def _indexToGroupIndex(self, index: int):
        if index >= len(self.translationTable):
            raise Exception(f"Index {index} is too large to translate into group coordinates. There are only {len(self.translationTable)} rectangles.")
        return self.translationTable[index]