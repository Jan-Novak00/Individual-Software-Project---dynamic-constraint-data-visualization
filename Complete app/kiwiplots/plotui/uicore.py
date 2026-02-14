from typing import Union
import tkinter as tk
from tkinter import simpledialog
from kiwiplots.solvers import ChartSolver
from .plotmetadata import PlotMetadata
from .eventhandlers import EventHandler
from .picturedrawers import PictureDrawer
from .datawriters import DataWriter
import os
"""
Handles communication between UI features.
"""
class UICore:
    """

    Handles communication between UI features.
    
    """
    def __init__(self, plotMetadata: PlotMetadata, solver : ChartSolver, canvasHandler : EventHandler, pictureDrawer : PictureDrawer, dataWriter: DataWriter, plotWidth: int, plotHeight: int):
        """
        Initializes UICore with all required components.
        
        Args:
            plotMetadata: Metadata about the plot dimensions and scale.
            solver: The solver containing the plot data.
            canvasHandler: Handler for canvas events and interactions.
            pictureDrawer: Component for saving plots as images.
            dataWriter: Component for exporting plot data.
            plotWidth: Width of the plot canvas in pixels.
            plotHeight: Height of the plot canvas in pixels.
        """
        self.solver : ChartSolver = solver
        self.canvasHandler : EventHandler = canvasHandler
        self.pictureDrawer : PictureDrawer = pictureDrawer
        self.dataWriter : DataWriter = dataWriter
        self.plotWidth = plotWidth
        self.plotHeight = plotHeight
        self.picturePathBuffer : Union[str,None] = None
        self.dataPathBuffer : Union[str,None] = None
        self.plotMetadata : PlotMetadata = plotMetadata 


    def inicializeUIElements(self):
        """
        Creates and initializes all UI elements including canvas, buttons, and text windows.
        """
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.canvas = tk.Canvas(self.frame, width=self.plotWidth, height=self.plotHeight, bg="white")
        self.canvas.pack()

        self.savePictureButton = tk.Button(self.frame, text="Save as png", command=self.on_savePictureButton_click)
        self.savePictureButton.pack(pady=5)

        self.dataWindow = tk.Text(self.frame, height=20, width=40)
        self.dataWindow.pack()

        self.saveDataButton = tk.Button(self.frame, text="Save data as csv", command=self.on_saveDataButton_click)
        self.saveDataButton.pack(pady=5)

        self.defaultMenu = tk.Menu(self.frame,tearoff=0)
        self.elementMenu = tk.Menu(self.frame,tearoff=0)

    def inicializeHandlers(self):
        """
        Initializes all event handlers with their respective UI components.
        """
        self.canvasHandler.inicializeCanvas(self.canvas, self.plotWidth, self.plotHeight)
        self.canvasHandler.inicializeDataView(self.dataWindow)
        self.canvasHandler.inicializeDefaultRightClickMenu(self.defaultMenu)
        self.canvasHandler.inicializeRightClickMenu(self.elementMenu)
    
    
    def on_saveDataButton_click(self):
        """
        Handles the 'Save data' button click event.
        
        Prompts the user for a file path and exports the plot data.
        """
        if self.dataPathBuffer == None:
            self.dataPathBuffer = os.path.join(os.getcwd(), self.solver.GetTitle())
        fileName = simpledialog.askstring("Save data", "File name (without extension): ", initialvalue=self.dataPathBuffer)
        if fileName == None:
            return
        else:
            self.dataPathBuffer = fileName

        self.dataWriter.write(self.plotMetadata, self.solver, self.dataPathBuffer + ".csv") # type: ignore    
    
    def on_savePictureButton_click(self):
        """
        Handles the 'Save as PNG' button click event.
        
        Prompts the user for a file path and saves the plot as a PNG image.
        """
        self.canvasHandler.UpdateUI()
        if self.picturePathBuffer == None:
            self.picturePathBuffer = os.path.join(os.getcwd(), self.solver.GetTitle())  
        
        pictureName = simpledialog.askstring("Save plot", "Image name (without extension): ", initialvalue=self.picturePathBuffer)

        if pictureName == None:
            return
        else:
            self.picturePathBuffer = pictureName 

        print("Saving canvas to", pictureName + ".png")
        self.pictureDrawer.draw(self.plotMetadata, self.solver, self.plotWidth, self.plotHeight)
    
    def View(self):
        """
        Initializes and displays the main UI window.
        
        Sets up all UI elements, handlers, and starts the event loop.
        """
        self.inicializeUIElements()
        self.inicializeHandlers()

        self.canvasHandler.UpdateUI() #initial draw
        self._UIRun()
    
    def _UIRun(self):
        """
        Binds all mouse and motion events to their respective handlers.
        
        Starts the main tkinter event loop.
        """
        self.canvas.bind("<Button-1>", self.canvasHandler.on_left_down) # type: ignore
        self.canvas.bind("<B1-Motion>", self.canvasHandler.on_mouse_move) # type: ignore
        self.canvas.bind("<ButtonRelease-1>", self.canvasHandler.on_left_up) # type: ignore
        self.canvas.bind("<Motion>", self.canvasHandler.check_cursor) # type: ignore
        self.canvas.bind("<Button-3>", self.canvasHandler.on_right_down) # type: ignore
        self.canvas.bind("<ButtonRelease-3>", self.canvasHandler.on_right_up) # type: ignore
        self.root.mainloop()
