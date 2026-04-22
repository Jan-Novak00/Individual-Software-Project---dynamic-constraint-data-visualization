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
    def write(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver, file: str):
        with open(file,"w") as output:
            candles = solver.GetCandleData()
            for candle in candles:
                output.write(f"{candle.name},{candle.openingCorner.Y/plotMetadata.heightScaleFactor + plotMetadata.xAxisValue},{candle.closingCorner.Y/plotMetadata.heightScaleFactor + plotMetadata.xAxisValue},{candle.wickBottom.Y/plotMetadata.heightScaleFactor + plotMetadata.xAxisValue},{candle.wickTop.Y/plotMetadata.heightScaleFactor + plotMetadata.xAxisValue}")
                output.write("\n")

class BarChartDataWriter(DataWriter):
    def write(self, plotMetadata: BarChartMetadata, solver: BarChartSolver, file: str):
        with open(file,"w") as output:
            groups = solver.GetRectangleData()
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
    def write(self, plotMetadata: HistogramMetadata, solver: BarChartSolver, file: str):
        with open(file,"w") as output:
            rectangles = solver.GetRectangleDataAsList()
            for rec in rectangles:
                height = rec.GetHeight()
                value = height/plotMetadata.heightScaleFactor
                output.write(f"{rec.leftBottom.secondaryName},{rec.rightTop.secondaryName},{value}\n")

class LineChartDataWriter(DataWriter):
    def write(self, plotMetadata: LineChartMetadata, solver: LineChartSolver, file: str):
        with open(file,"w") as output:
            lines = solver.GetLineData()
            origin = solver.GetOrigin()
            points = [line.leftEnd for line in lines] + [lines[-1].rightEnd]
            for i,point in enumerate(points):
                value = point.Y - origin.Y
                label = point.name
                trueValue = value/plotMetadata.heightScaleFactor + plotMetadata.xAxisValue
                output.write(label)
                output.write(",")
                output.write(str(trueValue))
                output.write("\n")
