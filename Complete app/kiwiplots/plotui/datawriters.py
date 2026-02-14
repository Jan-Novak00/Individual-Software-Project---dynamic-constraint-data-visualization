from abc import ABC
from .plotmetadata import *
from kiwiplots.solvers import *

class DataWriter(ABC):
    """
    Abstract class for exporting plot data to file formats.
    """

    def write(self, plotMetada : PlotMetadata, solver: ChartSolver):
        """
        Exports plot data to a file.
        
        This method should retrieve all plot data from the solver and write it to
        a file in a structured format (CSV).
        
        Args:
            plotMetada: Metadata about the plot including scale factor and axis values.
            solver: The solver containing the plot data to be exported.
        """
        raise NotImplementedError("Method DataWriter.write must be declared in subclass")

class CandlesticDataWriter(DataWriter):
    def write(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver, file: str):
        with open(file,"w") as output:
            candles = solver.GetCandleData()
            for candle in candles:
                output.write(f"{candle.name},{candle.openingCorner.Y/plotMetadata.scaleFactor + plotMetadata.xAxisValue},{candle.closingCorner.Y/plotMetadata.scaleFactor + plotMetadata.xAxisValue},{candle.wickBottom.Y/plotMetadata.scaleFactor + plotMetadata.xAxisValue},{candle.wickTop.Y/plotMetadata.scaleFactor + plotMetadata.xAxisValue}")
                output.write("\n")