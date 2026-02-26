from .uicore import UICore
from .plotmetadata import *
from kiwiplots.solvers import *
from .eventhandlers import EventHandler
from .candlesticeventhandler import CandlesticEventHandler
from .barcharteventhandler import BarChartEventHandler
from .histogrameventhandler import HistogramEventHandler
from .picturedrawers import *
from .datawriters import *
from numpy import abs

INITIAL_WIDTH : int   = 10
INITIAL_SPACING : int = 15
INITIAL_INNER_SPACING = 10
INITIAL_ORIGIN_X : int = 50
INITIAL_ORIGIN_Y : int = 30
INITIAL_PADDING : int = 10

class UIFactory:

    @staticmethod
    def _calculateScaleFactor(values: list[float],height: int)->float:
        scaleFactor : float = 1
        maxValue = max(values,default=1)
        if not (height*0.3 <= maxValue <= height*0.7):
            scaleFactor = height*0.8/maxValue
        return scaleFactor

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
        metadata : CandlesticPlotMetadata = UIFactory._createCandlesticChartMetadata(title,xAxisLabel,yAxisLabel, xAxisValue, initialOpening,initialClosing,initialMinimum,initialMaximum,plotHeight)
        solver : ChartSolver = UIFactory._createCandlesticChartSolver(metadata,initialOpening,initialClosing,initialMinimum,initialMaximum,names)
        eventHandler : EventHandler = CandlesticEventHandler(metadata, solver)
        pictureDrawer : PictureDrawer = CandlesticPictureDrawer()
        dataWriter : DataWriter = CandlesticDataWriter()
        return UICore(metadata,solver,eventHandler,pictureDrawer,dataWriter,plotWidth,plotHeight)


    @staticmethod
    def _createCandlesticChartMetadata(title: str,
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
    
        return CandlesticPlotMetadata(title,UIFactory._calculateScaleFactor(allValues,plotHeight),xAxisValue,xAxisLabel,yAxisLabel)
    
    @staticmethod
    def _createCandlesticChartSolver(metadata : CandlesticPlotMetadata,
                                     initialOpening : list[float], 
                                     initialClosing : list[float], 
                                     initialMinimum : list[float], 
                                     initialMaximum : list[float],
                                     names : list[str]
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
        
        rescaledXAxisValue : float = metadata.xAxisValue*metadata.heightScaleFactor

        return CandlestickChartSolver(INITIAL_WIDTH,
                                      rescaleList(initialOpening, metadata.heightScaleFactor,rescaledXAxisValue),
                                      rescaleList(initialClosing, metadata.heightScaleFactor,rescaledXAxisValue),
                                      rescaleList(initialMinimum, metadata.heightScaleFactor,rescaledXAxisValue),
                                      rescaleList(initialMaximum, metadata.heightScaleFactor,rescaledXAxisValue),
                                      INITIAL_SPACING,
                                      names,
                                      INITIAL_ORIGIN_X,
                                      INITIAL_ORIGIN_Y)

    @staticmethod
    def createBarChart( title: str, 
                        xAxisLabel : str, 
                        yAxisLabel : str, 
                        initialValues : list[list[float]],
                        rectangleNames : list[list[str]],
                        plotWidth: int,
                        plotHeight: int
                        )->UICore:
        metadata : BarChartMetadata = UIFactory._createBarChartMetadata(title, xAxisLabel, yAxisLabel, initialValues, plotHeight)
        solver : ChartSolver = UIFactory._createBarChartSolver(metadata,initialValues,rectangleNames)
        pictureDrawer : PictureDrawer = BarChartPictureDrawer()
        dataWriter : DataWriter = BarChartDataWriter()
        eventHandler : EventHandler = BarChartEventHandler(metadata,solver)
        return UICore(metadata,solver,eventHandler,pictureDrawer,dataWriter,plotWidth,plotHeight)
    
    @staticmethod
    def _createBarChartMetadata(title: str, xAxisLabel: str, yAxisLabel: str, initialValues: list[list[float]], plotHeight: int):
        allValues : list[float] = []
        for group in initialValues:
            for value in group:
                allValues.append(value)
        return BarChartMetadata(title,UIFactory._calculateScaleFactor(allValues,plotHeight),xAxisLabel,yAxisLabel)
    
    @staticmethod
    def _createBarChartSolver(metadata: BarChartMetadata, initialValues: list[list[float]], rectangleNames : list[list[str]], initialSpacing : int = INITIAL_SPACING, initialInnerSpacing : int = INITIAL_INNER_SPACING)->BarChartSolver:
        rescaledGroupValues : list[list[int]] = []
        for group in initialValues:
            rescaledGroupValues.append([int(metadata.heightScaleFactor*value) for value in group])
        
        return BarChartSolver(INITIAL_WIDTH,rescaledGroupValues,initialSpacing,initialInnerSpacing,rectangleNames,INITIAL_ORIGIN_X,INITIAL_ORIGIN_Y)
        

    @staticmethod
    def createHistogram(title: str,
                        xAxisLabel: str,
                        yAxisLabel: str,
                        initialValues: list[float], 
                        intervals: list[tuple[float,float]],
                        plotWidth: int,
                        plotHeight: int):
        metadata : HistogramMetadata = UIFactory._createHistogramMetadata(title,xAxisLabel,yAxisLabel,initialValues,intervals,plotHeight)
        solver : ChartSolver = UIFactory._createHistogramSolver(metadata, initialValues, intervals)
        pictureDrawer : PictureDrawer = HistorgramPictureDrawer()
        dataWriter : DataWriter = HistogramDataWriter()
        eventHandler : EventHandler = HistogramEventHandler(metadata,solver)
        return UICore(metadata,solver,eventHandler,pictureDrawer,dataWriter,plotWidth,plotHeight)


    @staticmethod
    def _createHistogramMetadata(title: str, xAxisLabel: str, yAxisLabel: str, initialValues : list[float], intervals: list[tuple[float,float]], plotHeight: int)-> HistogramMetadata:
        heightScaleFactor : float = UIFactory._calculateScaleFactor(initialValues,plotHeight)
        widthScales = [UIFactory._createScalesForIntervalGroup(intervals)]
        return HistogramMetadata(title, heightScaleFactor, widthScales, xAxisLabel, yAxisLabel)

    @staticmethod
    def _createScalesForIntervalGroup(intervals : list[tuple[float,float]])->list[float]:
        intervalLengths : list[float] = [interval[1]-interval[0] for interval in intervals]
        minimum = min([length for length in intervalLengths if length > 0], default=1)
        scales = [length/minimum for length in intervalLengths]
        return scales

    @staticmethod
    def _createHistogramSolver(metadata: HistogramMetadata, initialValues: list[float], intervals: list[tuple[float,float]]) -> BarChartSolver:
        solver: BarChartSolver = UIFactory._createBarChartSolver(metadata,[initialValues],[["" for _ in initialValues]],INITIAL_PADDING,0)
        solver.SetIntervalValues(intervals) # pyright: ignore[reportArgumentType]
        return solver