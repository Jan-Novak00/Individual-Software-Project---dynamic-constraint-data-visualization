import tkinter as tk
from typing import Union
from .canvasdrawers import HistogramCanvasDrawer
from .eventhandlers import EventHandler
from kiwiplots.solvers import BarChartSolver
from .plotmetadata import BarChartMetadata, HistogramMetadata
from .plotmath import isNear
from .dataviewers import HistogramDataViewer
from kiwiplots.plotelement import ValueRectangle, ValuePoint2D
from tkinter import simpledialog
from tkinter import colorchooser
from .barcharteventhandler import BarChartEventHandler
from enum import Enum
from typing import TypeAlias

class HistogramEventHandler(BarChartEventHandler):

    LeftEvents: TypeAlias = BarChartEventHandler.BarEventRegistersLeftButton.BarLeftEvents
    def __init__(self, plotMetadata: HistogramMetadata, solver: BarChartSolver):
        super().__init__(plotMetadata, solver)

    def initializeDataView(self, textWindow: tk.Text) -> None:
        self.dataViewer = HistogramDataViewer(textWindow)
    
    def initializeCanvas(self, canvas: tk.Canvas, width: int, height: int) -> None:
        self.canvas = canvas
        self.canvasHeight = height
        self.drawer = HistogramCanvasDrawer(canvas,width,height)

    def _clickedOnLeftEdge(self, event, rectangleIndex: int, rectangle: ValueRectangle): 
        """
        Registers that the user clicked on a left edge of some rectangle
        """
        groupIndex = self._indexToGroupIndex(rectangleIndex)
        if groupIndex[1] != 0:
            return
        self.eventRegistersLeft.eventType = self.LeftEvents.spacing
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x, event.y)
        self.eventRegistersLeft.dragIndex = rectangleIndex
        
        self.eventRegistersLeft.originalLeftX = rectangle.leftBottom.X
        self.eventRegistersLeft.originalSpacing = self.plotSolver.GetSpacing()

    def initializeRightClickMenu(self, menu: tk.Menu) -> None:
        self.elementMenu = menu
        self.elementMenu.add_command(label="Change color", command=self._changeColor)

    def check_cursor(self,event):
        """
        Changes cursor according to its position.
        """
        for index, rec in enumerate(self.plotSolver.GetRectangleDataAsList()):
            groupIndex = self._indexToGroupIndex(index)
            if self._isNearLeftEdge(event, rec) and groupIndex[1] == 0:
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
    
