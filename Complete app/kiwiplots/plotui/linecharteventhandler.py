import tkinter as tk
from typing import Union
from .canvasdrawers import LineChartCanvasDrawer
from .eventhandlers import EventHandler
from kiwiplots.solvers import LineChartSolver
from .plotmetadata import LineChartMetadata
from .plotmath import isNear
from .dataviewers import *
from kiwiplots.plotelement import ValueLine, ValuePoint2D
from tkinter import simpledialog
from tkinter import colorchooser

def _lineIndexToPointIndex(lineIndex: int, isLeft: bool):
        if isLeft:
            return lineIndex
        else:
            return lineIndex+1



class LineChartEventHandler(EventHandler):
    ###################
    # Initialization #
    ###################
    
    def __init__(self, plotMetadata: LineChartMetadata, solver: LineChartSolver):
        super().__init__(plotMetadata)
        self.plotSolver: LineChartSolver = solver
        self.canvasHeight : int = None # pyright: ignore[reportAttributeAccessIssue]

    def initializeDataView(self, textWindow: tk.Text) -> None:
        self.dataViewer = LineChartDataViewer(textWindow)
    
    def initializeCanvas(self, canvas: tk.Canvas, width: int, height: int) -> None:
        self.canvas = canvas
        self.canvasHeight = height
        self.drawer = LineChartCanvasDrawer(canvas, width, height)
    
    def initializeRightClickMenu(self, menu: tk.Menu) -> None:
        #ToDo
        return
    
    ########################
    # Left click handeling #
    ########################

    def on_left_down(self, event: tk.Event) -> None:
        lines = self.plotSolver.GetLineData()
        for index, line in enumerate(lines):
            point : ValuePoint2D = line.leftEnd
            if self._isNearLineEnd(event,point):
                print(f"point ({point.X}, {point.Y}) at line with index {index}.")
                self._clickedOnLineEnd(event,index,True)
                return
            if (index == len(lines)-1):
                point : ValuePoint2D = line.rightEnd
                if self._isNearLineEnd(event,point):
                    print(f"point ({point.X}, {point.Y}) at line with index {index}.")
                    self._clickedOnLineEnd(event,index,False)
                    return
    
    def on_left_up(self, event: tk.Event) -> None:
        self.eventRegistersLeft.reset()
    
    def _clickedOnLineEnd(self, event: tk.Event, index: int, leftEdge: bool):
        self.eventRegistersLeft.eventType = "left" if leftEdge else "right"
        self.eventRegistersLeft.dragIndex = index
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x,event.y)

    #######################
    # Mouse move handling #
    #######################

    def on_mouse_move(self, event: tk.Event) -> None:
        print("checkpoint 0")
        if self.eventRegistersLeft.eventType is None:
            return
        
        print("checkpoint 1")
        
        origin = self.plotSolver.GetOrigin()

        if self.eventRegistersLeft.eventType == "left" or self.eventRegistersLeft.eventType == "right":
            pointIndex = _lineIndexToPointIndex(self.eventRegistersLeft.dragIndex,self.eventRegistersLeft.eventType == "left")
            self.plotSolver.ChangeHeight(pointIndex,self.canvasHeight - event.y - origin.Y)
        
        self._updateCanvas()
        self._updateDataView()

    
    def check_cursor(self, event: tk.Event) -> None:
        lines = self.plotSolver.GetLineData()
        for index, line in enumerate(lines):
            point : ValuePoint2D = line.leftEnd
            if self._isNearLineEnd(event,point):
                self.canvas.config(cursor="cross")
                return
            if (index == len(lines)-1):
                point : ValuePoint2D = line.rightEnd
                if self._isNearLineEnd(event,point):
                    self.canvas.config(cursor="cross")
                    return
        self.canvas.config(cursor="arrow")
    
    
    ##################################
    # Predicates for locating events #
    ##################################

    def _isNearLineEnd(self,event: tk.Event, point: ValuePoint2D)->bool:
        origin = self.plotSolver.GetOrigin()
        xLeft, yLeft = point.X, self.canvasHeight - (point.Y + origin.Y)
        
        return isNear(xLeft,event.x) and isNear(yLeft,event.y)

