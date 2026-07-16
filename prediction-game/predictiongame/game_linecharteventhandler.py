from tkinter import Event, Text, Menu
from typing import Type
from kiwiplots import LineChartEventHandler, PlotMetadata, LineChartMetadata, LineChartSolver, ChartSolver
from kiwiplots.utils import inheritdocstring
from .gameeventhandler import GameEventHandler
from .game_dataviewer import GameDataViewer, GameLineChartDataViewer

class GameLineChartEventHandler(LineChartEventHandler, GameEventHandler):
    """Game event handler for line chart prediction games.

    Combines LineChartEventHandler with GameEventHandler to support pause/unpause
    control and solution display during a prediction game. The solution line is
    drawn in a configurable color.
    """

    def __init__(self, plotMetadata: LineChartMetadata, solver: LineChartSolver, dataViewerClass: Type[GameDataViewer], solutionColor : str):
        """Initializes the game line chart event handler.

        Args:
            plotMetadata (LineChartMetadata): Metadata for the line chart.
            solver (LineChartSolver): Solver containing the line chart data.
            dataViewerClass (Type[GameDataViewer]): Data viewer class to instantiate on initialization.
            solutionColor (str): Color used to render the solution line.
        """
        LineChartEventHandler.__init__(self,plotMetadata, solver)
        GameEventHandler.__init__(self)
        self.dataViewer : GameDataViewer = self.dataViewer
        self.dataViewerType : Type[GameDataViewer] = dataViewerClass
        self.solutionColor : str | int = solutionColor
    
    @inheritdocstring(LineChartEventHandler.initializeDataView)
    def initializeDataView(self, textWindow: Text) -> None:
        self.dataViewer = self.dataViewerType(textWindow)
    
    def initializeDefaultRightClickMenu(self, menu: Menu) -> None:
        """Initializes the default context menu with mode-switching only (no add-point command)."""
        self.valueModeLabel = "Switch to value modification mode"
        self.horizontalModeLabel = "Switch to horizontal layout modification mode"
        
        self.defaultMenu = menu
        self.defaultMenu.add_command(command=self._changeMode)
        self.changeModeIndex = self.defaultMenu.index("end")
        assert self.changeModeIndex is not None
        self.defaultMenu.entryconfig(self.changeModeIndex,label=self.horizontalModeLabel)
    
    @inheritdocstring(LineChartEventHandler.on_left_down)
    def on_left_down(self, event: Event):
        if self.paused:
            return
        super().on_left_down(event)
    
    @inheritdocstring(LineChartEventHandler.on_mouse_move)
    def on_mouse_move(self, event):
        if self.paused:
            return
        return super().on_mouse_move(event)
    
    def on_right_down(self, event: Event):
        """Shows the default context menu unless paused."""
        if self.paused:
            return
        assert self.defaultMenu
        self.defaultMenu.post(event.x_root,event.y_root)
    
    @inheritdocstring(LineChartEventHandler.on_left_up)
    def on_left_up(self, event):
        if self.paused:
            return
        return super().on_left_up(event)
    
    @inheritdocstring(LineChartEventHandler.on_right_up)
    def on_right_up(self, event: Event) -> None:
        if self.paused:
            return
        return super().on_right_up(event)

    @inheritdocstring(LineChartEventHandler.check_cursor)
    def check_cursor(self, event):
        if self.paused:
            return
        super().check_cursor(event)
    
    @inheritdocstring(GameEventHandler.DisplayOther)
    def DisplayOther(self, otherSolver: LineChartSolver):
        assert self.drawer
        self.plotSolver.Feed(otherSolver)
        currentColor = self.plotMetadata.color
        self.plotMetadata.color = self.solutionColor
        self.drawer.drawBare(self.plotMetadata, otherSolver,clear=True,specialHighlight=True,outlineOnly=False)
        self.plotMetadata.color = currentColor
        self.drawer.draw(self.plotMetadata,self.plotSolver,outlineOnly=True, clear=False)
    
    @inheritdocstring(GameEventHandler.WriteSolution)
    def WriteSolution(self, userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata):
        self.dataViewer.WriteSolution(userSolver,solutionSolver,plotMetadata)