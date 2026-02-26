from abc import ABC

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
    def __init__(self, title: str, heightScaleFactor: float, xAxisValue: float, xAxisLabel : str, yAxisLabel : str):
        super().__init__(title, heightScaleFactor, xAxisValue, xAxisLabel, yAxisLabel)