from abc import ABC, abstractmethod
from .plotmetadata import PlotMetadata
import tkinter as tk
from kiwiplots.chartelements import ValuePoint2D
from tkinter import simpledialog
from .canvasdrawers import CanvasDrawer
from .dataviewers import DataViewer
from kiwiplots.solvers import ChartSolver


class EventRegisters(ABC):
    def reset(self)->None:
        raise NotImplementedError("Method EventRegisters.reset must be declared in subclass")


class EventHandler(ABC):
    """
    Abstract class for handling user interactions with the plot on a tkinter Canvas.
    
    Manages mouse events, cursor changes, and updates to the plot data and visualization.
    Implementations are specific to the type of plot being displayed.
    """
    class EventRegistersLeftButton(EventRegisters):
        def __init__(self):
            self.reset()

        def reset(self)-> None:
            self.eventType = None                # which edge is being dragged                 
            self.dragStart = ValuePoint2D(0,0)   # where draging started
            self.dragIndex : int = None          # index of plot element which is being dragged #type: ignore
            self.originalLeftX : float = None           #                        #type: ignore
            self.originalSpacing : float = None         #                           #type: ignore
            self.originalHeight : float = None          #               #type: ignore
    
    class EventRegistersRightButton(EventRegisters):
        def __init__(self) -> None:
            self.reset()
        
        def reset(self)->None:
            self.indexToChange : int = None #type: ignore

    def __init__(self, plotMetadata: PlotMetadata) -> None:
        """
        Initializes the CanvasHandler with plot metadata.
        After initialization CanvasHandler should be provided with tkinter widgets.

        Args:
            plotMetadata: Metadata about the plot including scale factor and axis values.
        """
        self.canvas : tk.Canvas | None = None    
        self.defaultMenu : tk.Menu | None = None       
        self.elementMenu : tk.Menu | None = None         
        self.drawer : CanvasDrawer | None = None   
        self.dataViewer : DataViewer | None= None     
        self.plotSolver : ChartSolver | None= None 
        self.plotMetadata = plotMetadata                        
        self.eventRegistersLeft : EventHandler.EventRegistersLeftButton = None # pyright: ignore[reportAttributeAccessIssue]
        self.eventRegistersRight : EventHandler.EventRegistersRightButton = None  # pyright: ignore[reportAttributeAccessIssue]
    
    def UpdateUI(self):
        """
        Updates both the canvas drawing and the data viewer display.
        
        Refreshes the visualization to reflect any changes in the plot data.
        """
        self._updateCanvas()
        self._updateDataView()
    
    @abstractmethod
    def _isEventTypeValueChange(self)->bool:
        return False
    
    
    def _updateCanvas(self):
        """
        Redraws the plot on the canvas using the current solver state.
        """
        assert self.plotSolver is not None
        assert self.drawer is not None
        self.drawer.draw(self.plotMetadata,self.plotSolver) 
    

    def _updateDataView(self):
        """
        Updates the data viewer to display current plot values.
        
        Highlights the data element currently being edited if any.
        """
        assert self.plotSolver is not None
        assert self.dataViewer is not None
        self.dataViewer.Write(self.plotMetadata, self.plotSolver, self.eventRegistersLeft.dragIndex, self._isEventTypeValueChange())
    
    def _changeTitle(self):
        """
        Plot title change using UI
        """
        newTitle = simpledialog.askstring("Enter new title","New title: ")
        if newTitle is None:
            return
        else:
            self.plotMetadata.title = newTitle
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
        assert self.defaultMenu is not None
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
    
    def initializeDataView(self, textWindow: tk.Text)->None:
        """
        Initializes the data viewer component with a text window.
        
        Creates the appropriate DataViewer implementation for this plot type.
        
        Args:
            textWindow: A tkinter Text widget where plot data will be displayed.
        """
        raise NotImplementedError("Method CanvasHandler.inicializeDataView must be declared in subclass")
    
    def initializeCanvas(self, canvas: tk.Canvas, width:int, height: int)->None:
        """
        Initializes the canvas drawer with the plot canvas and dimensions.
        
        Creates the appropriate CanvasDrawer implementation for this plot type.
        
        Args:
            canvas: The tkinter Canvas widget for drawing.
            width: Width of the canvas in pixels.
            height: Height of the canvas in pixels.
        """
        raise NotImplementedError("Method CanvasHandler.inicializeCanvas must be declared in subclass")
    
    def initializeDefaultRightClickMenu(self, menu: tk.Menu)->None:
        """
        Initializes the default right-click context menu.
        
        Sets up the menu that appears when right-clicking on empty canvas area.
        
        Args:
            menu: The tkinter Menu widget to use as the default context menu.
        """
        self.defaultMenu = menu
        self.defaultMenu.add_command(label = "Change title", command=self._changeTitle)
    
    def initializeRightClickMenu(self, menu: tk.Menu)->None:
        """
        Initializes the element-specific right-click context menu.
        
        Sets up the menu that appears when right-clicking on a plot element.
        Subclasses should add menu items specific to their plot type.
        
        Args:
            menu: The tkinter Menu widget to use as the element context menu.
        """
        raise NotImplementedError("Method CanvasHandler.inicializeRightClickMenu must be declared in subclass")