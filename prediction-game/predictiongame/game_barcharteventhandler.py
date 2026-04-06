from tkinter import Event
from kiwiplots import BarChartEventHandler
from kiwiplots.plotui.plotmetadata import PlotMetadata
from .gameeventhandler import GameEventHandler
from kiwiplots.solvers import BarChartSolver, ChartSolver
from kiwiplots import BarChartMetadata
from game_dataviewer import GameDataViewer

class GameBarChartEventHandler(BarChartEventHandler,GameEventHandler):
    def __init__(self, plotMetadata: BarChartMetadata, solver: BarChartSolver) -> None:
        BarChartEventHandler.__init__(self,plotMetadata,solver)
        GameEventHandler.__init__(self)
        self.dataViewer : GameDataViewer = self.dataViewer
    
    def on_left_down(self, event: Event):
        if self.paused:
            return
        super().on_left_down(event)
    
    def on_right_down(self, event: Event):
        if self.paused:
            return
        super().on_right_down(event)
    
    def check_cursor(self, event):
        if self.paused:
            return
        super().check_cursor(event)
    
    def DisplayOther(self, otherSolver: BarChartSolver):
        self.plotSolver.Feed(otherSolver)
        self.drawer.drawBare(self.plotMetadata, otherSolver,clear=True,specialHighlight=True,outlineOnly=False)
        self.drawer.draw(self.plotMetadata,self.plotSolver,outlineOnly=True, clear=False)
    
    def WriteSolution(self, userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata):
        self.dataViewer.WriteSolution(userSolver,solutionSolver,plotMetadata)