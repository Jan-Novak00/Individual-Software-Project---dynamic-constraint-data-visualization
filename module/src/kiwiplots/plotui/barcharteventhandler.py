import tkinter as tk
from typing import Union
from .canvasdrawers import BarChartCanvasDrawer
from .eventhandlers import EventHandler
from kiwiplots.solvers import BarChartSolver
from .plotmetadata import BarChartMetadata
from .plotmath import isNear
from .dataviewers import BarChartDataViewer
from kiwiplots.chartelements import ValueRectangle, ValuePoint2D
from tkinter import simpledialog
from tkinter import colorchooser
from enum import Enum
from typing import TypeAlias
from tkinter import messagebox
from .rectangleeventhandler import RectangleEventHandler

class BarChartEventHandler(RectangleEventHandler):
    
    ###################
    # Inicialization #
    ###################

    def __init__(self, plotMetadata: BarChartMetadata, solver: BarChartSolver) -> None:
        """_summary_

        Args:
            plotMetadata (BarChartMetadata): _description_
            solver (BarChartSolver): _description_
        """
        super().__init__(plotMetadata, solver)
        self.plotSolver : BarChartSolver = solver
        self.plotMetadata : BarChartMetadata = plotMetadata

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
        self.elementMenu.add_command(label="Add rectangle to group", command=self._addRectangle)
    
    def initializeDefaultRightClickMenu(self, menu: tk.Menu) -> None:
        EventHandler.initializeDefaultRightClickMenu(self,menu)
        assert self.defaultMenu
        self.defaultMenu.add_command(label="Add rectangle group", command=self._addGroup)
    
    def _addGroup(self):
        def createPopUp():
            assert self.canvas
            popup = tk.Toplevel()
            popup.resizable(True, False)
            popup.title("Add new rectangle group")
            tk.Label(popup, text="Name of the first rectangle:").pack(anchor="w", padx=10, pady=(10,0))
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
        self.plotSolver.AddGroup(newName,newValue * self.plotMetadata.heightScaleFactor)
        self.UpdateUI()
        self._createTranslationTable(self.plotSolver.GetBarData()) # pyright: ignore[reportArgumentType]
    
    def _addRectangle(self):
        groupIndex, _ = self._indexToGroupIndex(self.eventRegistersRight.rectangleIndexToChange)
        def createPopUp():
            assert self.canvas
            popup = tk.Toplevel()
            popup.resizable(True, False)
            popup.title(f"Add new rectangle to group {groupIndex}")
            tk.Label(popup, text="Name of the rectangle:").pack(anchor="w", padx=10, pady=(10,0))
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
        self.plotSolver.AddBar(newName, groupIndex, newValue * self.plotMetadata.heightScaleFactor)
        self.UpdateUI()
        self._createTranslationTable(self.plotSolver.GetBarData()) # pyright: ignore[reportArgumentType]
    

    def _addGroupTEST(self):
        print("adding group!")
        self.plotSolver.AddGroup("newBar",5*self.plotMetadata.heightScaleFactor)
        print("updating UI")
        self.UpdateUI()
        print("group added")
        print("reseting translation table")
        self._createTranslationTable(self.plotSolver.GetBarData()) # pyright: ignore[reportArgumentType]
    
    def _addRectangleTEST1(self):
        print("adding ractangle to the first group")
        self.plotSolver.AddBar("new rec",1,5*self.plotMetadata.heightScaleFactor)
        print("updating UI")
        self.UpdateUI()
        print("reseting translation table")
        self._createTranslationTable(self.plotSolver.GetBarData()) # pyright: ignore[reportArgumentType]

    #######################
    # Mouse move handling #
    #######################

    
    def check_cursor(self,event):
        """
        Changes cursor according to its position.
        """
        assert self.canvas
        for idx, rec in enumerate(self.plotSolver.GetBarDataAsList()):
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
