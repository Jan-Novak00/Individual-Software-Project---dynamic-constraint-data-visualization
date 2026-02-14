from abc import ABC
from .plotmetadata import PlotMetadata
import tkinter as tk
from kiwiplots.plotelement import ValuePoint2D
from tkinter import simpledialog 

class EventHandler(ABC):
    """
    Abstract class for handling user interactions with the plot on a tkinter Canvas.
    
    Manages mouse events, cursor changes, and updates to the plot data and visualization.
    Implementations are specific to the type of plot being displayed.
    """
    def __init__(self, plotMetadata: PlotMetadata) -> None:
        """
        Initializes the CanvasHandler with plot metadata.
        After initialization CanvasHandler should be provided with tkinter widgets.

        Args:
            plotMetadata: Metadata about the plot including scale factor and axis values.
        """
        self.canvas : tk.Canvas = None                                                                                  # type: ignore
        self.defaultMenu : tk.Menu = None                                                                               # type: ignore
        self.elementMenu : tk.Menu = None                                                                               # type: ignore
        self.drawer : CanvasDrawer = None                                                                               # type: ignore
        self.dataViewer : DataViewer = None                                                                             # type: ignore
        self.plotSolver : ChartSolver = None                                                                            # type: ignore
        self.plotMetada = plotMetadata                           #ToDo  typing
        self._setEventRegistersLeftButton()
        self._setEventRegistersRightButton()
    
    def UpdateUI(self):
        """
        Updates both the canvas drawing and the data viewer display.
        
        Refreshes the visualization to reflect any changes in the plot data.
        """
        self._updateCanvas()
        self._updateDataView()
    
    def _setEventRegistersLeftButton(self):
        """
        Variables which register information about events regarding the left mouse button
        """
        self.dragEdge = None                # which edge is being dragged
        self.dragStart = ValuePoint2D(0,0)  # where draging started
        self.dragIndex = None               # index of plot element which is being dragged
        self.originalLeftX = None           # 
        self.originalSpacing = None         #
        self.rightEdgeCursorOffset = None   #
        self.originalHeight = None          #
    
    def _setEventRegistersRightButton(self):
        """
        Variables which register information about events regarding the right mouse button
        """
        self.rectangleIndexToChange = None
    
    def _updateCanvas(self):
        """
        Redraws the plot on the canvas using the current solver state.
        """
        self.drawer.draw(self.plotMetada,self.plotSolver) 
    
    def _updateDataView(self):
        """
        Updates the data viewer to display current plot values.
        
        Highlights the data element currently being edited if any.
        """
        self.dataViewer.write(self.plotMetada, self.plotSolver, self.dragIndex, self.dragEdge) # type: ignore
    
    def _changeTitle(self):
        """
        Plot title change using UI
        """
        newTitle = simpledialog.askstring("Enter new title","New title: ")
        if newTitle is None:
            return
        else:
            self.plotSolver.ChangeTitle(newTitle)
            self._updateCanvas()

    
    def on_left_down(self, event: tk.Event)->None:
        """
        Handles left mouse button press events.
        
        Determines which plot element was clicked and registers the drag operation.
        
        Args:
            event: The tkinter Event object containing mouse coordinates and button information.
        """
        raise NotImplementedError("Method CanvasHandler.on_left_down must be declared in subclass")
    
    def on_right_down(self, event: tk.Event)->None:
        """
        Handles right mouse button press events.
        
        Displays the default context menu at the cursor position.
        
        Args:
            event: The tkinter Event object containing mouse coordinates.
        """
        self.defaultMenu.post(event.x_root,event.y_root)

    def on_mouse_move(self,event: tk.Event)->None:
        """
        Handles mouse motion events while dragging.
        
        Updates the plot element being dragged based on mouse position.
        Updates canvas and data display after each movement.
        
        Args:
            event: The tkinter Event object containing current mouse coordinates.
        """
        raise NotImplementedError("Method CanvasHandler.on_mouse_move must be declared in subclass")
    
    def on_left_up(self,event: tk.Event)->None:
        """
        Handles left mouse button release events.
        
        Ends the drag operation and clears all drag-related state variables.
        
        Args:
            event: The tkinter Event object containing mouse coordinates.
        """
        raise NotImplementedError("Method CanvasHandler.on_left_up must be declared in subclass")
    
    def on_right_up(self,event: tk.Event)->None:
        """
        Handles right mouse button release events.
        
        Args:
            event: The tkinter Event object containing mouse coordinates.
        """
        raise NotImplementedError("Method CanvasHandler.on_right_up must be declared in subclass")
    
    def check_cursor(self, event: tk.Event)->None:
        """
        Updates cursor appearance based on mouse position over plot elements.
        
        Changes the cursor to indicate what action is possible at the current location
        (e.g., resize, drag, cross for point selection).
        
        Args:
            event: The tkinter Event object containing current mouse coordinates.
        """
        raise NotImplementedError("Method CanvasHandler.check_cursor must be declared in subclass")
    
    def inicializeDataView(self, textWindow: tk.Text)->None:
        """
        Initializes the data viewer component with a text window.
        
        Creates the appropriate DataViewer implementation for this plot type.
        
        Args:
            textWindow: A tkinter Text widget where plot data will be displayed.
        """
        raise NotImplementedError("Method CanvasHandler.inicializeDataView must be declared in subclass")
    
    def inicializeCanvas(self, canvas: tk.Canvas, width:int, height: int)->None:
        """
        Initializes the canvas drawer with the plot canvas and dimensions.
        
        Creates the appropriate CanvasDrawer implementation for this plot type.
        
        Args:
            canvas: The tkinter Canvas widget for drawing.
            width: Width of the canvas in pixels.
            height: Height of the canvas in pixels.
        """
        raise NotImplementedError("Method CanvasHandler.inicializeCanvas must be declared in subclass")
    
    def inicializeDefaultRightClickMenu(self, menu: tk.Menu)->None:
        """
        Initializes the default right-click context menu.
        
        Sets up the menu that appears when right-clicking on empty canvas area.
        
        Args:
            menu: The tkinter Menu widget to use as the default context menu.
        """
        self.defaultMenu = menu
        self.defaultMenu.add_command(label = "Change title", command=self._changeTitle)
    
    def inicializeRightClickMenu(self, menu: tk.Menu)->None:
        """
        Initializes the element-specific right-click context menu.
        
        Sets up the menu that appears when right-clicking on a plot element.
        Subclasses should add menu items specific to their plot type.
        
        Args:
            menu: The tkinter Menu widget to use as the element context menu.
        """
        raise NotImplementedError("Method CanvasHandler.inicializeRightClickMenu must be declared in subclass")