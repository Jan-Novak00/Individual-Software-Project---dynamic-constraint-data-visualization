from kiwiplots import *
import tkinter as tk
from .gameevaluator import GameEvaluator
from .gameeventhandler import EventHandlerProtocol
from .game_dataviewer import GameDataViewer


class GameUI:
    def __init__(self, gameEventHandler : EventHandlerProtocol, instructionString: str, evaluator: GameEvaluator, userSolver : ChartSolver, solutionSolver : ChartSolver, plotMetadata : PlotMetadata, plotWidth: int, plotHeight: int):
        self.eventHandler = gameEventHandler
        self.plotWidth = plotWidth
        self.plotHeight = plotHeight
        self.instructionsForPlayer : str = instructionString
        self.evaluator: GameEvaluator = evaluator
        self.userSolver : ChartSolver = userSolver
        self.solutionSolver : ChartSolver = solutionSolver
        self.plotMetadata : PlotMetadata = plotMetadata

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
        self.instructionWindow = tk.Text(leftFrame, wrap="word", font=("Arial",12), width=40, height=10)
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
        self.eventHandler.initializeCanvas(self.canvas, self.plotWidth, self.plotHeight)
        self.eventHandler.initializeDataView(self.dataWindow)
        self.eventHandler.initializeDefaultRightClickMenu(self.defaultMenu)
        self.eventHandler.initializeRightClickMenu(self.elementMenu)
    

    def _canvasBind(self):
        self.canvas.bind("<Button-1>", self.eventHandler.on_left_down) # type: ignore
        self.canvas.bind("<B1-Motion>", self.eventHandler.on_mouse_move) # type: ignore
        self.canvas.bind("<ButtonRelease-1>", self.eventHandler.on_left_up) # type: ignore
        self.canvas.bind("<Motion>", self.eventHandler.check_cursor) # type: ignore
        self.canvas.bind("<Button-3>", self.eventHandler.on_right_down) # type: ignore
        self.canvas.bind("<ButtonRelease-3>", self.eventHandler.on_right_up) # type: ignore


    def _UIRun(self):
        """
        Binds all mouse and motion events to their respective handlers.
        
        Starts the main tkinter event loop.
        """
        self._canvasBind()
        self.root.mainloop()

    
    def Play(self):
        print("checkpoint 1")
        self.initializeUIElements()
        print("checkpoint 2")
        self.inicializeHandlers()
        print("checkpoint 3")
        self.eventHandler.UpdateUI()
        print("ui updtated")
        self._UIRun()
    

    def _evaluatePrediction_ButtonPressed(self):
        self.eventHandler.Pause()
        self.eventHandler.DisplayOther(self.solutionSolver)
        score = self.evaluator.Eval(self.userSolver, self.solutionSolver, self.plotMetadata)
        self.scoreCounter.set(f"{score}/10000")
        self.eventHandler.WriteSolution(self.userSolver, self.solutionSolver, self.plotMetadata)
        self.evalButton.config(state="disabled")
        