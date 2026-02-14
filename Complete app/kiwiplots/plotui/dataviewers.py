from abc import ABC
import tkinter as tk
from .plotmetadata import *
from kiwiplots.solvers import *

class DataViewer(ABC):
    """

    Abstract class. Contains logic for showing current data values represented by a graph.

    """
    def __init__(self, textWindow : tk.Text):
        """
        Initializes the DataViewer with a text window for displaying data.
        
        Args:
            textWindow: A tkinter Text widget where data will be displayed.
        """
        self.dataWindow : tk.Text = textWindow

    def write(self, plotMetadata: PlotMetadata, solver: ChartSolver, changedIndex: int, changedStatus: str = "")->None: # type: ignore
        """
        Displays plot data in the text window.
        
        This method should update the text window with current data values from the solver,
        and highlight the data element that is currently being edited.
        
        Args:
            plotMetadata: Metadata about the plot including scale factor and axis values.
            solver: The solver containing the plot data to be displayed.
            changedIndex: Index of the data element currently being modified. -1 or None if none are being modified.
            changedStatus: Name of the value being changed (e.g., 'opening', 'closing', 'maximum', 'minimum').
        """
        raise NotImplementedError("Method DataViewr.write must be declared in subclass")


class CandlesticDataViewer(DataViewer):
    def __init__(self, textWindow: tk.Text):
        super().__init__(textWindow)

    def write(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver, changedIndex: int, changedStatus: str = ""):
        """
        Displays all data for the user and highlights which data is being edited
        """
        xAxisValue = plotMetadata.xAxisValue
        scaleFactor = plotMetadata.scaleFactor
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        valueEdited = changedStatus in ["opening", "closing", "maximum", "minimum"]
        candles = solver.GetCandleData()

        for i in range(len(candles)-1, -1, -1):
            candle = candles[i]
            openingValue = candle.openingCorner.Y/scaleFactor + xAxisValue
            closingValue = candle.closingCorner.Y/scaleFactor + xAxisValue
            maximumValue = candle.wickTop.Y/scaleFactor + xAxisValue
            minimumValue = candle.wickBottom.Y/scaleFactor + xAxisValue
            
            string = f"{candle.name}:\n\topening = {openingValue:.4f},\n\tclosing = {closingValue:.4f},\n\tmin = {minimumValue:.4f},\n\tmax = {maximumValue:.4f}\n\n"
            if valueEdited and i == changedIndex:
                self.dataWindow.insert("1.0",f"{string}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"{string}\n")
        self.dataWindow.config(state="disabled")