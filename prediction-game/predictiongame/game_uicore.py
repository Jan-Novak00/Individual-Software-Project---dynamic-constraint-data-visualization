from kiwiplots import *
import tkinter as tk

class GameUI:
    def __init__(self, gameEventHandler, instructionString: str, plotWidth: int, plotHeight: int):
        self.eventHandler = gameEventHandler
        self.plotWidth = plotWidth
        self.plotHeight = plotHeight
        self.instructionsForPlayer : str = instructionString

    def initializeUIElements(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.scoreCounter = tk.StringVar(value="-")

        self.canvas = tk.Canvas(self.frame, width=self.plotWidth, height=self.plotHeight, bg="white")
        self.canvas.pack()

        self.scoreFrame = tk.Frame(self.root)
        self.scoreFrame.pack(pady=20,padx=20)
        tk.Label(self.scoreFrame, text="Score:", font=("Arial", 20)).pack(side="left")
        tk.Label(self.scoreFrame, textvariable=self.scoreCounter, font=("Arial", 40, "bold"), bg="black", fg="lime", bd=5, relief="ridge").pack(side="left", padx=(10,0))

        self.buttonFrame = tk.Frame(self.frame)
        self.buttonFrame.pack(pady=5)

        self.evalButton = tk.Button(self.buttonFrame, text="Evaluate your prediction", command=lambda : print("TODO"))
        self.evalButton.pack()

        self.infoFrame = tk.Frame(self.root)
        self.infoFrame.pack(pady=5)

        self.instructionWindow = tk.Text(self.infoFrame, wrap="none", font=("Arial",12), width=250, height=250)
        self.instructionWindow.pack(padx=20, pady=20)
        self.instructionWindow.insert("1.0",self.instructionsForPlayer)


        #todo inicializace dataview a instrukci
    
    def Play(self):
        self.initializeUIElements()
        self.root.mainloop()