import tkinter as tk
from typing import Union, TypeAlias
from .canvasdrawers import LineChartCanvasDrawer
from .eventhandlers import EventHandler
from kiwiplots.solvers import LineChartSolver
from .plotmetadata import LineChartMetadata
from .plotmath import isNear
from .dataviewers import *
from kiwiplots.chartelements import ValueLine, ValuePoint2D
from tkinter import messagebox
from tkinter import colorchooser, simpledialog
from enum import Enum

def LineIndexToPointIndex(lineIndex: int, isLeft: bool):
        if isLeft:
            return lineIndex
        else:
            return lineIndex+1

class LineChartEventHandler(EventHandler):

    class LineEndParity(Enum):
        left = 0,
        right = 1

    class LineChartEventRegisterLeftButton(EventHandler.EventRegistersLeftButton):
        class LineLeftEvents(Enum):
            nothing = 0
            height  = 1,
            origin  = 2,
            horizontal = 3,
            axisTop = 5

        def __init__(self):
            super().__init__()
            self.eventType : LineChartEventHandler.LineChartEventRegisterLeftButton.LineLeftEvents = LineChartEventHandler.LineChartEventRegisterLeftButton.LineLeftEvents.nothing
            self.lineEndParity : LineChartEventHandler.LineEndParity|None = None
        
        def reset(self):
            super().reset()
            self.eventType = LineChartEventHandler.LineChartEventRegisterLeftButton.LineLeftEvents.nothing
            self.lineEndParity = None 
    
    class LineChartEventRegistersRightButton(EventHandler.EventRegistersRightButton):
        def __init__(self):
            super().__init__()
        def reset(self):
            self.pointIndex : int|None = None

    class EditMode(Enum):
        VALUE = 0,
        HORIZONTAL = 1
    
    LeftEvents : TypeAlias = LineChartEventRegisterLeftButton.LineLeftEvents

    

    ###################
    # Initialization #
    ###################
    
    def __init__(self, plotMetadata: LineChartMetadata, solver: LineChartSolver):
        super().__init__(plotMetadata)
        self.plotSolver: LineChartSolver = solver
        self.canvasHeight : int = None # pyright: ignore[reportAttributeAccessIssue]
        self.mode : LineChartEventHandler.EditMode = LineChartEventHandler.EditMode.VALUE
        self.plotMetadata : LineChartMetadata = self.plotMetadata
        self.eventRegistersLeft : LineChartEventHandler.LineChartEventRegisterLeftButton =  LineChartEventHandler.LineChartEventRegisterLeftButton()
        self.eventRegistersRight : LineChartEventHandler.LineChartEventRegistersRightButton = LineChartEventHandler.LineChartEventRegistersRightButton()

    def _isEventTypeValueChange(self) -> bool:
        return self.eventRegistersLeft.eventType == self.LeftEvents.height

    def initializeDataView(self, textWindow: tk.Text) -> None:
        self.dataViewer = LineChartDataViewer(textWindow)
    
    def initializeCanvas(self, canvas: tk.Canvas, width: int, height: int) -> None:
        self.canvas = canvas
        self.canvasHeight = height
        self.drawer = LineChartCanvasDrawer(canvas, width, height)
    
    def initializeRightClickMenu(self, menu: tk.Menu) -> None:
        self.elementMenu = menu
        self.elementMenu.add_command(label="Change color", command=self._changeColor)
        self.elementMenu.add_command(label="Change name", command=self._changeName)
        return
    
    def initializeDefaultRightClickMenu(self, menu: tk.Menu) -> None:
        super().initializeDefaultRightClickMenu(menu)
        self.valueModeLabel = "Switch to value modification mode"
        self.horizontalModeLabel = "Switch to horizontal layout modification mode"
        
        assert self.defaultMenu is not None
        self.defaultMenu.add_command(command=self._changeMode)
        self.changeModeIndex = self.defaultMenu.index("end")
        assert self.changeModeIndex is not None
        self.defaultMenu.entryconfig(self.changeModeIndex,label=self.horizontalModeLabel)
        self.defaultMenu.add_command(label="Add point", command=self._addPoint)


    def _changeMode(self):
        assert self.defaultMenu is not None
        assert self.changeModeIndex is not None
        print ("change mode index: ",self.changeModeIndex)
        if self.mode == LineChartEventHandler.EditMode.VALUE:
            self.mode = LineChartEventHandler.EditMode.HORIZONTAL
            self.defaultMenu.entryconfig(self.changeModeIndex,label=self.valueModeLabel)
        else:
            self.mode = LineChartEventHandler.EditMode.VALUE
            self.defaultMenu.entryconfig(self.changeModeIndex,label=self.horizontalModeLabel)
    
    def _changeColor(self):
        color = colorchooser.askcolor(title="Choose different color")
        if color[1] == None:
            return
        self.plotMetadata.color = color[1]
        self._updateCanvas()
    
    def _changeName(self):
        assert self.eventRegistersRight.pointIndex is not None
        name = simpledialog.askstring(title="Change name", prompt="New name:")
        if name == None:
            return
        self.plotSolver.ChangeName(self.eventRegistersRight.pointIndex, name)
        self._updateCanvas()
        self._updateDataView()

    def _addPoint(self):
        def createPopUp():
            assert self.canvas is not None
            popup = tk.Toplevel()
            popup.resizable(True, False)
            popup.title("Add new point")
            tk.Label(popup, text="Name:").pack(anchor="w", padx=10, pady=(10,0))
            nameEntry = tk.Entry(popup)
            nameEntry.pack(fill="x", padx=10)
            tk.Label(popup, text="Value:").pack(anchor="w", padx=10, pady=(10,0))
            valueEntry = tk.Entry(popup)
            valueEntry.pack(fill="x", padx=10)

            name = None
            value = None

            def commit():
                nonlocal name, value
                name = nameEntry.get()
                try:
                    value = float(valueEntry.get())
                    if name == "":
                        name = None
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error","Invalid name or value.")
                else:
                    popup.destroy()
            def cancel():
                nonlocal name, value
                name, value = None, None
                popup.destroy()
            buttonFrame = tk.Frame(popup)
            buttonFrame.pack(pady=10)
            tk.Button(buttonFrame, text="OK", command=commit).pack(side="left", padx=5)
            tk.Button(buttonFrame, text="Cancel",command=cancel).pack(side="right", padx=5)
            popup.grab_set()
            self.canvas.wait_window(popup)
            return name, value
        newName, newValue = createPopUp()
        if newName == None or newValue == None:
            return
        self.plotSolver.AddPoint(value = newValue * self.plotMetadata.heightScaleFactor, name = newName)
        self.UpdateUI()

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
        self.eventRegistersLeft.eventType = self.LeftEvents.height if self.mode == LineChartEventHandler.EditMode.VALUE else self.LeftEvents.horizontal
        self.eventRegistersLeft.lineEndParity = self.LineEndParity.left if leftEdge else self.LineEndParity.right
        self.eventRegistersLeft.dragIndex = index
        self.eventRegistersLeft.dragStart = ValuePoint2D(event.x,event.y)
    
    def _clickedOnOrigin(self, event: tk.Event):
        self.eventRegistersLeft.eventType = self.LeftEvents.origin
    
    def _clickedOnTopOfAxis(self, event: tk.Event):
        self.eventRegistersLeft.eventType = self.LeftEvents.axisTop

    #######################
    # Mouse move handling #
    #######################

    def on_mouse_move(self, event: tk.Event) -> None:
        if self.eventRegistersLeft.eventType == self.LeftEvents.nothing:
            return
        
        origin = self.plotSolver.GetOrigin()
        points = self.plotSolver.GetPoints()

        if self.eventRegistersLeft.eventType == self.LeftEvents.height:
            pointIndex = self.eventRegistersLeft.dragIndex
            self.plotSolver.ChangeHeight(pointIndex,self.canvasHeight - event.y - origin.Y)

        
        elif self.eventRegistersLeft.eventType == self.LeftEvents.horizontal and self.eventRegistersLeft.dragIndex != 0:
            newX = event.x #- self.plotSolver.GetPadding()
            if newX >= 5:
                #self.plotSolver.ChangeWidth(newWidth)
                self.plotSolver.ChangeWidthX(self.eventRegistersLeft.dragIndex, newX)
        
        elif self.eventRegistersLeft.eventType == self.LeftEvents.horizontal and self.eventRegistersLeft.dragIndex == 0:
            #newPadding = event.x - origin.X TOTO NEPOUZIVAT
            #if newPadding >= 0:
                #self.plotSolver.ChangePadding(newPadding)
            newX = event.x
            self.plotSolver.ChangePaddingX(newX)

        elif self.eventRegistersLeft.eventType == self.LeftEvents.origin:
            self.plotSolver.ChangeOrigin(event.x, self.canvasHeight - event.y)
            print("Origin: ", origin)
        
        elif self.eventRegistersLeft.eventType == self.LeftEvents.axisTop:  
            newHeight = self.canvasHeight - event.y - origin.Y
            if newHeight > 10:
                self.plotSolver.ChangeAxisHeight(int(newHeight))
        
        
        self._updateCanvas()
        self._updateDataView()

    
    def check_cursor(self, event: tk.Event) -> None:
        assert self.canvas
        if self._isNearOrigin(event):
            self.canvas.config(cursor="fleur")
            return
        elif self._isNearTopOfYAxis(event):
            self.canvas.config(cursor="sb_v_double_arrow")
            return
        
        points = self.plotSolver.GetPoints()
        for index, point in enumerate(points):
            if self._isNearLineEnd(event,point):
                if self.mode == LineChartEventHandler.EditMode.VALUE:
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
        assert self.elementMenu
        assert self.defaultMenu
        print("on_right_down triggered")
        lines = self.plotSolver.GetLineData()
        for index, line in enumerate(lines):
            point : ValuePoint2D = line.leftEnd
            if self._isNearLineEnd(event,point):
                self.eventRegistersRight.pointIndex = index
                print("self.eventRegistersRight.pointIndex = ", "index ",index)
                self.elementMenu.post(event.x_root, event.y_root)
                return
            if (index == len(lines)-1):
                point : ValuePoint2D = line.rightEnd
                if self._isNearLineEnd(event,point):
                    self.eventRegistersRight.pointIndex = index + 1
                    print("self.eventRegistersRight.pointIndex = ", "index ",index+1)
                    self.elementMenu.post(event.x_root, event.y_root)
                    return
        self.defaultMenu.post(event.x_root,event.y_root)
    
    ##################################
    # Predicates for locating events #
    ##################################

    def _isNearLineEnd(self,event: tk.Event, point: ValuePoint2D)->bool:
        xLeft, yLeft = point.X, self.canvasHeight - (point.Y)
        return isNear(xLeft,event.x) and isNear(yLeft,event.y)
    
    def _isNearOrigin(self, event: tk.Event):
        origin = self.plotSolver.GetOrigin()
        return isNear(event.x, origin.X) and isNear(event.y, self.canvasHeight - origin.Y)
    
    def _isNearTopOfYAxis(self,event: tk.Event):
        topNormalized = self.canvasHeight - self.plotSolver.GetAxisHeight() - self.plotSolver.GetOrigin().Y
        return isNear(event.y, topNormalized, 10) and isNear(event.x, self.plotSolver.GetOrigin().X, 10)
    