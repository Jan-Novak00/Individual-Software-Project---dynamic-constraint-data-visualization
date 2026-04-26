from tkinter import Text
from kiwiplots import *
from kiwiplots import ChartSolver, PlotMetadata

def FormatFloat(value: float)->str:
    if ((value >= 1e+06) or (value <= 1e-04)):
        return f"{value:.4g}"
    return str(value)

class GameDataViewer(DataViewer):
    def __init__(self, textWindow: Text):
        super().__init__(textWindow)
        self.dataWindow.tag_configure("changing_Value", foreground="red")
        self.dataWindow.tag_configure("header",font=("Arial", 12, "bold"))
        self.dataWindow.tag_configure("green_highlight",foreground="green",font=("Arial", 12, "bold"))

    @abstractmethod
    def WriteSolution(self, userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata : PlotMetadata):
        raise NotImplementedError("Method GameDataViewer.writeSolution must be declared in subclass.")

class GameBarChartDataViewer(GameDataViewer):
    def __init__(self, textWindow: Text):
        super().__init__(textWindow)
    
    def Write(self, plotMetadata: PlotMetadata, solver: BarChartSolver, changedIndex: int, valueChanged : bool) -> None:
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
    def __init__(self, textWindow: Text):
        super().__init__(textWindow)
    
    @staticmethod
    def _getPoints(lines: list[ValueLine])->list[float]:
        result = []
        for line in lines:
            result.append(line.leftHeight)
        if len(lines) != 0:
            result.append(lines[-1].rightHeight)
        return result
    
    @staticmethod
    def _getPointNames(lines: list[ValueLine])->list[str]:
        result = []
        for line in lines:
            result.append(line.leftEnd.name)
        if len(lines) != 0:
            result.append(lines[-1].rightEnd.name)
        return result

    
    def Write(self, plotMetadata: LineChartMetadata, solver: LineChartSolver, changedIndex: int, valueChanged : bool) -> None:
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
    def __init__(self, textWindow: Text):
        super().__init__(textWindow)
    
    def Write(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver, changedIndex: int, valueChanged : bool) -> None:
        """
        Displays all data for the user and highlights which data is being edited
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
    def Write(self, plotMetadata: HistogramMetadata, solver: HistogramSolver, changedIndex: int, valueChanged : bool) -> None:
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