from tkinter import Text
from kiwiplots import *
from kiwiplots import ChartSolver, PlotMetadata

def FormatFloat(value: float)->str:
    """Formats a float for display, using scientific notation for very large or very small values.

    Args:
        value (float): The value to format.

    Returns:
        str: A human-readable string representation of the value.
    """
    if ((value >= 1e+06) or (value <= 1e-04)):
        return f"{value:.4g}"
    return str(value)

class GameDataViewer(DataViewer):
    """Abstract data viewer for prediction game sessions.

    Extends DataViewer with styled text tags and an abstract WriteSolution method
    for displaying the user's guesses alongside the correct solution.
    """

    def __init__(self, textWindow: Text):
        """Initializes the game data viewer and configures text display tags."""
        super().__init__(textWindow)
        self.dataWindow.tag_configure("changing_Value", foreground="red")
        self.dataWindow.tag_configure("header",font=("Arial", 12, "bold"))
        self.dataWindow.tag_configure("green_highlight",foreground="green",font=("Arial", 12, "bold"))

    @abstractmethod
    def WriteSolution(self, userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata : PlotMetadata):
        """Displays the user's guesses alongside the correct solution values.

        Args:
            userSolver (ChartSolver): Solver containing the user's submitted data.
            solutionSolver (ChartSolver): Solver containing the correct solution.
            plotMetadata (PlotMetadata): Metadata used for value scaling.
        """
        raise NotImplementedError("Method GameDataViewer.writeSolution must be declared in subclass.")

class GameBarChartDataViewer(GameDataViewer):
    """Game data viewer for bar chart prediction games.

    Displays bar names and values, highlighting the currently edited bar in red.
    After the game ends, shows each bar's value alongside the solution in green.
    """

    def __init__(self, textWindow: Text):
        """Initializes the bar chart game data viewer."""
        super().__init__(textWindow)
    
    def Write(self, plotMetadata: PlotMetadata, solver: BarChartSolver, changedIndex: int, valueChanged : bool) -> None:
        """Displays the current bar values, highlighting the bar being edited.

        Args:
            plotMetadata (PlotMetadata): Metadata for value scaling.
            solver (BarChartSolver): Solver containing the current bar data.
            changedIndex (int): Index of the bar currently being edited.
            valueChanged (bool): Whether a bar value is actively being changed.
        """
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        
        rectangles = solver.GetBarDataAsList()
        for i in range(len(rectangles)-1, -1, -1):
            rec = rectangles[i]
            trueValue = rec.GetHeight()/plotMetadata.heightScaleFactor
            valueString = FormatFloat(trueValue)

            if valueChanged and i == changedIndex:
                self.dataWindow.insert("1.0",f"{rec.name} = {valueString}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"{rec.name} = {valueString}\n")
        self.dataWindow.insert("1.0","rectangle name = your guess\n\n","header")
        self.dataWindow.config(state="disabled")

    def WriteSolution(self, userSolver: BarChartSolver, solutionSolver: BarChartSolver, plotMetadata: PlotMetadata):
        """Displays each bar's guessed value next to the solution value.

        Args:
            userSolver (BarChartSolver): Solver containing the user's bar data.
            solutionSolver (BarChartSolver): Solver containing the solution bar data.
            plotMetadata (PlotMetadata): Metadata for value scaling.
        """
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        userRectangles = userSolver.GetBarDataAsList()
        solutionRectangles = solutionSolver.GetBarDataAsList()

        assert len(userRectangles) == len(solutionRectangles)

        for i in range(len(userRectangles)-1, -1, -1):
            userRec = userRectangles[i]
            solutionRec = solutionRectangles[i]
            trueValueUser, trueValueSolution = userRec.GetHeight()/plotMetadata.heightScaleFactor, solutionRec.GetHeight()/plotMetadata.heightScaleFactor
            valueStringUser = FormatFloat(trueValueUser)
            valueStringSolution = FormatFloat(trueValueSolution)
            self.dataWindow.insert("1.0",")\n")
            self.dataWindow.insert("1.0",f"{valueStringSolution}","green_highlight")
            self.dataWindow.insert("1.0",f"{userRec.name} = {valueStringUser} (")
        
        self.dataWindow.insert("1.0",")\n\n","header")
        self.dataWindow.insert("1.0","real value","green_highlight")
        self.dataWindow.insert("1.0","rectangle name = your guess (","header")
        self.dataWindow.config(state="disabled")

class GameLineChartDataViewer(GameDataViewer):
    """Game data viewer for line chart prediction games.

    Displays point names and values, highlighting the currently edited point in red.
    After the game ends, shows each point's value alongside the solution in green.
    """

    def __init__(self, textWindow: Text):
        """Initializes the line chart game data viewer."""
        super().__init__(textWindow)
    
    @staticmethod
    def _getPoints(lines: list[ValueLine])->list[float]:
        """Extracts the Y height of every point from a list of lines."""
        result = []
        for line in lines:
            result.append(line.leftHeight)
        if len(lines) != 0:
            result.append(lines[-1].rightHeight)
        return result
    
    @staticmethod
    def _getPointNames(lines: list[ValueLine])->list[str]:
        """Extracts the name of every point from a list of lines."""
        result = []
        for line in lines:
            result.append(line.leftEnd.name)
        if len(lines) != 0:
            result.append(lines[-1].rightEnd.name)
        return result

    
    def Write(self, plotMetadata: LineChartMetadata, solver: LineChartSolver, changedIndex: int, valueChanged : bool) -> None:
        """Displays the current point values, highlighting the point being edited.

        Args:
            plotMetadata (LineChartMetadata): Metadata for value scaling.
            solver (LineChartSolver): Solver containing the current line data.
            changedIndex (int): Index of the point currently being edited.
            valueChanged (bool): Whether a point value is actively being changed.
        """
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        
        lines = solver.GetLineData()
        points = GameLineChartDataViewer._getPoints(lines)
        names = GameLineChartDataViewer._getPointNames(lines)
        
        for i in range(len(points)-1, -1, -1):
            value = points[i]
            trueValue = value/plotMetadata.heightScaleFactor
            valueString = FormatFloat(trueValue)

            if valueChanged and i == changedIndex:
                self.dataWindow.insert("1.0",f"{names[i]} = {valueString}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"{names[i]} = {valueString}\n")
        self.dataWindow.insert("1.0","point name = your guess\n\n","header")
        self.dataWindow.config(state="disabled")
    
    def WriteSolution(self, userSolver: LineChartSolver, solutionSolver: LineChartSolver, plotMetadata: LineChartMetadata):
        """Displays each point's guessed value next to the solution value.

        Args:
            userSolver (LineChartSolver): Solver containing the user's line data.
            solutionSolver (LineChartSolver): Solver containing the solution line data.
            plotMetadata (LineChartMetadata): Metadata for value scaling.
        """
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        userLines = userSolver.GetLineData()
        solutionLines = solutionSolver.GetLineData()

        userPoints = GameLineChartDataViewer._getPoints(userLines)
        solutionPoints = GameLineChartDataViewer._getPoints(solutionLines)
        names = GameLineChartDataViewer._getPointNames(userLines)

        assert len(userPoints) == len(solutionPoints)

        for i in range(len(userPoints)-1, -1, -1):
            userValue = userPoints[i]
            solutionValue = solutionPoints[i]
            trueValueUser, trueValueSolution = userValue/plotMetadata.heightScaleFactor, solutionValue/plotMetadata.heightScaleFactor
            valueStringUser = FormatFloat(trueValueUser)
            valueStringSolution = FormatFloat(trueValueSolution)
            self.dataWindow.insert("1.0",")\n")
            self.dataWindow.insert("1.0",f"{valueStringSolution}","green_highlight")
            self.dataWindow.insert("1.0",f"{names[i]} = {valueStringUser} (")
        
        self.dataWindow.insert("1.0",")\n\n","header")
        self.dataWindow.insert("1.0","real value","green_highlight")
        self.dataWindow.insert("1.0","rectangle name = your guess (","header")
        self.dataWindow.config(state="disabled")

class GameCandlestickChartDataViewer(GameDataViewer):
    """Game data viewer for candlestick chart prediction games.

    Displays opening, closing, minimum, and maximum values for each candle,
    highlighting the candle being edited. After the game ends, shows each
    candle's values alongside the solution in green.
    """

    def __init__(self, textWindow: Text):
        """Initializes the candlestick chart game data viewer."""
        super().__init__(textWindow)
    
    def Write(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver, changedIndex: int, valueChanged : bool) -> None:
        """Displays the current candle values, highlighting the candle being edited.

        Args:
            plotMetadata (CandlesticPlotMetadata): Metadata for value scaling.
            solver (CandlestickChartSolver): Solver containing the current candle data.
            changedIndex (int): Index of the candle currently being edited.
            valueChanged (bool): Whether a candle value is actively being changed.
        """
        xAxisValue = plotMetadata.xAxisValue
        scaleFactor = plotMetadata.heightScaleFactor
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        eventType = CandlesticEventHandler.CandleEventRegistersLeftButton.CandleLeftEvents
        
        candles = solver.GetCandleData()

        for i in range(len(candles)-1, -1, -1):
            candle = candles[i]
            openingValue = FormatFloat(candle.openingCorner.Y/scaleFactor + xAxisValue)
            closingValue = FormatFloat(candle.closingCorner.Y/scaleFactor + xAxisValue)
            maximumValue = FormatFloat(candle.wickTop.Y/scaleFactor + xAxisValue)
            minimumValue = FormatFloat(candle.wickBottom.Y/scaleFactor + xAxisValue/scaleFactor)
            
            string = f"{candle.name}:\t{openingValue}, {closingValue}, {minimumValue}, {maximumValue}\n"
            if valueChanged and i == changedIndex:
                self.dataWindow.insert("1.0",f"{string}", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"{string}")
        self.dataWindow.insert("1.0","candle:\t opening, closing, min, max\n\n","header")
        self.dataWindow.config(state="disabled")

    def WriteSolution(self, userSolver: CandlestickChartSolver, solutionSolver: CandlestickChartSolver, plotMetadata: CandlesticPlotMetadata):
        """Displays each candle's guessed values next to the solution values.

        Args:
            userSolver (CandlestickChartSolver): Solver containing the user's candle data.
            solutionSolver (CandlestickChartSolver): Solver containing the solution candle data.
            plotMetadata (CandlesticPlotMetadata): Metadata for value scaling.
        """
        xAxisValue = plotMetadata.xAxisValue
        scaleFactor = plotMetadata.heightScaleFactor
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        userCandles = userSolver.GetCandleData()
        solutionCandles = solutionSolver.GetCandleData()

        assert len(userCandles) == len(solutionCandles)

        for i in range(len(userCandles)-1, -1, -1):
            userCandle = userCandles[i]
            solutionCandle = solutionCandles[i]

            UopeningValue = FormatFloat(userCandle.openingCorner.Y/scaleFactor + xAxisValue)
            UclosingValue = FormatFloat(userCandle.closingCorner.Y/scaleFactor + xAxisValue)
            UmaximumValue = FormatFloat(userCandle.wickTop.Y/scaleFactor + xAxisValue)
            UminimumValue = FormatFloat(userCandle.wickBottom.Y/scaleFactor + xAxisValue/scaleFactor)
            
            SopeningValue = FormatFloat(solutionCandle.openingCorner.Y/scaleFactor + xAxisValue)
            SclosingValue = FormatFloat(solutionCandle.closingCorner.Y/scaleFactor + xAxisValue)
            SmaximumValue = FormatFloat(solutionCandle.wickTop.Y/scaleFactor + xAxisValue)
            SminimumValue = FormatFloat(solutionCandle.wickBottom.Y/scaleFactor + xAxisValue/scaleFactor)
            
            self.dataWindow.insert("1.0",")\n")
            self.dataWindow.insert("1.0",SmaximumValue,"green_highlight")
            self.dataWindow.insert("1.0",f"), {UmaximumValue} (")
            self.dataWindow.insert("1.0",SminimumValue,"green_highlight")
            self.dataWindow.insert("1.0",f"), {UminimumValue} (")
            self.dataWindow.insert("1.0",SclosingValue,"green_highlight")
            self.dataWindow.insert("1.0",f"), {UclosingValue} (")
            self.dataWindow.insert("1.0",SopeningValue,"green_highlight")
            self.dataWindow.insert("1.0",f"{userCandle.name}:\t{UopeningValue} (")

        self.dataWindow.insert("1.0","Green values represent the solution\n\n","green_highlight")
        self.dataWindow.insert("1.0","candle:\t opening, closing, min, max\n","header")
        self.dataWindow.config(state="disabled")

class GameHistogramDataViewer(GameDataViewer):
    """Game data viewer for histogram prediction games.

    Displays bucket intervals and their values, highlighting the bucket being
    edited. After the game ends, shows each bucket's value alongside the solution.
    """

    def Write(self, plotMetadata: HistogramMetadata, solver: HistogramSolver, changedIndex: int, valueChanged : bool) -> None:
        """Displays the current bucket values, highlighting the bucket being edited.

        Args:
            plotMetadata (HistogramMetadata): Metadata for value scaling.
            solver (HistogramSolver): Solver containing the current histogram data.
            changedIndex (int): Index of the bucket currently being edited.
            valueChanged (bool): Whether a bucket value is actively being changed.
        """
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        
        rectangles : list[ValueBucket] = solver.GetRectangleDataAsList() # pyright: ignore[reportAssignmentType]

        for i in range(len(rectangles)-1, -1, -1):
            rec = rectangles[i]
            trueValue = rec.GetHeight()/plotMetadata.heightScaleFactor
            valueString = ""
            if ((trueValue >= 1e+06) or (trueValue <= 1e-04)):
                valueString = f"{trueValue:.4g}"
            else:
                valueString = str(trueValue)


            if valueChanged and i == changedIndex:
                self.dataWindow.insert("1.0",f"({rec.interval[0]}, {rec.interval[1]}) = {valueString}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"({rec.interval[0]}, {rec.interval[1]}) = {valueString}\n")
        self.dataWindow.insert("1.0","(interval start, interval end) = value\n","header")
        self.dataWindow.config(state="disabled")
    
    def WriteSolution(self, userSolver: HistogramSolver, solutionSolver: HistogramSolver, plotMetadata: HistogramMetadata):
        """Displays each bucket's guessed value next to the solution value.

        Args:
            userSolver (HistogramSolver): Solver containing the user's histogram data.
            solutionSolver (HistogramSolver): Solver containing the solution histogram data.
            plotMetadata (HistogramMetadata): Metadata for value scaling.
        """
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        userRectangles : list[ValueBucket] = userSolver.GetRectangleDataAsList() # pyright: ignore[reportAssignmentType]
        solutionRectangles : list[ValueBucket] = solutionSolver.GetRectangleDataAsList() # pyright: ignore[reportAssignmentType]

        assert len(userRectangles) == len(solutionRectangles)

        for i in range(len(solutionRectangles)-1, -1, -1):
            Urec = userRectangles[i]
            Srec = solutionRectangles[i]
            trueUValue = Urec.GetHeight()/plotMetadata.heightScaleFactor
            trueSValue = Srec.GetHeight()/plotMetadata.heightScaleFactor
            
            UvalueString = FormatFloat(trueUValue)
            SvalueString = FormatFloat(trueSValue)

            self.dataWindow.insert("1.0",")\n")
            self.dataWindow.insert("1.0", SvalueString, "green_highlight")
            self.dataWindow.insert("1.0",f"({Urec.interval[0]}, {Urec.interval[1]}) = {UvalueString} (")
        self.dataWindow.insert("1.0",")\n","header")
        self.dataWindow.insert("1.0","solution","green_highlight")
        self.dataWindow.insert("1.0","(interval start, interval end) = value (","header")
        self.dataWindow.config(state="disabled")