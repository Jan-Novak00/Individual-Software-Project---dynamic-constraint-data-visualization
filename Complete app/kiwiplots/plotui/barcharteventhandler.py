import tkinter as tk
from .canvasdrawers import CandlesticCanvasDrawer
from .eventhandlers import EventHandler
from kiwiplots.solvers import BarChartSolver
from .plotmetadata import BarPlotMetadata
from .plotmath import isNear
from .dataviewers import CandlesticDataViewer
from kiwiplots.plotelement import ValueCandle, ValuePoint2D
from tkinter import simpledialog
from tkinter import colorchooser

class BarChartEventHandler(EventHandler):
    def __init__(self, plotMetadata: BarPlotMetadata, solver: BarChartSolver) -> None:
        super().__init__(plotMetadata)
        self.plotSolver : BarChartSolver = solver  # type: ignore
        self.canvasHeight : int = None # type: ignore