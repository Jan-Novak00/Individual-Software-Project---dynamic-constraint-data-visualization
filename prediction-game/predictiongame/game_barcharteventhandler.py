from tkinter import Event, Menu, Text
from typing import Type
from kiwiplots import BarChartEventHandler, PlotMetadata, BarChartMetadata, BarChartSolver, ChartSolver
from kiwiplots.utils import inheritdocstring
from .gameeventhandler import GameEventHandler
from .game_dataviewer import GameDataViewer, GameBarChartDataViewer

class GameBarChartEventHandler(BarChartEventHandler,GameEventHandler):
    """Game event handler for bar chart prediction games.

    Combines BarChartEventHandler with GameEventHandler to support pause/unpause
    control and solution display during a prediction game.
    """

    def __init__(self, plotMetadata: BarChartMetadata, solver: BarChartSolver, dataViewerClass: Type[GameDataViewer]) -> None:
        """Initializes the game bar chart event handler.

        Args:
            plotMetadata (BarChartMetadata): Metadata for the bar chart.
            solver (BarChartSolver): Solver containing the bar chart data.
            dataViewerClass (Type[GameDataViewer]): Data viewer class to instantiate on initialization.
        """
        BarChartEventHandler.__init__(self,plotMetadata,solver)
        GameEventHandler.__init__(self)
        self.dataViewer : GameDataViewer = self.dataViewer
        self.dataViewerType : Type[GameDataViewer] = dataViewerClass
    
    @inheritdocstring(BarChartEventHandler.initializeDataView)
    def initializeDataView(self, textWindow: Text) -> None:
        self.dataViewer = self.dataViewerType(textWindow)
    
    def initializeDefaultRightClickMenu(self, menu: Menu) -> None:
        """Disables the default right-click context menu during a prediction game."""
        return
    
    def initializeRightClickMenu(self, menu: Menu) -> None:
        """Disables the element right-click context menu during a prediction game."""
        return
    
    @inheritdocstring(BarChartEventHandler.on_left_down)
    def on_left_down(self, event: Event):
        if self.paused:
            return
        super().on_left_down(event)
    
    @inheritdocstring(BarChartEventHandler.on_mouse_move)
    def on_mouse_move(self, event):
        if self.paused:
            return
        return super().on_mouse_move(event)
    
    @inheritdocstring(BarChartEventHandler.on_right_down)
    def on_right_down(self, event: Event):
        if self.paused:
            return
        super().on_right_down(event)
    
    @inheritdocstring(BarChartEventHandler.on_left_up)
    def on_left_up(self, event):
        if self.paused:
            return
        return super().on_left_up(event)
    
    @inheritdocstring(BarChartEventHandler.on_right_up)
    def on_right_up(self, event: Event) -> None:
        if self.paused:
            return
        return super().on_right_up(event)

    @inheritdocstring(BarChartEventHandler.check_cursor)
    def check_cursor(self, event):
        if self.paused:
            return
        super().check_cursor(event)
    
    @inheritdocstring(GameEventHandler.DisplayOther)
    def DisplayOther(self, otherSolver: BarChartSolver):
        self.plotSolver.Feed(otherSolver)
        self.drawer.drawBare(self.plotMetadata, otherSolver,clear=True,specialHighlight=True,outlineOnly=False) # type: ignore
        self.drawer.draw(self.plotMetadata,self.plotSolver,outlineOnly=True, clear=False) # type: ignore
    
    @inheritdocstring(GameEventHandler.WriteSolution)
    def WriteSolution(self, userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata):
        self.dataViewer.WriteSolution(userSolver,solutionSolver,plotMetadata)
    