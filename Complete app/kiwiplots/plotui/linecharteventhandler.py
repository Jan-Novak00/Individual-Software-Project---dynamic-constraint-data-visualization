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

class LineChartEventHandler(EventHandler):
    def __init__(self, plotMetadata: LineChartMetadata, solver: LineChartSolver):
        super().__init__(plotMetadata)
        self.plotSolver: LineChartSolver = solver
        self.canvasHeight : int = None # pyright: ignore[reportAttributeAccessIssue]

    def inicializeDataView(self, textWindow: tk.Text) -> None:
        self.dataViewer = LineChartDataViewer(textWindow)
    
    def inicializeCanvas(self, canvas: tk.Canvas, width: int, height: int) -> None:
        self.canvas = canvas
        self.canvasHeight = height
        self.drawer = LineChartCanvasDrawer(canvas, width, height)
    
    def inicializeRightClickMenu(self, menu: tk.Menu) -> None:
        #ToDo
        return