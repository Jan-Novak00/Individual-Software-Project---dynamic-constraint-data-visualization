from abc import ABC, abstractmethod
from kiwiplots import ChartSolver, PlotMetadata
from typing import Protocol
from tkinter import Event, Canvas, Menu, Text

class GameEventHandler(ABC):
    """Abstract base class for prediction game event handlers.

    Extends chart event handling with pause/unpause control and methods
    for displaying a comparison chart and writing the solution overlay.
    """

    def __init__(self):
        """Initializes the event handler in the unpaused state."""
        self.paused = False
    
    def Pause(self):
        """Pauses the event handler, disabling interactive editing."""
        self.paused = True
    
    def Unpause(self):
        """Resumes the event handler, re-enabling interactive editing."""
        self.paused = False

    def IsPaused(self):
        """Returns whether the event handler is currently paused."""
        return self.paused

    @abstractmethod
    def DisplayOther(self, otherSolver: ChartSolver):
        """Renders a secondary chart (e.g. the solution) on top of the canvas.

        Args:
            otherSolver (ChartSolver): Solver containing the data to display.
        """
        raise NotImplementedError("Method GameEventHandler.DisplayOther msut be definded in a subclass")
    
    @abstractmethod
    def WriteSolution(self, userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata):
        """Writes the solution comparison into the data viewer.

        Args:
            userSolver (ChartSolver): Solver containing the user's submitted data.
            solutionSolver (ChartSolver): Solver containing the correct solution data.
            plotMetadata (PlotMetadata): Metadata used for value scaling.
        """
        raise NotImplementedError("Method GameEventHandler.WriteSolution msut be definded in a subclass")


class EventHandlerProtocol(Protocol):
    """Structural protocol describing the full interface expected of a game event handler.

    Used for static type checking in place of a concrete base class, allowing any
    object that implements these methods to be used as an event handler.
    """

    def UpdateUI(self):
        """Redraws the canvas and refreshes the data view."""
        pass
    def Pause(self):
        """Pauses interactive editing."""
        pass
    def Unpause(self):
        """Resumes interactive editing."""
        pass
    def IsPaused(self):
        """Returns whether the handler is currently paused."""
        pass
    def DisplayOther(self, otherSolver: ChartSolver):
        """Renders a secondary chart on the canvas."""
        pass
    def WriteSolution(self, userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata):
        """Writes the solution comparison into the data viewer."""
        pass

    def on_left_down(self, event: Event):
        """Handles left mouse button press."""
        pass
    def on_mouse_move(self, event: Event):
        """Handles mouse movement."""
        pass
    def on_left_up(self, event: Event):
        """Handles left mouse button release."""
        pass
    def check_cursor(self, event: Event):
        """Updates the cursor based on hovered element."""
        pass
    def on_right_down(self, event: Event):
        """Handles right mouse button press."""
        pass
    def on_right_up(self, event: Event):
        """Handles right mouse button release."""
        pass

    def initializeCanvas(self, canvas: Canvas, width : int, height : int):
        """Initializes the canvas drawer."""
        pass
    def initializeDataView(self, textWindow: Text):
        """Initializes the data viewer."""
        pass
    def initializeDefaultRightClickMenu(self, menu: Menu):
        """Initializes the default right-click context menu."""
        pass
    def initializeRightClickMenu(self, menu: Menu):
        """Initializes the element-specific right-click context menu."""
        pass
