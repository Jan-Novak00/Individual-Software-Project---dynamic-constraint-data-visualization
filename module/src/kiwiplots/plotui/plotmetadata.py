from abc import ABC
from typing import Union

class PlotMetadata(ABC):
    """
    Abstract class that carries shared metadata about plot data.
    
    Contains information such as scale factor and axis values used to convert
    pixel dimensions into data dimensions.
    """
    def __init__(self, title: str, heightScaleFactor: float, xAxisValue: float, xAxisLabel : str, yAxisLabel : str):
        """
        Initializes PlotMetadata with scale and axis information.
        
        Args:
            scaleFactor: The scaling factor for converting pixel coordinates to data values.
            xAxisValue: The data value corresponding to the x-axis origin.
        """
        self.heightScaleFactor : float = heightScaleFactor
        self.xAxisValue : float = xAxisValue
        self.title = title
        self.xAxisLabel : str = xAxisLabel
        self.yAxisLabel : str = yAxisLabel



class CandlesticPlotMetadata(PlotMetadata):
    """
    Metadata for candlestick plots.

    Inherits common scale and axis information from `PlotMetadata` and is
    intended for use with candlestick renderers that require title,
    height scaling and axis labels. No additional attributes are added by
    this subclass — it exists for semantic clarity and potential future extension.
    """
    def __init__(self, title: str, heightScaleFactor: float, xAxisValue: float, xAxisLabel : str, yAxisLabel : str):
        super().__init__(title, heightScaleFactor, xAxisValue, xAxisLabel, yAxisLabel)

class BarChartMetadata(PlotMetadata):
    """
    Metadata for bar chart plots.

    Provides the shared `PlotMetadata` fields but defaults the
    `xAxisValue` to 0 since bar charts commonly align bars to integer
    bucket indices rather than a continuous x-origin value.
    """
    def __init__(self, title: str, heightScaleFactor: float, xAxisLabel : str, yAxisLabel : str):
        super().__init__(title, heightScaleFactor, 0, xAxisLabel, yAxisLabel)

class HistogramMetadata(BarChartMetadata):
    """
    Metadata for histogram plots.

    Extends `BarChartMetadata` with an additional `widthScaleFactor` field
    that stores scaling information for interval groups (bins). The
    `intervalGropsScaleFactors` parameter is expected to be a nested list
    of floats describing widths or scaling per interval group (histograms ALWAYS have just one interval group - multiple groups are supported only for interoperability with bar chart infrastructure).
    """
    def __init__(self, title: str, heightScaleFactor: float, intervalGropsScaleFactors: list[list[float]], xAxisLabel : str, yAxisLabel : str):
        super().__init__(title,heightScaleFactor,xAxisLabel,yAxisLabel)
        self.widthScaleFactor: list[list[float]] = intervalGropsScaleFactors

class LineChartMetadata(PlotMetadata):
    """
    Metadata for line chart plots.

    Carries scale and axis labels for continuous line plots where the
    `xAxisValue` may represent the data value at the x-origin. Use this
    class with renderers that draw lines connecting data points.
    """
    def __init__(self, title: str, color: Union[str,int], heightScaleFactor: float, xAxisValue: float, xAxisLabel : str, yAxisLabel : str):
        super().__init__(title, heightScaleFactor, xAxisValue, xAxisLabel, yAxisLabel)
        self.color : Union[str,int] = color

from numpy import abs
from .datautils import *
from .uiconstants import *

def CreateCandlesticChartMetadata(title: str,
                            xAxisLabel: str, 
                            yAxisLabel: str, 
                            xAxisValue : float,
                            initialOpening : list[float], 
                            initialClosing : list[float], 
                            initialMinimum : list[float], 
                            initialMaximum : list[float],
                            plotHeight : int
                            )-> CandlesticPlotMetadata:
    """
    Creates metadata for a candlestick chart, including calculated scale factor.
    
    This method determines the appropriate scale factor to fit the data values within
    the plot height (between 30% and 70% of available height). If values fall outside
    this range, it calculates a scale factor to fit them optimally.
    
    Args:
        title (str): Title of the plot
        xAxisLabel (str): Label for the x-axis
        yAxisLabel (str): Label for the y-axis
        xAxisValue (float): The value where the x-axis is positioned
        initialOpening (list[float]): List of opening prices
        initialClosing (list[float]): List of closing prices
        initialMinimum (list[float]): List of minimum prices
        initialMaximum (list[float]): List of maximum prices
        plotHeight (int): Height of the plot area in pixels
        
    Returns:
        CandlesticPlotMetadata: Metadata object containing scale factor and axis information
    """
    allValues : list[float] = abs(initialClosing) + abs(initialOpening) + abs(initialMinimum) + abs(initialMaximum) # pyright: ignore[reportAssignmentType]

    return CandlesticPlotMetadata(title,CalculateScaleFactor(allValues,plotHeight),xAxisValue,xAxisLabel,yAxisLabel)

def CreateBarChartMetadata(title: str, xAxisLabel: str, yAxisLabel: str, initialValues: list[list[float]], plotHeight: int):
    """
    Produce `BarChartMetadata` with a scale factor computed from all rectangle groups.

    Args:
        title (str): Chart title.
        xAxisLabel (str): Label for the x-axis.
        yAxisLabel (str): Label for the y-axis.
        initialValues (list[list[float]]): Grouped bar values.
        plotHeight (int): Pixel height of the plotting area.

    Returns:
        BarChartMetadata: Metadata instance with computed height scale.
    """
    allValues : list[float] = []
    for group in initialValues:
        for value in group:
            allValues.append(value)
    return BarChartMetadata(title,CalculateScaleFactor(allValues,plotHeight),xAxisLabel,yAxisLabel)


def CreateHistogramMetadata(title: str, xAxisLabel: str, yAxisLabel: str, initialValues : list[float], intervals: list[tuple[float,float]], plotHeight: int)-> HistogramMetadata:
    """
    Build `HistogramMetadata` including height and per-interval width scales.

    Computes the height scale using the provided values and constructs a
    nested list of width scale factors for the provided `intervals`.

    Args:
        title (str): Histogram title.
        xAxisLabel (str): X-axis label.
        yAxisLabel (str): Y-axis label.
        initialValues (list[float]): Values to use when computing height scale.
        intervals (list[tuple[float,float]]): Bins defined by (start, end) tuples.
        plotHeight (int): Pixel height of the plotting area.

    Returns:
        HistogramMetadata: Metadata with height and width scale information.
    """
    heightScaleFactor : float = CalculateScaleFactor(initialValues,plotHeight)
    widthScales = [CreateScalesForIntervalGroup(intervals)]
    return HistogramMetadata(title, heightScaleFactor, widthScales, xAxisLabel, yAxisLabel)


def CreateLineChartMetadata(title: str, xAxisValue : float, values : list[float], xAxisLabel : str, yAxisLabel : str, height : int, color: str|int = DEFAULT_COLOR)->LineChartMetadata:
    heightScaleFactor : float = CalculateScaleFactor(values,height)
    return LineChartMetadata(title,color,heightScaleFactor,xAxisValue,xAxisLabel,yAxisLabel)