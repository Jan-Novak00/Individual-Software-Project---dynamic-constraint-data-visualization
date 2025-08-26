import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from barPlots import *
import csv

class MenuScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.state("zoomed")
        self.root.title("Data visualisation")
        
        self.mainMenu = tk.Frame(self.root, bg="bisque2")
        self.mainMenu.pack(fill="both",expand=True)

        self._setDataInput()
        self._setPlotTypeMenu()
        self._setPlotDimentionsMenu()
        self._setGenerateButton()

    def View(self):
        self.root.mainloop()
       

    def _setDataInput(self):
        self.dataInputFrame = tk.Frame(self.mainMenu, bg="bisque2")
        self.dataInputFrame.pack()

        labelDataInput = tk.Label(self.dataInputFrame, text="Data input", font=("Arial", 15), bg="bisque2")
        labelDataInput.grid(row=0, column=0, sticky="w")
        self.dataInputField = tk.Text(self.dataInputFrame, height=20, width=50)
        self.dataInputField.grid(row=1, column=0, pady=5)

        self.importButton = tk.Button(self.dataInputFrame, text="Import as CSV", command=self.on_importCSV_click)
        self.importButton.grid(row=2, column=0, pady=5, sticky="w")

    def _setPlotTypeMenu(self):
        self.plotTypeMenu = tk.Frame(self.mainMenu, bg="bisque2")
        self.plotTypeMenu.pack()

        plotTypeLabel = tk.Label(self.plotTypeMenu, text="Plot type", font=("Arial", 15), bg="bisque2")
        plotTypeLabel.pack()
        self.chosenPlotType = tk.StringVar()
        self.chosenPlotType.set("Histogram")
        self.plotMenu = tk.OptionMenu(self.plotTypeMenu, self.chosenPlotType,"Candlestick chart","Bar chart", "Histogram")
        self.plotMenu.pack(pady=20)
        
    def _setPlotDimentionsMenu(self):
        self.plotDimentionsMenu = tk.Frame(self.mainMenu, bg="bisque2")
        self.plotDimentionsMenu.pack()

        def onlyNumber(input: str):
            return input.isdigit() or input == ""
        
        numberValidator = self.plotDimentionsMenu.register(onlyNumber)

        sizeLabel = tk.Label(self.plotDimentionsMenu, text="Plot canvas size", font=("Arial", 15), bg="bisque2")
        sizeLabel.grid(row=0, column=0, sticky="w")
        widthLabel = tk.Label(self.plotDimentionsMenu, text="width", font=("Arial", 11), bg="bisque2")
        widthLabel.grid(row=1, column=0, sticky="w")
        self.widthEntry = tk.Entry(self.plotDimentionsMenu, validate="key", validatecommand=(numberValidator, "%P"))
        self.widthEntry.grid(row=1, column=1, pady=5)
        heightLabel = tk.Label(self.plotDimentionsMenu, text="height", font=("Arial", 11), bg="bisque2")
        heightLabel.grid(row=2, column=0, sticky="w")
        self.heightEntry = tk.Entry(self.plotDimentionsMenu, validate="key", validatecommand=(numberValidator, "%P"))
        self.heightEntry.grid(row=2, column=1, pady=5)
        pass

    def _setGenerateButton(self):
        self.generateButton = tk.Button(self.mainMenu, text="GENERATE", command=self.on_generateButton_click)
        self.generateButton.pack(pady=100)
        pass


    
    def on_importCSV_click(self):
        fileAddress = simpledialog.askstring("Enter address of the file","File path: ")
        if fileAddress is None:
            return
        
        else:
            input : str = ""
            with open(fileAddress, "r") as file:
                for line in file:
                    input += line
            self.dataInputField.delete("1.0", "end")
            self.dataInputField.insert("1.0", input)
    
    def on_generateButton_click(self):
        width = int(self.widthEntry.get())
        height = int(self.heightEntry.get())
        input = self.dataInputField.get("1.0", "end")
        plotType = self.chosenPlotType.get()
        if plotType == "Bar chart":
            self._runBarChart(input, width, height)
        elif plotType == "Histogram":
            self._runHistogram(input, width, height)
        elif plotType == "Candlestick chart":
            self._runCandlestickChart(input, width, height)

    @staticmethod
    def _csvToListOfLists(fileString : str):
        return list(csv.reader(fileString.splitlines()))
    
    @staticmethod
    def _isFloat(string : str):
        try:
            a = float(string)
            return True
        except ValueError:
            return False

    def _validateInput_For_BarChart(self, CSVlistOfLists : list[list[str]]):
        for line in CSVlistOfLists:
            if (len(line) % 2 != 0):
                return False
            for i in range(1,len(line),2):
                if not self._isFloat(line[i]):
                    return False
        return True
    
    def _validateInput_For_Histogram(self, CSVlistOfLists : list[list[str]]):
        lastIntervalBoundary = None
        for line in CSVlistOfLists:
            if len(line) != 3:
                return False
            if not (self._isFloat(line[0]) and self._isFloat(line[1]) and self._isFloat(line[2])):
                return False
            low, high = float(line[0]), float(line[1])
            if lastIntervalBoundary == None:
                lastIntervalBoundary = low
            if lastIntervalBoundary != low or (high <= low):
                return False
            lastIntervalBoundary = high
        return True
    
    def _validateInput_For_CandlestickChart(self, CSVlistOfLists : list[list[str]]):
        for line in CSVlistOfLists:
            if len(line) != 5:
                return False
            if not (self._isFloat(line[1]) and self._isFloat(line[2]) and self._isFloat(line[3] and self._isFloat(line[4]))):
                    return False
            opening, closing, minimum, maximum = float(line[1]), float(line[2]), float(line[3]), float(line[4])
            if (minimum > maximum) or not (minimum <= opening <= maximum) or not (minimum <= closing <= maximum):
                return False
        return True

    def _prepareInput_BarChart(self, inputString : str):
        CSVlist = self._csvToListOfLists(inputString)
        if not self._validateInput_For_BarChart(CSVlist):
            return None        
        names = []
        values = []
        for line in CSVlist:
            newValueGroup = []
            newNameGroup = []
            for i in range(len(line)):
                if i%2 == 0:
                    newNameGroup.append(line[i])
                else:
                    newValueGroup.append(float(line[i]))
            names.append(newNameGroup)
            values.append(newValueGroup)
        return [names, values]
    
    def _prepareInput_Histogram(self, inputString : str):
        CSVlist = self._csvToListOfLists(inputString)
        if not self._validateInput_For_Histogram(CSVlist):
            return None
        values = []
        for line in CSVlist:
            values.append([float(line[0]),float(line[1]),float(line[2])])
        return values

    def _prepareInput_CandlestickChart(self, inputString : str):
        CSVlist = self._csvToListOfLists(inputString)
        if not self._validateInput_For_CandlestickChart(CSVlist):
            return None
        names, openings, closings, minima, maxima = [], [], [], [], []
        for line in CSVlist:
            names.append(line[0])
            openings.append(float(line[1]))
            closings.append(float(line[2]))
            minima.append(float(line[3]))
            maxima.append(float(line[4]))
        return [names, openings, closings, minima, maxima]

    def _runBarChart(self, input : str, width : int, height : int):
        data = self._prepareInput_BarChart(input)
        if data is None:
            messagebox.showerror("Warning","Input text is not in correct format.")
            return
        
        names, values = data[0], data[1]
        barChart = BarChartCanvas(values, 20, 5, 3, width, height, "Title")
        self.root.destroy()
        barChart.View()
    
    def _runHistogram(self, input : str, width : int, height : int):
        data = self._prepareInput_Histogram(input)
        if data is None:
            messagebox.showerror("Warning","Input text is not in correct format.")
            return
        
        histogram = HistogramCanvas(data,20,10,width,height,"Title")
        self.root.destroy()
        histogram.View()

    def _runCandlestickChart(self, input : str, width : int, height : int):
        data = self._prepareInput_CandlestickChart(input)
        if data is None:
            messagebox.showerror("Warning","Input text is not in correct format.")
            return
        names, openings, closings, minima, maxima = data[0], data[1], data[2], data[3], data[4]
        candlestickChart = CandlestickChartCanvas(20, openings, closings, minima, maxima, 5, width, height, 0, "Title")
        self.root.destroy()
        candlestickChart.View()

    





menu = MenuScreen()
menu.View()