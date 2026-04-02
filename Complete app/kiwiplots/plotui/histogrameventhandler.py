import tkinter as tk
from typing import Union
from .canvasdrawers import HistogramCanvasDrawer
from .eventhandlers import EventHandler
from kiwiplots.solvers import HistogramSolver
from .plotmetadata import BarChartMetadata, HistogramMetadata
from .plotmath import isNear
from .dataviewers import HistogramDataViewer
from kiwiplots.plotelement import ValueRectangle, ValuePoint2D
from tkinter import simpledialog
from tkinter import colorchooser
from .barcharteventhandler import BarChartEventHandler
from enum import Enum
from typing import TypeAlias
from tkinter import messagebox

class HistogramEventHandler(BarChartEventHandler):

    LeftEvents: TypeAlias = BarChartEventHandler.BarEventRegistersLeftButton.BarLeftEvents
    def __init__(self, plotMetadata: HistogramMetadata, solver: HistogramSolver):
        super().__init__(plotMetadata, solver) #pyright: ignore
        self.plotSolver : HistogramSolver = solver

    def initializeDataView(self, textWindow: tk.Text) -> None:
        self.dataViewer = HistogramDataViewer(textWindow)
    
    def initializeCanvas(self, canvas: tk.Canvas, width: int, height: int) -> None:
        self.canvas = canvas
        self.canvasHeight = height
        self.drawer = HistogramCanvasDrawer(canvas,width,height)
    
    def initializeDefaultRightClickMenu(self, menu: tk.Menu) -> None:
        EventHandler.initializeDefaultRightClickMenu(self,menu)
        self.defaultMenu.add_command(label="Append new interval", command=self._addRectangle)
    

    def _addRectangle(self):
        #TODO only one interval
        endOfLastInterval = float(self.plotSolver.GetRectangleDataAsList()[-1].rightTop.secondaryName)
        def createPopUp():
            popup = tk.Toplevel()
            popup.resizable(True, False)
            popup.title(f"Add new value for interval")
            tk.Label(popup, text="New interval end:").pack(anchor="w", padx=10, pady=(10,0))
            endEntry = tk.Entry(popup)
            endEntry.pack(fill="x", padx=10)
            tk.Label(popup, text="Value:").pack(anchor="w", padx=10, pady=(10,0))
            valueEntry = tk.Entry(popup)
            valueEntry.pack(fill="x", padx=10)
            
            end = None
            value = None

            def commit():
                    nonlocal end, value
                    class WrongOrderError(Exception):
                        pass
                    try:
                        value = float(valueEntry.get())
                        end   = float(endEntry.get())
                        if end <= endOfLastInterval:
                            raise WrongOrderError                            
                    except ValueError:
                        messagebox.showerror("Error","Invalid value entered.")
                    except WrongOrderError:
                        messagebox.showerror("Error","New Interval must end after the last existing interval")
                    else:
                        popup.destroy()
            def cancel():
                nonlocal end, value
                end, value = None, None
                popup.destroy()

            buttonFrame = tk.Frame(popup)
            buttonFrame.pack(pady=10)
            tk.Button(buttonFrame, text="OK", command=commit).pack(side="left", padx=5)
            tk.Button(buttonFrame, text="Cancel",command=cancel).pack(side="right", padx=5)
            popup.grab_set()
            self.canvas.wait_window(popup)
            return end, value
        newEnd, newValue = createPopUp()
        if newEnd == None or newValue == None:
            return
        self.plotSolver.AddRectangle(endOfLastInterval,newEnd,newValue*self.plotMetadata.heightScaleFactor)
        self.UpdateUI()
        self._createTranslationTable(self.plotSolver.GetRectangleData()) # pyright: ignore[reportArgumentType]



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
    
