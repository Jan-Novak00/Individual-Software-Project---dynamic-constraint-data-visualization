from kiwiplots import *
import tkinter as tk
from .gameevaluator import GameEvaluator
from .gameeventhandler import GameEventHandler


class GameUI:
    def __init__(self, gameEventHandler, instructionString: str, evaluator: GameEvaluator, plotWidth: int, plotHeight: int):
        self.canvasHandler = gameEventHandler
        self.plotWidth = plotWidth
        self.plotHeight = plotHeight
        self.instructionsForPlayer : str = instructionString
        self.evaluator: GameEvaluator = evaluator

    def initializeUIElements(self):
        """
        Creates and initializes all UI elements including canvas, buttons, and text windows.
        """
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.scoreCounter = tk.StringVar(value="-")

        self.canvas = tk.Canvas(self.frame, width=self.plotWidth, height=self.plotHeight, bg="white")
        self.canvas.pack()

        self.scoreFrame = tk.Frame(self.root)
        self.scoreFrame.pack(pady=20,padx=20)
        tk.Label(self.scoreFrame, text="Score:", font=("Arial", 20)).pack(side="left")
        self.scoreDisplay = tk.Label(self.scoreFrame, textvariable=self.scoreCounter, font=("Arial", 40, "bold"), bd=5, bg = "white", relief="ridge", width=13)
        self.scoreDisplay.pack(side="left", padx=(10,0))

        self.buttonFrame = tk.Frame(self.frame)
        self.buttonFrame.pack(pady=5)

        self.evalButton = tk.Button(self.buttonFrame, text="Evaluate your prediction", command=self._evaluatePrediction_ButtonPressed)
        self.evalButton.pack()

        self.infoFrame = tk.Frame(self.root)
        self.infoFrame.pack(pady=5)

        leftFrame = tk.Frame(self.infoFrame)
        leftFrame.pack(side="left", padx=10)

        rightFrame = tk.Frame(self.infoFrame)
        rightFrame.pack(side="left", padx=10)

        tk.Label(leftFrame, text="Instructions:", font=("Arial", 13, "bold")).pack()
        self.instructionWindow = tk.Text(leftFrame, wrap="none", font=("Arial",12), width=40, height=10)
        self.instructionWindow.pack(padx=20, pady=20, side="left")
        self.instructionWindow.insert("1.0",self.instructionsForPlayer)
        self.instructionWindow.config(state="disabled")

        tk.Label(rightFrame, text="Your data:", font=("Arial", 13, "bold")).pack()
        self.dataWindow = tk.Text(rightFrame, wrap="none", font=("Arial",12), width=40, height=20)
        self.dataWindow.pack(padx=20, pady=20, side="left")
        self.dataWindow.config(state="disabled")
      
        self.defaultMenu = tk.Menu(self.frame,tearoff=0)
        self.elementMenu = tk.Menu(self.frame,tearoff=0)
    
    def inicializeHandlers(self):
        """
        Initializes all event handlers with their respective UI components.
        """
        self.canvasHandler.initializeCanvas(self.canvas, self.plotWidth, self.plotHeight)
        self.canvasHandler.initializeDataView(self.dataWindow)
        self.canvasHandler.initializeDefaultRightClickMenu(self.defaultMenu)
        self.canvasHandler.initializeRightClickMenu(self.elementMenu)

    
    def Play(self):
        self.initializeUIElements()
        self.inicializeHandlers()
        self.root.mainloop()
    

    def _evaluatePrediction_ButtonPressed(self):
        print("TODO")
        self.scoreCounter.set("9990/10000")
        pass