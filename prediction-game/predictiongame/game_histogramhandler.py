from tkinter import Event, Menu, Text
from typing import Type
from kiwiplots import HistogramEventHandler, PlotMetadata, HistogramMetadata, HistogramSolver, ChartSolver
from .gameeventhandler import GameEventHandler
from .game_dataviewer import GameDataViewer, GameBarChartDataViewer

class GameHistogramEventHandler(HistogramEventHandler,GameEventHandler):
    def __init__(self, plotMetadata: HistogramMetadata, solver: HistogramSolver, dataViewerClass: Type[GameDataViewer]) -> None:
        HistogramEventHandler.__init__(self,plotMetadata,solver)
        GameEventHandler.__init__(self)
        self.dataViewer : GameDataViewer = self.dataViewer
        self.dataViewerType : Type[GameDataViewer] = dataViewerClass
    
    def initializeDataView(self, textWindow: Text) -> None:
        self.dataViewer = self.dataViewerType(textWindow)
    
    def initializeDefaultRightClickMenu(self, menu: Menu) -> None:
        return
    
    def initializeRightClickMenu(self, menu: Menu) -> None:
        return
    
    def on_left_down(self, event: Event):
        if self.paused:
            return
        super().on_left_down(event)
    
    def on_mouse_move(self, event):
        if self.paused:
            return
        return super().on_mouse_move(event)
    
    def on_right_down(self, event: Event):
        if self.paused:
            return
        super().on_right_down(event)
    
    def on_left_up(self, event):
        if self.paused:
            return
        return super().on_left_up(event)
    
    def on_right_up(self, event: Event) -> None:
        if self.paused:
            return
        return super().on_right_up(event)

    def check_cursor(self, event):
        if self.paused:
            return
        super().check_cursor(event)
    
    def DisplayOther(self, otherSolver: HistogramSolver): # pyright: ignore[reportIncompatibleMethodOverride]
        self.plotSolver.Feed(otherSolver)
        self.drawer.drawBare(self.plotMetadata, otherSolver,clear=True,specialHighlight=True,outlineOnly=False)
        self.drawer.draw(self.plotMetadata,self.plotSolver,outlineOnly=True, clear=False)
    
    def WriteSolution(self, userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata):
        self.dataViewer.WriteSolution(userSolver,solutionSolver,plotMetadata)
    