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

def LineIndexToPointIndex(lineIndex: int, isLeft: bool):
        if isLeft:
            return lineIndex
        else:
            return lineIndex+1



class LineChartEventHandler(EventHandler):

    class LineChartEventRegisterLeftButton(EventHandler.EventRegistersLeftButton):
        def reset(self):
            super().reset()
            self.lineEndParity : str = None # pyright: ignore[reportAttributeAccessIssue] # left or right 

    ###################
    # Initialization #
    ###################
    
    def __init__(self, plotMetadata: LineChartMetadata, solver: LineChartSolver):
        super().__init__(plotMetadata)
        self.plotSolver: LineChartSolver = solver
        self.canvasHeight : int = None # pyright: ignore[reportAttributeAccessIssue]
        self.mode = "value"
        self.plotMetadata : LineChartMetadata = self.plotMetadata
        self.eventRegistersLeft : LineChartEventHandler.LineChartEventRegisterLeftButton =  LineChartEventHandler.LineChartEventRegisterLeftButton()

    def initializeDataView(self, textWindow: tk.Text) -> None:
        self.dataViewer = LineChartDataViewer(textWindow)
    
    def initializeCanvas(self, canvas: tk.Canvas, width: int, height: int) -> None:
        self.canvas = canvas
        self.canvasHeight = height
        self.drawer = LineChartCanvasDrawer(canvas, width, height)
    
    def initializeRightClickMenu(self, menu: tk.Menu) -> None:
        self.elementMenu = menu
        self.elementMenu.add_command(label="Change color", command=self._changeColor)
        return
    
    def initializeDefaultRightClickMenu(self, menu: tk.Menu) -> None:
        super().initializeDefaultRightClickMenu(menu)
        self.defaultMenu.add_command(label="Change mode", command=self._changeMode)


    def _changeMode(self):
        print("CLICK")
        if self.mode == "value":
            self.mode = "width"
        else:
            self.mode = "value"
    
    def _changeColor(self):
        color = colorchooser.askcolor(title="Choose different color")
        if color[1] == None:
            return
        self.plotMetadata.color = color[1] # pyright: ignore[reportAttributeAccessIssue]
        self._updateCanvas()

    ########################
    # Left click handeling #
    ########################

    def on_left_down(self, event: tk.Event) -> None:
        if self._isNearOrigin(event):
                self._clickedOnOrigin(event)
                return
        elif self._isNearTopOfYAxis(event):
                self._clickedOnTopOfAxis(event)
                return

        points = self.plotSolver.GetPoints()
        for index, point in enumerate(points):
            if self._isNearLineEnd(event,point):
                print(f"Clicked point ({point.X}, {point.Y}) at line with index {index}.")
                self._clickedOnLineEnd(event, index, index == 0)

        return

    
    def on_left_up(self, event: tk.Event) -> None:
        self.eventRegistersLeft.reset()
    
    def _clickedOnLineEnd(self, event: tk.Event, index: int, leftEdge: bool):
        self.eventRegistersLeft.eventType = "value" if self.mode == "value" else "width"
        self.eventRegistersLeft.lineEndParity = "left" if leftEdge else "right"
        self.eventRegistersLeft.dragIndex = index
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x,event.y)
    
    def _clickedOnOrigin(self, event: tk.Event):
        self.eventRegistersLeft.eventType = "origin"
    
    def _clickedOnTopOfAxis(self, event: tk.Event):
        self.eventRegistersLeft.eventType = "axisTop"

    #######################
    # Mouse move handling #
    #######################

    def on_mouse_move(self, event: tk.Event) -> None:
        if self.eventRegistersLeft.eventType is None:
            return
        
        origin = self.plotSolver.GetOrigin()
        points = self.plotSolver.GetPoints()

        if self.eventRegistersLeft.eventType == "value":
            pointIndex = self.eventRegistersLeft.dragIndex
            self.plotSolver.ChangeHeight(pointIndex,self.canvasHeight - event.y - origin.Y)

        
        elif self.eventRegistersLeft.eventType == "width" and self.eventRegistersLeft.dragIndex != 0:
            #newWidth = (event.x - origin.X - self.plotSolver.GetPadding())/(self.eventRegistersLeft.dragIndex)
            previousPoint = points[self.eventRegistersLeft.dragIndex - 1]
            newWidth = event.x - origin.X - self.plotSolver.GetPadding()
            if newWidth >= 5:
                #self.plotSolver.ChangeWidth(newWidth)
                self.plotSolver.ChangeX(self.eventRegistersLeft.dragIndex, newWidth)
        
        elif self.eventRegistersLeft.eventType == "width" and self.eventRegistersLeft.dragIndex == 0:
            newPadding = event.x - origin.X
            if newPadding >= 0:
                self.plotSolver.ChangePadding(newPadding)

        elif self.eventRegistersLeft.eventType == "origin":
            self.plotSolver.ChangeOrigin(event.x, self.canvasHeight - event.y)
            print("Origin: ", origin)
        
        elif self.eventRegistersLeft.eventType == "axisTop":  
            newHeight = self.canvasHeight - event.y - origin.Y
            if newHeight > 10:
                self.plotSolver.ChangeAxisHeight(int(newHeight))
        
        
        self._updateCanvas()
        self._updateDataView()

    
    def check_cursor(self, event: tk.Event) -> None:
        if self._isNearOrigin(event):
            self.canvas.config(cursor="fleur")
            return
        elif self._isNearTopOfYAxis(event):
            self.canvas.config(cursor="sb_v_double_arrow")
            return
        
        points = self.plotSolver.GetPoints()
        for index, point in enumerate(points):
            if self._isNearLineEnd(event,point):
                if self.mode == "value":
                    self.canvas.config(cursor="cross")
                else:
                    if index == 0:
                        self.canvas.config(cursor="hand2")
                    else:
                        self.canvas.config(cursor="sb_h_double_arrow")
                return


        self.canvas.config(cursor="arrow")

    ########################
    # Right mouse handling #
    ########################

    def on_right_up(self, event: tk.Event):
        return
    
    def on_right_down(self, event: tk.Event) -> None:
        lines = self.plotSolver.GetLineData()
        for index, line in enumerate(lines):
            point : ValuePoint2D = line.leftEnd
            if self._isNearLineEnd(event,point):
                self.eventRegistersRight.rectangleIndexToChange = index
                self.elementMenu.post(event.x_root, event.y_root)
                return
            if (index == len(lines)-1):
                point : ValuePoint2D = line.rightEnd
                if self._isNearLineEnd(event,point):
                    self.eventRegistersRight.rectangleIndexToChange = index
                    self.elementMenu.post(event.x_root, event.y_root)
                    return
        self.defaultMenu.post(event.x_root,event.y_root)
    
    ##################################
    # Predicates for locating events #
    ##################################

    def _isNearLineEnd(self,event: tk.Event, point: ValuePoint2D)->bool:
        origin = self.plotSolver.GetOrigin()
        xLeft, yLeft = point.X, self.canvasHeight - (point.Y)
        return isNear(xLeft,event.x) and isNear(yLeft,event.y)
    
    def _isNearOrigin(self, event: tk.Event):
        origin = self.plotSolver.GetOrigin()
        return isNear(event.x, origin.X) and isNear(event.y, self.canvasHeight - origin.Y)
    
    def _isNearTopOfYAxis(self,event: tk.Event):
        topNormalized = self.canvasHeight - self.plotSolver.GetAxisHeight() - self.plotSolver.GetOrigin().Y
        return isNear(event.y, topNormalized, 10) and isNear(event.x, self.plotSolver.GetOrigin().X, 10)
    