from abc import ABC
from .plotmetadata import *
from kiwiplots.solvers import *


class DataWriter(ABC):
    """
    Abstract class for exporting plot data to file formats.
    """

    def write(self, plotMetada : PlotMetadata, solver: ChartSolver, file: str):
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
    """
    Data writer for candlestick charts.
    
    Exports candlestick data to CSV format.
    """
    def write(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver, file: str):
        """Exports candlestick data to a CSV file.

        Args:
            plotMetadata (CandlesticPlotMetadata): Metadata containing scale factor and axis values.
            solver (CandlestickChartSolver): Solver containing candle data.
            file (str): Path to the output CSV file.
        """
        with open(file,"w") as output:
            candles = solver.GetCandleData()
            for candle in candles:
                output.write(f"{candle.name},{candle.openingCorner.Y/plotMetadata.heightScaleFactor + plotMetadata.xAxisValue},{candle.closingCorner.Y/plotMetadata.heightScaleFactor + plotMetadata.xAxisValue},{candle.wickBottom.Y/plotMetadata.heightScaleFactor + plotMetadata.xAxisValue},{candle.wickTop.Y/plotMetadata.heightScaleFactor + plotMetadata.xAxisValue}")
                output.write("\n")

class BarChartDataWriter(DataWriter):
    """
    Data writer for bar charts.
    
    Exports bar chart data to CSV format.
    """
    def write(self, plotMetadata: BarChartMetadata, solver: BarChartSolver, file: str):
        """Exports bar chart data to a CSV file.

        Args:
            plotMetadata (BarChartMetadata): Metadata containing scale factor and axis values.
            solver (BarChartSolver): Solver containing bar data.
            file (str): Path to the output CSV file.
        """
        with open(file,"w") as output:
            groups = solver.GetBarData()
            for group in groups: # pyright: ignore[reportOptionalIterable]
                for i in range(len(group)):
                    rec = group[i]
                    if i != 0:
                        output.write(",")
                    height = rec.GetHeight()
                    value = height/plotMetadata.heightScaleFactor
                    output.write(f"{rec.name},{value}")
                output.write("\n")

class HistogramDataWriter(DataWriter):
    """
    Data writer for histograms.
    
    Exports histogram bucket data to CSV format.
    """
    def write(self, plotMetadata: HistogramMetadata, solver: HistogramSolver, file: str):
        """Exports histogram bucket data to a CSV file.

        Args:
            plotMetadata (HistogramMetadata): Metadata containing scale factor and axis values.
            solver (HistogramSolver): Solver containing bucket data.
            file (str): Path to the output CSV file.
        """
        with open(file,"w") as output:
            rectangles = solver.GetBucketData()
            for rec in rectangles:
                height = rec.GetHeight()
                value = height/plotMetadata.heightScaleFactor
                output.write(f"{rec.interval[0]},{rec.interval[1]},{value}\n")

class LineChartDataWriter(DataWriter):
    """
    Data writer for line charts.
    
    Exports line chart data to CSV format.
    """
    def write(self, plotMetadata: LineChartMetadata, solver: LineChartSolver, file: str):
        """Exports line chart data to a CSV file.

        Args:
            plotMetadata (LineChartMetadata): Metadata containing scale factor and axis values.
            solver (LineChartSolver): Solver containing line data.
            file (str): Path to the output CSV file.
        """
        with open(file,"w") as output:
            lines = solver.GetLineData()
            origin = solver.GetOrigin()
            points = solver.GetPoints()
            for i,point in enumerate(points):
                value = point.Y - origin.Y
                label = point.name
                trueValue = value/plotMetadata.heightScaleFactor + plotMetadata.xAxisValue
                output.write(label)
                output.write(",")
                output.write(str(trueValue))
                output.write("\n")
