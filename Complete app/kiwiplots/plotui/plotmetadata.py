from abc import ABC

class PlotMetadata(ABC):
    """
    Abstract class that carries shared metadata about plot data.
    
    Contains information such as scale factor and axis values used to convert
    pixel dimensions into data dimensions.
    """
    def __init__(self, title: str, heightScaleFactor: float, xAxisValue: float):
        """
        Initializes PlotMetadata with scale and axis information.
        
        Args:
            scaleFactor: The scaling factor for converting pixel coordinates to data values.
            xAxisValue: The data value corresponding to the x-axis origin.
        """
        self.heightScaleFactor : float = heightScaleFactor
        self.xAxisValue : float = xAxisValue
        self.title = title



class CandlesticPlotMetadata(PlotMetadata):
    def __init__(self, title: str, heightScaleFactor: float, xAxisValue: float, xAxisLabel : str, yAxisLabel : str):
        self.heightScaleFactor : float = heightScaleFactor
        self.xAxisValue : float = xAxisValue
        self.xAxisLabel : str = xAxisLabel
        self.yAxisLabel : str = yAxisLabel
        self.title: str = title

class BarChartMetadata(PlotMetadata):
    def __init__(self, title: str, heightScaleFactor: float, xAxisLabel : str, yAxisLabel : str):
        super().__init__(title, heightScaleFactor, 0)
        self.xAxisLabel : str = xAxisLabel
        self.yAxisLabel : str = yAxisLabel

class HistogramMetadata(BarChartMetadata):
    def __init__(self, title: str, heightScaleFactor: float, intervalGropsScaleFactors: list[list[float]], xAxisLabel : str, yAxisLabel : str):
        super().__init__(title,heightScaleFactor,xAxisLabel,yAxisLabel)
        self.widthScaleFactor: list[list[float]] = intervalGropsScaleFactors