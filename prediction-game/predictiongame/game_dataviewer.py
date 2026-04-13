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
    
    def Write(self, plotMetadata: PlotMetadata, solver: BarChartSolver, changedIndex: int, changedStatus: str) -> None:
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        valueEdited = changedStatus == BarChartEventHandler.BarEventRegistersLeftButton.BarLeftEvents.height
        rectangles = solver.GetRectangleDataAsList()
        for i in range(len(rectangles)-1, -1, -1):
            rec = rectangles[i]
            trueValue = rec.GetHeight()/plotMetadata.heightScaleFactor
            valueString = FormatFloat(trueValue)

            if valueEdited and i == changedIndex:
                self.dataWindow.insert("1.0",f"{rec.name} = {valueString}\n", "changing_Value")
            else:
                self.dataWindow.insert("1.0",f"{rec.name} = {valueString}\n")
        self.dataWindow.insert("1.0","rectangle name = your guess\n\n","header")
        self.dataWindow.config(state="disabled")

    def WriteSolution(self, userSolver: BarChartSolver, solutionSolver: BarChartSolver, plotMetadata: PlotMetadata):
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        self.dataWindow.tag_configure("changing_Value", foreground="red")
        userRectangles = userSolver.GetRectangleDataAsList()
        solutionRectangles = solutionSolver.GetRectangleDataAsList()

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
            result.append(lines[-1].righHeight)
        return result
    
    @staticmethod
    def _getPointNames(lines: list[ValueLine])->list[str]:
        result = []
        for line in lines:
            result.append(line.leftEnd.name)
        if len(lines) != 0:
            result.append(lines[-1].rightEnd.name)
        return result

    
    def Write(self, plotMetadata: LineChartMetadata, solver: LineChartSolver, changedIndex: int, changedStatus: str) -> None:
        self.dataWindow.config(state="normal")
        self.dataWindow.delete("1.0", "end")

        valueEdited = changedStatus == BarChartEventHandler.BarEventRegistersLeftButton.BarLeftEvents.height
        lines = solver.GetLineData()
        points = GameLineChartDataViewer._getPoints(lines)
        names = GameLineChartDataViewer._getPointNames(lines)
        
        for i in range(len(points)-1, -1, -1):
            value = points[i]
            trueValue = value/plotMetadata.heightScaleFactor
            valueString = FormatFloat(trueValue)

            if valueEdited and i == changedIndex:
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

