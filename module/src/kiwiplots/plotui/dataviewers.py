from abc import ABC
import tkinter as tk
from kiwiplots.plotui.plotmetadata import PlotMetadata
from kiwiplots.solvers import ChartSolver
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

    def Write(self, plotMetadata: PlotMetadata, solver: ChartSolver, changedIndex: int, changedStatus: str)->None: # type: ignore
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

    def Write(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver, changedIndex: int, changedStatus: str): # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Displays all data for the user and highlights which data is being edited
        """
        xAxisValue = plotMetadata.xAxisValue
        scaleFactor = plotMetadata.heightScaleFactor
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
            minimumValue = candle.wickBottom.Y/scaleFactor + xAxisValue/scaleFactor
            
            string = f"{candle.name}:\n\topening = {openingValue:.4f},\n\tclosing = {closingValue:.4f},\n\tmin = {minimumValue:.4f},\n\tmax = {maximumValue:.4f}\n\n"
            if valueEdited and i == changedIndex:
                self.dataWindow.insert("1.0",f"{string}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"{string}\n")
        self.dataWindow.config(state="disabled")

class BarChartDataViewer(DataViewer):
    def Write(self, plotMetadata: BarChartMetadata, solver: BarChartSolver, changedIndex: int, changedStatus: str) -> None: # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Displays all data for the user and highlights which data is being edited
        """
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        valueEdited = changedStatus == "top"
        rectangles = solver.GetBarDataAsList()

        for i in range(len(rectangles)-1, -1, -1):
            rec = rectangles[i]
            trueValue = rec.GetHeight()/plotMetadata.heightScaleFactor
            valueString = ""
            if ((trueValue >= 1e+06) or (trueValue <= 1e-04)):
                valueString = f"{trueValue:.4g}"
            else:
                valueString = str(trueValue)

            if valueEdited and i == changedIndex:
                self.dataWindow.insert("1.0",f"{rec.name} = {valueString}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"{rec.name} = {valueString}\n")
        self.dataWindow.config(state="disabled")

class HistogramDataViewer(DataViewer):
    def Write(self, plotMetadata: HistogramMetadata, solver: BarChartSolver, changedIndex: int, changedStatus: str) -> None: # pyright: ignore[reportIncompatibleMethodOverride]
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        valueEdited = changedStatus == "top"
        rectangles = solver.GetBarDataAsList()

        for i in range(len(rectangles)-1, -1, -1):
            rec = rectangles[i]
            trueValue = rec.GetHeight()/plotMetadata.heightScaleFactor
            valueString = ""
            if ((trueValue >= 1e+06) or (trueValue <= 1e-04)):
                valueString = f"{trueValue:.4g}"
            else:
                valueString = str(trueValue)


            if valueEdited and i == changedIndex:
                self.dataWindow.insert("1.0",f"({rec.leftBottom.secondaryName}, {rec.rightTop.secondaryName}) = {valueString}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"({rec.leftBottom.secondaryName}, {rec.rightTop.secondaryName}) = {valueString}\n")
        self.dataWindow.config(state="disabled")

class LineChartDataViewer(DataViewer):
    def Write(self, plotMetadata: LineChartMetadata, solver: LineChartSolver, changedIndex: int, changedStatus: str)->None:
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")
        self.dataWindow.tag_configure("changing_Value", foreground="red")
        valueEdited = False #
        lines = solver.GetLineData()
        origin = solver.GetOrigin()
        points = [line.leftEnd for line in lines] + [lines[-1].rightEnd]
        points.reverse()

        for i,point in enumerate(points):
            value = point.Y - origin.Y
            label = point.name
            trueValue = value/plotMetadata.heightScaleFactor + plotMetadata.xAxisValue
            valueString = ""
            if ((trueValue >= 1e+06) or (trueValue <= 1e-04)):
                valueString = f"{trueValue:.4g}"
            else:
                valueString = str(trueValue)
            if valueEdited and i == changedIndex:
                self.dataWindow.insert("1.0",f"{label} = {valueString}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"{label} = {valueString}\n")
        self.dataWindow.config(state="disabled")
