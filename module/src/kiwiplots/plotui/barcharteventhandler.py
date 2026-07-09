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
from kiwiplots.utils import inheritdocstring

class BarChartEventHandler(RectangleEventHandler):
    """Event handler for bar chart user interactions.
    
    Manages mouse events and context menus for bar chart manipulation including adding/removing
    bars and groups, changing properties, and interactive resizing of rectangles.
    
    Attributes:
        plotSolver (BarChartSolver): The solver containing bar chart data.
        plotMetadata (BarChartMetadata): Metadata about the bar chart including scale factors.
    """
    
    ###################
    # Inicialization #
    ###################

    def __init__(self, plotMetadata: BarChartMetadata, solver: BarChartSolver) -> None:
        """Initializes the BarChartEventHandler with plot metadata and solver.

        Args:
            plotMetadata (BarChartMetadata): Metadata about the bar chart including scale factor and axis values.
            solver (BarChartSolver): Solver containing bar chart data.
        """
        super().__init__(plotMetadata, solver)
        self.plotSolver : BarChartSolver = solver
        self.plotMetadata : BarChartMetadata = plotMetadata

    @inheritdocstring(RectangleEventHandler.initializeDataView)
    def initializeDataView(self, textWindow: tk.Text) -> None:
        """Initializes the data viewer for bar chart display.
        
        Creates a BarChartDataViewer to display bar values in the text window.
        """
        self.dataViewer = BarChartDataViewer(textWindow)
    
    @inheritdocstring(RectangleEventHandler.initializeCanvas)
    def initializeCanvas(self, canvas: tk.Canvas, width: int, height: int) -> None:
        """Initializes the canvas drawer for bar chart visualization.
        
        Creates a BarChartCanvasDrawer for rendering bars on the canvas.
        """
        self.canvas = canvas
        self.canvasHeight = height
        self.drawer = BarChartCanvasDrawer(canvas,width,height)
    
    @inheritdocstring(RectangleEventHandler.initializeRightClickMenu)
    def initializeRightClickMenu(self, menu: tk.Menu) -> None:
        """Initializes the right-click context menu for bar operations.
        
        Adds commands to change color, change name, and add rectangles to selected bars.
        """
        self.elementMenu = menu
        self.elementMenu.add_command(label="Change color", command=self._changeColor)
        self.elementMenu.add_command(label="Change name", command=self._changeName)
        self.elementMenu.add_command(label="Add rectangle to group", command=self._addRectangle)
    
    @inheritdocstring(RectangleEventHandler.initializeDefaultRightClickMenu)
    def initializeDefaultRightClickMenu(self, menu: tk.Menu) -> None:
        """Initializes the default right-click context menu for empty canvas area.
        
        Adds commands to add new bar groups to the chart.
        """
        EventHandler.initializeDefaultRightClickMenu(self,menu)
        assert self.defaultMenu
        self.defaultMenu.add_command(label="Add rectangle group", command=self._addGroup)
    
    def _addGroup(self):
        """Prompts user to add a new rectangle group to the bar chart.
        
        Opens a dialog for entering the group's first rectangle name and initial value.
        Updates the chart visualization and translation table after adding the group.
        """
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
        """Prompts user to add a new rectangle to the selected bar group.
        
        Opens a dialog for entering the rectangle's name and value.
        Updates the chart visualization and translation table after adding the rectangle.
        """
        groupIndex, _ = self._indexToGroupIndex(self.eventRegistersRight.indexToChange)
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
    

    #######################
    # Mouse move handling #
    #######################

    
    @inheritdocstring(RectangleEventHandler.check_cursor)
    def check_cursor(self, event):
        """Updates cursor appearance based on mouse position over bar chart elements.
        
        Changes the cursor to indicate what action is possible at the current location:
        - hand2: Near a left edge (spacing adjustment)
        - sb_h_double_arrow: Near a right edge (width adjustment)
        - sb_v_double_arrow: Near a top edge (height adjustment) or Y-axis top
        - fleur: Near the chart origin (pan operation)
        - arrow: Default cursor for empty areas
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
