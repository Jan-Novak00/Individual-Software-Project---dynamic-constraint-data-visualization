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

INITIAL_WIDTH : int   = 100
INITIAL_SPACING : int = 15
INITIAL_INNER_SPACING = 10
INITIAL_ORIGIN_X : int = 50
INITIAL_ORIGIN_Y : int = 30
INITIAL_PADDING : int = 10
INITIAL_COLOR : Union[str,int] = "blue"
INITIAL_PADDING : int = 10

class UIFactory:

    @staticmethod
    def _calculateScaleFactor(values: list[float],height: int)->float:
        """
        Compute a vertical scale factor to fit numeric values into a plot height.

        The function returns 1 when values already fall within a comfortable
        portion of the available height; otherwise it scales values so their
        maximum maps to approximately 80% of the provided `height`.

        Args:
            values (list[float]): Sequence of data values to be plotted.
            height (int): Pixel height of the plot area.

        Returns:
            float: Scale factor to multiply raw values by to convert to pixels.
        """
        scaleFactor : float = 1
        absValues = [abs(val) for val in values]
        maxValue = max(absValues,default=1)
        if not (height*0.3 <= maxValue <= height*0.7):
            scaleFactor = height*0.8/maxValue
        return scaleFactor
    
    @staticmethod
    def _rescaleList(inputList : list[float], scaleFactor : float, scaledXAxisValue: float = 0) -> list[int]:
        """
        Rescale a list of float values to integers using a scale factor and optional offset.

        Applies the formula: int(value * scaleFactor - scaledXAxisValue) to each value
        in the input list, converting them to pixel coordinates for plotting.

        Args:
            inputList (list[float]): List of float values to rescale.
            scaleFactor (float): Factor to multiply each value by.
            scaledXAxisValue (float, optional): Offset value to subtract after scaling. Defaults to 0.

        Returns:
            list[int]: List of rescaled integer values.
        """
        return [int(value*scaleFactor-scaledXAxisValue) for value in inputList]

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
        
        
        rescaledXAxisValue : float = metadata.xAxisValue*metadata.heightScaleFactor

        return CandlestickChartSolver(INITIAL_WIDTH,
                                      UIFactory._rescaleList(initialOpening, metadata.heightScaleFactor,rescaledXAxisValue),
                                      UIFactory._rescaleList(initialClosing, metadata.heightScaleFactor,rescaledXAxisValue),
                                      UIFactory._rescaleList(initialMinimum, metadata.heightScaleFactor,rescaledXAxisValue),
                                      UIFactory._rescaleList(initialMaximum, metadata.heightScaleFactor,rescaledXAxisValue),
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
        metadata : BarChartMetadata = UIFactory._createBarChartMetadata(title, xAxisLabel, yAxisLabel, initialValues, plotHeight)
        solver : ChartSolver = UIFactory._createBarChartSolver(metadata,initialValues,rectangleNames)
        pictureDrawer : PictureDrawer = BarChartPictureDrawer()
        dataWriter : DataWriter = BarChartDataWriter()
        eventHandler : EventHandler = BarChartEventHandler(metadata,solver)
        return UICore(metadata,solver,eventHandler,pictureDrawer,dataWriter,plotWidth,plotHeight)
    
    @staticmethod
    def _createBarChartMetadata(title: str, xAxisLabel: str, yAxisLabel: str, initialValues: list[list[float]], plotHeight: int):
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
        return BarChartMetadata(title,UIFactory._calculateScaleFactor(allValues,plotHeight),xAxisLabel,yAxisLabel)
    
    @staticmethod
    def _createBarChartSolver(metadata: BarChartMetadata, initialValues: list[list[float]], rectangleNames : list[list[str]], initialSpacing : int = INITIAL_SPACING, initialInnerSpacing : int = INITIAL_INNER_SPACING, widhtScales : list[list[float]] = None)->BarChartSolver:
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
        metadata : HistogramMetadata = UIFactory._createHistogramMetadata(title,xAxisLabel,yAxisLabel,initialValues,intervals,plotHeight)
        solver : ChartSolver = UIFactory._createHistogramSolver(metadata, initialValues, intervals)
        pictureDrawer : PictureDrawer = HistorgramPictureDrawer()
        dataWriter : DataWriter = HistogramDataWriter()
        eventHandler : EventHandler = HistogramEventHandler(metadata,solver)
        return UICore(metadata,solver,eventHandler,pictureDrawer,dataWriter,plotWidth,plotHeight)


    @staticmethod
    def _createHistogramMetadata(title: str, xAxisLabel: str, yAxisLabel: str, initialValues : list[float], intervals: list[tuple[float,float]], plotHeight: int)-> HistogramMetadata:
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
        heightScaleFactor : float = UIFactory._calculateScaleFactor(initialValues,plotHeight)
        widthScales = [UIFactory._createScalesForIntervalGroup(intervals)]
        return HistogramMetadata(title, heightScaleFactor, widthScales, xAxisLabel, yAxisLabel)

    @staticmethod
    def _createScalesForIntervalGroup(intervals : list[tuple[float,float]])->list[float]:
        """
        Compute relative width scale factors for a group of histogram intervals.

        The smallest positive interval length maps to scale 1.0; other
        intervals are scaled relative to that minimum length.

        Args:
            intervals (list[tuple[float,float]]): List of (start, end) bin ranges.

        Returns:
            list[float]: Scale factors proportional to interval lengths.
        """
        intervalLengths : list[float] = [interval[1]-interval[0] for interval in intervals]
        minimum = min([length for length in intervalLengths if length > 0], default=1)
        scales = [length/minimum for length in intervalLengths]
        return scales

    @staticmethod
    def _createHistogramSolver(plotMetadata: HistogramMetadata, initialValues: list[float], intervals: list[tuple[float,float]]) -> BarChartSolver:
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
                                                                 widhtScales=[UIFactory._createIntervalScales(intervals)])
        solver.SetIntervalValues(intervals) # pyright: ignore[reportArgumentType]
        return solver
    
    @staticmethod
    def _createIntervalScales(intervals : list[tuple[float,float]])->list[float]:
        intervalLengths : list[float] = [interval[1]-interval[0] for interval in intervals]
        minimum = min([length for length in intervalLengths if length > 0], default=1)
        scales : list[float] = [length/minimum for length in intervalLengths]
        return scales
    
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
        metadata : LineChartMetadata = UIFactory._createLineChartMetadata(title,xAxisValue,initialValues,xAxisLabel,yAxisLabel, plotHeight)
        solver : LineChartSolver = UIFactory._createLineChartSolver(metadata, initialValues, names)
        pictureDrawer : PictureDrawer = None # pyright: ignore[reportAssignmentType] #TODO
        dataWriter : DataWriter = None # pyright: ignore[reportAssignmentType] #TODO
        eventHandler : EventHandler = LineChartEventHandler(metadata, solver)
        return UICore(metadata,solver,eventHandler,pictureDrawer,dataWriter,plotWidth,plotHeight)
    
    @staticmethod
    def _createLineChartMetadata(title: str, xAxisValue : float, values : list[float], xAxisLabel : str, yAxisLabel : str, height : int)->LineChartMetadata:
        heightScaleFactor : float = UIFactory._calculateScaleFactor(values,height)
        return LineChartMetadata(title,INITIAL_COLOR,heightScaleFactor,xAxisValue,xAxisLabel,yAxisLabel)
    
    @staticmethod
    def _createLineChartSolver(metadata : LineChartMetadata, initialValues : list[float], names : list[str]):
        rescaledValues : list[int] = UIFactory._rescaleList(initialValues,metadata.heightScaleFactor,metadata.xAxisValue)
        return LineChartSolver(INITIAL_WIDTH,rescaledValues,names,INITIAL_ORIGIN_X,INITIAL_ORIGIN_Y,INITIAL_PADDING) # pyright: ignore[reportArgumentType]
        
    