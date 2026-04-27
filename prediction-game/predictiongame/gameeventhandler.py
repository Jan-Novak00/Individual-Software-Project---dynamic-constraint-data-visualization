from abc import ABC, abstractmethod
from kiwiplots import ChartSolver, PlotMetadata
from typing import Protocol
from tkinter import Event, Canvas, Menu, Text

class GameEventHandler(ABC):
    def __init__(self):
        self.paused = False
    
    def Pause(self):
        self.paused = True
    
    def Unpause(self):
        self.paused = False

    def IsPaused(self):
        return self.paused

    @abstractmethod
    def DisplayOther(self, otherSolver: ChartSolver):
        raise NotImplementedError("Method GameEventHandler.DisplayOther msut be definded in a subclass")
    
    @abstractmethod
    def WriteSolution(self, userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata):
        raise NotImplementedError("Method GameEventHandler.WriteSolution msut be definded in a subclass")


class EventHandlerProtocol(Protocol):
    def UpdateUI(self):
        pass
    def Pause(self):
        pass
    def Unpause(self):
        pass
    def IsPaused(self):
        pass
    def DisplayOther(self, otherSolver: ChartSolver):
        pass
    def WriteSolution(self, userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata):
        pass

    def on_left_down(self, event: Event):
        pass
    def on_mouse_move(self, event: Event):
        pass
    def on_left_up(self, event: Event):
        pass
    def check_cursor(self, event: Event):
        pass
    def on_right_down(self, event: Event):
        pass
    def on_right_up(self, event: Event):
        pass

    def initializeCanvas(self, canvas: Canvas, width : int, height : int):
        pass
    def initializeDataView(self, textWindow: Text):
        pass
    def initializeDefaultRightClickMenu(self, menu: Menu):
        pass
    def initializeRightClickMenu(self, menu: Menu):
        pass
