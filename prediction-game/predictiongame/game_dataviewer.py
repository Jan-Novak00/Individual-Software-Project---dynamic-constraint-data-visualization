from tkinter import Text
from kiwiplots import *
from kiwiplots import ChartSolver, PlotMetadata

def FormatFloat(value: float)->str:
    if ((value >= 1e+06) or (value <= 1e-04)):
        return f"{value:.4g}"
    return str(value)




class GameDataViewer(DataViewer):
    @abstractmethod
    def WriteSolution(self, userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata : PlotMetadata):
        raise NotImplementedError("Method GameDataViewer.writeSolution must be declared in subclass.")

class GameBarChartDataViewer(GameDataViewer):
    def __init__(self, textWindow: Text):
        super().__init__(textWindow)
        self.dataWindow.tag_configure("changing_Value", foreground="red")
        self.dataWindow.tag_configure("header",font=("Arial", 12, "bold"))
        self.dataWindow.tag_configure("green_highlight",foreground="green",font=("Arial", 12, "bold"))
    
    
    def Write(self, plotMetadata: PlotMetadata, solver: BarChartSolver, changedIndex: int, changedStatus: str) -> None:
        print("write called")
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
        print("WriteSolution called")
        print("write called")
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
    