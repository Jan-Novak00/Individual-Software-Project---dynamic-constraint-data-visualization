from .uicore import UICore
from .plotmetadata import *
from kiwiplots.solvers import *
from .eventhandlers import EventHandler
from .candlesticeventhandler import CandlesticEventHandler
from .picturedrawers import *
from .datawriters import *
from numpy import abs

INITIAL_WIDTH : int   = 10
INITIAL_SPACING : int = 10
INITIAL_ORIGIN_X : int = 50
INITIAL_ORIGIN_Y : int = 30

class UIFactory:

    @staticmethod
    def createCandlesticChart(title: str, 
                              xAxisLabel : str, 
                              yAxisLabel : str,
                              xAxisValue : float, 
                              initialOpening : list[float], 
                              initialClosing : list[float], 
                              initialMinimum : list[float], 
                              initialMaximum : list[float], 
                              names : list[str],
                              plotWidth: int,
                              plotHeight: int
                              )->UICore:
        """
        Creates a complete candlestick chart UI component with all necessary metadata, solvers, and handlers.
        
        Args:
            title (str): The title of the candlestick chart
            xAxisLabel (str): Label for the x-axis
            yAxisLabel (str): Label for the y-axis
            xAxisValue (float): The value where the x-axis is positioned
            initialOpening (list[float]): List of opening prices for each candlestick
            initialClosing (list[float]): List of closing prices for each candlestick
            initialMinimum (list[float]): List of minimum prices for each candlestick
            initialMaximum (list[float]): List of maximum prices for each candlestick
            names (list[str]): Names/labels for each candlestick
            plotWidth (int): Width of the plot area in pixels
            plotHeight (int): Height of the plot area in pixels
            
        Returns:
            UICore: A fully configured UICore instance containing metadata, solver, event handler,
                    picture drawer, and data writer for the candlestick chart
        """
        metadata : CandlesticPlotMetadata = UIFactory._createCandlesticChartMetadata(xAxisLabel,yAxisLabel, xAxisValue, initialOpening,initialClosing,initialMinimum,initialMaximum,plotHeight)
        solver : CandlestickChartSolver = UIFactory._createCandlesticChartSolver(metadata,initialOpening,initialClosing,initialMinimum,initialMaximum,names,title)
        eventHandler : EventHandler = CandlesticEventHandler(metadata, solver)
        pictureDrawer : PictureDrawer = CandlesticPictureDrawer()
        dataWriter : DataWriter = CandlesticDataWriter()
        return UICore(metadata,solver,eventHandler,pictureDrawer,dataWriter,plotWidth,plotHeight)


    @staticmethod
    def _createCandlesticChartMetadata(xAxisLabel: str, 
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
        scaleFactor : float = 1
        allValues = abs(initialClosing) + abs(initialOpening) + abs(initialMinimum) + abs(initialMaximum)
        maxValue = max(allValues,default=1)
        if not (plotHeight*0.3 <= maxValue <= plotHeight*0.7):
            scaleFactor = plotHeight*0.8/maxValue

        return CandlesticPlotMetadata(scaleFactor,xAxisValue,xAxisLabel,yAxisLabel)
    
    @staticmethod
    def _createCandlesticChartSolver(metadata : CandlesticPlotMetadata,
                                     initialOpening : list[float], 
                                     initialClosing : list[float], 
                                     initialMinimum : list[float], 
                                     initialMaximum : list[float],
                                     names : list[str],
                                     title : str
                                     )-> CandlestickChartSolver:
        """
        Creates a solver for the candlestick chart with rescaled data.
        
        This method takes the raw price data and rescales it according to the scale factor
        from the metadata, positioning it relative to the x-axis value. It creates a
        CandlestickChartSolver initialized with the rescaled values and chart configuration.
        
        Args:
            metadata (CandlesticPlotMetadata): Chart metadata including scale factor and axis information
            initialOpening (list[float]): List of opening prices to be rescaled
            initialClosing (list[float]): List of closing prices to be rescaled
            initialMinimum (list[float]): List of minimum prices to be rescaled
            initialMaximum (list[float]): List of maximum prices to be rescaled
            names (list[str]): Names/labels for each candlestick
            title (str): The title of the chart
            
        Returns:
            CandlestickChartSolver: A solver instance with rescaled data and configured parameters
                                    (width, spacing, origin coordinates)
        """
        
        def rescaleList(inputList : list[float], scaleFactor : float, scaledXAxisValue: float) -> list[int]:
            return [int(value*scaleFactor-scaledXAxisValue) for value in inputList]
        
        rescaledXAxisValue : float = metadata.xAxisValue*metadata.scaleFactor

        return CandlestickChartSolver(INITIAL_WIDTH,
                                      rescaleList(initialOpening, metadata.scaleFactor,rescaledXAxisValue),
                                      rescaleList(initialClosing, metadata.scaleFactor,rescaledXAxisValue),
                                      rescaleList(initialMinimum, metadata.scaleFactor,rescaledXAxisValue),
                                      rescaleList(initialMaximum, metadata.scaleFactor,rescaledXAxisValue),
                                      INITIAL_SPACING,
                                      names,
                                      title,
                                      INITIAL_ORIGIN_X,
                                      INITIAL_ORIGIN_Y)

    