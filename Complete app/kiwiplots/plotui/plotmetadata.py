from abc import ABC

class PlotMetadata(ABC):
    """
    Abstract class that carries shared metadata about plot data.
    
    Contains information such as scale factor and axis values used to convert
    pixel dimensions into data dimensions.
    """
    def __init__(self, scaleFactor: float, xAxisValue: float):
        """
        Initializes PlotMetadata with scale and axis information.
        
        Args:
            scaleFactor: The scaling factor for converting pixel coordinates to data values.
            xAxisValue: The data value corresponding to the x-axis origin.
        """
        self.scaleFactor : float = scaleFactor
        self.xAxisValue : float = xAxisValue


class CandlesticPlotMetadata(PlotMetadata):
    def __init__(self, scaleFactor: float, xAxisValue: float, xAxisLabel : str, yAxisLabel : str):
        self.scaleFactor : float = scaleFactor
        self.xAxisValue : float = xAxisValue
        self.xAxisLabel : str = xAxisLabel
        self.yAxisLabel : str = yAxisLabel
