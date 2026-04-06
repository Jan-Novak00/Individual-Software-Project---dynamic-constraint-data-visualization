from tkinter import Event
from kiwiplots import BarChartEventHandler
from .gameeventhandler import GameEventHandler
from kiwiplots.solvers import BarChartSolver, ChartSolver
from kiwiplots import BarChartMetadata

class GameBarChartEventHandler(BarChartEventHandler,GameEventHandler):
    def __init__(self, plotMetadata: BarChartMetadata, solver: BarChartSolver) -> None:
        BarChartEventHandler.__init__(self,plotMetadata,solver)
        GameEventHandler.__init__(self)
    
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
        raise NotImplementedError("DisplayOther not yet implemented")