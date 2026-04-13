from .uicore import UICore
from .plotmetadata import *
from kiwiplots.solvers import *
from .eventhandlers import EventHandler
from .candlesticeventhandler import CandlesticEventHandler
from .barcharteventhandler import BarChartEventHandler
from .histogrameventhandler import HistogramEventHandler
from .linecharteventhandler import LineChartEventHandler
from .picturedrawers import *
from .datawriters import *
from numpy import abs
from .datautils import *
from .uiconstants import *

class UIFactory:
    @staticmethod
    def CreateCandlesticChart(title: str, 
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
        metadata : CandlesticPlotMetadata = CreateCandlesticChartMetadata(title,xAxisLabel,yAxisLabel, xAxisValue, initialOpening,initialClosing,initialMinimum,initialMaximum,plotHeight)
        solver : ChartSolver = UIFactory._createCandlesticChartSolver(metadata,initialOpening,initialClosing,initialMinimum,initialMaximum,names)
        eventHandler : EventHandler = CandlesticEventHandler(metadata, solver)
        pictureDrawer : PictureDrawer = CandlesticPictureDrawer()
        dataWriter : DataWriter = CandlesticDataWriter()
        return UICore(metadata,solver,eventHandler,pictureDrawer,dataWriter,plotWidth,plotHeight)


    
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
        
        
        rescaledXAxisValue : float = metadata.xAxisValue*metadata.heightScaleFactor

        return CandlestickChartSolver(INITIAL_WIDTH,
                                      RescaleList(initialOpening, metadata.heightScaleFactor,rescaledXAxisValue),
                                      RescaleList(initialClosing, metadata.heightScaleFactor,rescaledXAxisValue),
                                      RescaleList(initialMinimum, metadata.heightScaleFactor,rescaledXAxisValue),
                                      RescaleList(initialMaximum, metadata.heightScaleFactor,rescaledXAxisValue),
                                      INITIAL_SPACING,
                                      names,
                                      INITIAL_ORIGIN_X,
                                      INITIAL_ORIGIN_Y)

    @staticmethod
    def CreateBarChart( title: str, 
                        xAxisLabel : str, 
                        yAxisLabel : str, 
                        initialValues : list[list[float]],
                        rectangleNames : list[list[str]],
                        plotWidth: int,
                        plotHeight: int
                        )->UICore:
        """
        Create a full bar chart UI component.

        Builds `BarChartMetadata`, a `BarChartSolver`, picture drawer, data writer
        and event handler and returns a configured `UICore` for displaying the
        bar chart.

        Args:
            title (str): Chart title.
            xAxisLabel (str): X-axis label.
            yAxisLabel (str): Y-axis label.
            initialValues (list[list[float]]): Grouped numeric values for the bars.
            rectangleNames (list[list[str]]): Labels for individual bars within groups.
            plotWidth (int): Width of the plot area in pixels.
            plotHeight (int): Height of the plot area in pixels.

        Returns:
            UICore: Configured UI component for the bar chart.
        """
        metadata : BarChartMetadata = CreateBarChartMetadata(title, xAxisLabel, yAxisLabel, initialValues, plotHeight)
        solver : ChartSolver = UIFactory._createBarChartSolver(metadata,initialValues,rectangleNames)
        pictureDrawer : PictureDrawer = BarChartPictureDrawer()
        dataWriter : DataWriter = BarChartDataWriter()
        eventHandler : EventHandler = BarChartEventHandler(metadata,solver)
        return UICore(metadata,solver,eventHandler,pictureDrawer,dataWriter,plotWidth,plotHeight)
    
    
    @staticmethod
    def _createBarChartSolver(metadata: BarChartMetadata, initialValues: list[list[float]], rectangleNames : list[list[str]], initialSpacing : int = INITIAL_SPACING, initialInnerSpacing : int = INITIAL_INNER_SPACING, widhtScales : list[list[float]] = None)->BarChartSolver: # pyright: ignore[reportArgumentType]
        """
        Create a `BarChartSolver` from grouped values and names.

        Rescales each numeric value using the metadata's height scale factor and
        initializes a `BarChartSolver` with layout parameters.

        Args:
            metadata (BarChartMetadata): Chart metadata including scale factor.
            initialValues (list[list[float]]): Grouped numeric values.
            rectangleNames (list[list[str]]): Labels per bar.
            initialSpacing (int): Spacing between groups of bars.
            initialInnerSpacing (int): Spacing between bars within a group.

        Returns:
            BarChartSolver: Solver configured with rescaled integer bar heights.
        """
        rescaledGroupValues : list[list[int]] = []
        for group in initialValues:
            rescaledGroupValues.append([int(metadata.heightScaleFactor*value) for value in group])
        
        return BarChartSolver(INITIAL_WIDTH,rescaledGroupValues,initialSpacing,initialInnerSpacing,rectangleNames,INITIAL_ORIGIN_X,INITIAL_ORIGIN_Y, widhtScales)
        

    @staticmethod
    def CreateHistogram(title: str,
                        xAxisLabel: str,
                        yAxisLabel: str,
                        initialValues: list[float], 
                        intervals: list[tuple[float,float]],
                        plotWidth: int,
                        plotHeight: int):
        """
        Create a histogram UI component.

        Prepares `HistogramMetadata` (including per-interval width scales), a
        `BarChartSolver` adapted for histogram rendering, and related UI pieces
        and returns `UICore` instance.

        Args:
            title (str): Histogram title.
            xAxisLabel (str): Label for the x-axis.
            yAxisLabel (str): Label for the y-axis.
            initialValues (list[float]): Values to be binned into intervals.
            intervals (list[tuple[float,float]]): List of (start, end) tuples for bins.
            plotWidth (int): Pixel width of the plot.
            plotHeight (int): Pixel height of the plot.

        Returns:
            UICore: Configured histogram UI component.
        """
        metadata : HistogramMetadata = CreateHistogramMetadata(title,xAxisLabel,yAxisLabel,initialValues,intervals,plotHeight)
        solver : ChartSolver = UIFactory._createHistogramSolver(metadata, initialValues, intervals)
        pictureDrawer : PictureDrawer = HistorgramPictureDrawer()
        dataWriter : DataWriter = HistogramDataWriter()
        eventHandler : EventHandler = HistogramEventHandler(metadata,solver)
        return UICore(metadata,solver,eventHandler,pictureDrawer,dataWriter,plotWidth,plotHeight)

    @staticmethod
    def _createHistogramSolver(plotMetadata: HistogramMetadata, initialValues: list[float], intervals: list[tuple[float,float]]) -> HistogramSolver:
        """
        Create a `BarChartSolver` configured for histogram rendering.

        This function reuses the bar chart solver interface to represent
        histogram bars, then sets interval ranges on the solver so it can
        position and size bins correctly.

        Args:
            metadata (HistogramMetadata): Metadata including width scales.
            initialValues (list[float]): Values binned into intervals.
            intervals (list[tuple[float,float]]): Bin ranges.

        Returns:
            BarChartSolver: Solver prepared for histogram visualization.
        """
        solver: BarChartSolver = UIFactory._createBarChartSolver(metadata=plotMetadata,
                                                                 initialValues=[initialValues],
                                                                 rectangleNames=[["" for _ in initialValues]],
                                                                 initialSpacing=INITIAL_PADDING,
                                                                 initialInnerSpacing=0,
                                                                 widhtScales=[CreateIntervalScales(intervals)])
        solver.SetIntervalValues(intervals) # pyright: ignore[reportArgumentType]
        return HistogramSolver(solver)
    
    @staticmethod
    def CreateLineChart(title: str, 
                        xAxisLabel: str, 
                        yAxisLabel: str, 
                        xAxisValue : float, 
                        initialValues: list[float], 
                        names: list[str], 
                        plotWidth: int,
                        plotHeight: int
                        )->UICore:
        metadata : LineChartMetadata = CreateLineChartMetadata(title,xAxisValue,initialValues,xAxisLabel,yAxisLabel, plotHeight)
        solver : LineChartSolver = UIFactory._createLineChartSolver(metadata, initialValues, names)
        pictureDrawer : PictureDrawer = None # pyright: ignore[reportAssignmentType] #TODO
        dataWriter : DataWriter = None # pyright: ignore[reportAssignmentType] #TODO
        eventHandler : EventHandler = LineChartEventHandler(metadata, solver)
        return UICore(metadata,solver,eventHandler,pictureDrawer,dataWriter,plotWidth,plotHeight)
    
    @staticmethod
    def _createLineChartSolver(metadata : LineChartMetadata, initialValues : list[float], names : list[str]):
        rescaledValues : list[int] = RescaleList(initialValues,metadata.heightScaleFactor,metadata.xAxisValue)
        return LineChartSolver(INITIAL_WIDTH,rescaledValues,names,INITIAL_ORIGIN_X,INITIAL_ORIGIN_Y,INITIAL_PADDING) # pyright: ignore[reportArgumentType]
        
    