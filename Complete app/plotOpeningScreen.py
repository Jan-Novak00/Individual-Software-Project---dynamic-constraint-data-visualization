import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from kiwiplots import *
import csv
import kiwisolver


class MenuScreen:
    """
    A GUI application for data visualization using tkinter.

    This class creates a main menu screen where users can input data, select plot types,
    configure plot dimensions and axis labels, and generate various types of charts
    including bar charts, histograms, line charts and candlestick charts.
    """
    def __init__(self):
        """
        Initialize the MenuScreen GUI application.

        Sets up the main tkinter window, creates the main menu frame, and initializes
        all UI components including data input, plot type selection, dimensions,
        axis labels, and the generate button.
        """
        self.root = tk.Tk()
        self.root.state("zoomed") # ToDo: zoomed is for Windows only :(
        self.root.title("Data visualisation")
        
        self.mainMenu = tk.Frame(self.root, bg="bisque2")
        self.mainMenu.pack(fill="both",expand=True)
        self.xAxisValueEntry = None

        self._setDataInput()
        self._setPlotTypeMenu()

        self.dimentionsAndLabelsFrame = tk.Frame(self.mainMenu, bg="bisque2")
        self.dimentionsAndLabelsFrame.pack()

        self._setPlotDimentionsMenu()
        self._setAxisLabelsMenu()
        self.chosenPlotType.trace_add("write", self._updateCandlestickEntry)
        self._setGenerateButton()

    def View(self):
        """
        Start the tkinter event loop to display the GUI of the menu screen.
        """
        self.root.mainloop()
    
    def _updateCandlestickEntry(self, *args): # ToDo test please
        """
        Update the UI to show or hide the X axis value entry based on plot type selection.
        """
        if hasattr(self, "xAxisValueFrame") and self.xAxisValueFrame is not None:
            self.xAxisValueFrame.destroy()
            self.xAxisValueFrame = None

        if self.chosenPlotType.get() == "Candlestick chart" or "Line chart":

            self.xAxisValueFrame = tk.Frame(self.mainMenu, bg="bisque2")
            self.xAxisValueFrame.pack(pady=5, before=self.generateButton)

            xLabel = tk.Label(self.xAxisValueFrame, text="X axis value:", font=("Arial", 11), bg="bisque2")
            xLabel.pack(side="left")


            def onlyNumber(input: str):
                return input.isdigit() or input == ""
            validator = self.mainMenu.register(onlyNumber)

            self.xAxisValueEntry = tk.Entry(self.xAxisValueFrame, validate="key", validatecommand=(validator, "%P"))
            self.xAxisValueEntry.insert(0, "0")
            self.xAxisValueEntry.pack(side="left")


    def _setDataInput(self):
        """
        Set up the data input section of the GUI.

        Creates a frame with a text area for manual data entry and an import button
        for loading CSV files.
        """
        self.dataInputFrame = tk.Frame(self.mainMenu, bg="bisque2")
        self.dataInputFrame.pack()

        labelDataInput = tk.Label(self.dataInputFrame, text="Data input", font=("Arial", 15), bg="bisque2")
        labelDataInput.grid(row=0, column=0, sticky="w")
        self.dataInputField = tk.Text(self.dataInputFrame, height=20, width=50)
        self.dataInputField.grid(row=1, column=0, pady=5)

        self.importButton = tk.Button(self.dataInputFrame, text="Import as CSV", command=self.on_importCSV_click)
        self.importButton.grid(row=2, column=0, pady=5, sticky="w")

    def _setPlotTypeMenu(self):
        """
        Set up the plot type selection menu.
        """
        self.plotTypeMenu = tk.Frame(self.mainMenu, bg="bisque2")
        self.plotTypeMenu.pack()

        plotTypeLabel = tk.Label(self.plotTypeMenu, text="Plot type", font=("Arial", 15), bg="bisque2")
        plotTypeLabel.pack()
        self.chosenPlotType = tk.StringVar()
        self.chosenPlotType.set("Histogram")
        self.plotMenu = tk.OptionMenu(self.plotTypeMenu, self.chosenPlotType,"Candlestick chart","Bar chart", "Histogram", "Line chart")
        self.plotMenu.pack(pady=20)
        
    def _setPlotDimentionsMenu(self):
        """
        Set up the plot dimensions configuration menu.

        Creates input fields for specifying the width and height of the plot canvas.
        Includes validation to ensure only numeric input is accepted.
        Defaults to 1000x500 pixels.
        """
        self.plotDimentionsMenu = tk.Frame(self.dimentionsAndLabelsFrame, bg="bisque2")
        self.plotDimentionsMenu.pack(side="left", padx=20)

        def onlyNumber(input: str):
            return input.isdigit() or input == ""
        
        numberValidator = self.plotDimentionsMenu.register(onlyNumber)

        sizeLabel = tk.Label(self.plotDimentionsMenu, text="Plot canvas size", font=("Arial", 15), bg="bisque2")
        sizeLabel.grid(row=0, column=0, sticky="w")
        widthLabel = tk.Label(self.plotDimentionsMenu, text="width", font=("Arial", 11), bg="bisque2")
        widthLabel.grid(row=1, column=0, sticky="w")
        self.widthEntry = tk.Entry(self.plotDimentionsMenu, validate="key", validatecommand=(numberValidator, "%P"))
        self.widthEntry.insert(0,"1000")
        self.widthEntry.grid(row=1, column=1, pady=5)
        heightLabel = tk.Label(self.plotDimentionsMenu, text="height", font=("Arial", 11), bg="bisque2")
        heightLabel.grid(row=2, column=0, sticky="w")
        self.heightEntry = tk.Entry(self.plotDimentionsMenu, validate="key", validatecommand=(numberValidator, "%P"))
        self.heightEntry.insert(0,"500")
        self.heightEntry.grid(row=2, column=1, pady=5)

    def _setAxisLabelsMenu(self):
        """
        Set up the axis labels configuration menu.

        Creates input fields for specifying custom labels for the X and Y axes
        of the plot.
        """
        self.axisLabelsMenu = tk.Frame(self.dimentionsAndLabelsFrame, bg="bisque2")
        self.axisLabelsMenu.pack(side="left", padx=20)

        axisLabel = tk.Label(self.axisLabelsMenu, text="Axis labels", font=("Arial", 15), bg="bisque2")
        axisLabel.grid(row=0, column=0, sticky="w")

        xLabel = tk.Label(self.axisLabelsMenu, text="x label", font=("Arial", 11), bg="bisque2")
        xLabel.grid(row=1, column=0, sticky="w")
        self.xAxisEntry = tk.Entry(self.axisLabelsMenu)
        self.xAxisEntry.grid(row=1, column=1, pady=5)

        yLabel = tk.Label(self.axisLabelsMenu, text="y label", font=("Arial", 11), bg="bisque2")
        yLabel.grid(row=2, column=0, sticky="w")
        self.yAxisEntry = tk.Entry(self.axisLabelsMenu)
        self.yAxisEntry.grid(row=2, column=1, pady=5)



    def _setGenerateButton(self):
        """
        Set up the generate button.

        Creates a button that triggers the plot generation process when clicked,
        calling the on_generateButton_click method.
        """
        self.generateButton = tk.Button(self.mainMenu, text="GENERATE", command=self.on_generateButton_click)
        self.generateButton.pack(pady=100)


    
    def on_importCSV_click(self):
        """
        Handle the CSV import button click event.

        Opens a dialog for the user to enter a file path, reads the CSV file,
        and populates the data input text field with its contents.
        """
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
    
    def on_generateButton_click(self): # ToDo
        """
        Handle the generate button click event.

        Retrieves all user inputs (dimensions, data, plot type, labels), validates
        the data format, and launches the appropriate plot based on the selected type.
        Destroys the current window and opens the plot visualization.
        """
        print("Line chart checkpoint 3")
        width = int(self.widthEntry.get())
        height = int(self.heightEntry.get())
        input = self.dataInputField.get("1.0", "end")
        plotType = self.chosenPlotType.get()
        print("plotType = "+"\""+plotType+"\"")
        xLabel = self.xAxisEntry.get()
        yLabel = self.yAxisEntry.get()
        if plotType == "Bar chart":
            self._runBarChart(input, width, height, xLabel, yLabel)
        elif plotType == "Histogram":
            self._runHistogram(input, width, height, xLabel, yLabel)
        elif plotType == "Candlestick chart":
            self._runCandlestickChart(input, width, height, xLabel, yLabel)
        elif plotType == "Line chart":
            print("Line chart checkpoint 2")
            self._runLineChart(input, width, height, xLabel, yLabel)

    @staticmethod
    def _csvToListOfLists(fileString : str):
        """
        Convert a CSV string to a list of lists.

        Parses the input string as CSV data and returns it as a list where each
        element is a list representing a row of the CSV.

        Args:
            fileString (str): The CSV data as a string.

        Returns:
            list[list[str]]: A list of lists containing the CSV data.
        """
        return list(csv.reader(fileString.splitlines()))
    
    @staticmethod
    def _isFloat(string : str):
        """
        Check if a string can be converted to a float.

        Attempts to convert the string to a float and returns True if successful,
        False otherwise.

        Args:
            string (str): The string to check.

        Returns:
            bool: True if the string is a valid float, False otherwise.
        """
        try:
            a = float(string)
            return True
        except ValueError:
            return False

    def _validateInput_For_BarChart(self, CSVlistOfLists : list[list[str]]):
        """
        Validate CSV data for bar chart format.

        Checks that each row has an even number of columns (alternating names and values)
        and that all value columns contain valid floats.

        Args:
            CSVlistOfLists (list[list[str]]): The CSV data as a list of lists.

        Returns:
            bool: True if the data is valid for a bar chart, False otherwise.
        """
        for line in CSVlistOfLists:
            if (len(line) % 2 != 0):
                return False
            for i in range(1,len(line),2):
                if not self._isFloat(line[i]):
                    return False
        return True
    
    def _validateInput_For_Histogram(self, CSVlistOfLists : list[list[str]]):
        """
        Validate CSV data for histogram format.

        Checks that each row has exactly 3 columns (low, high, value), all are floats,
        intervals are contiguous (each low equals previous high), and high > low.

        Args:
            CSVlistOfLists (list[list[str]]): The CSV data as a list of lists.

        Returns:
            bool: True if the data is valid for a histogram, False otherwise.
        """
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
        """
        Validate CSV data for candlestick chart format.

        Checks that each row has exactly 5 columns (name, open, close, min, max),
        all numeric columns are floats, min <= max, and open/close are within min-max range.

        Args:
            CSVlistOfLists (list[list[str]]): The CSV data as a list of lists.

        Returns:
            bool: True if the data is valid for a candlestick chart, False otherwise.
        """
        for line in CSVlistOfLists:
            if len(line) != 5:
                return False
            # TODO following line is weird
            if not (self._isFloat(line[1]) and self._isFloat(line[2]) and self._isFloat(line[3] and self._isFloat(line[4]))): # pyright: ignore[reportArgumentType]
                    return False
            opening, closing, minimum, maximum = float(line[1]), float(line[2]), float(line[3]), float(line[4])
            if (minimum > maximum) or not (minimum <= opening <= maximum) or not (minimum <= closing <= maximum):
                return False
        return True
    
    def _validateInput_For_LineChart(self, CSVlistOfLists : list[list[str]]):
        for line in CSVlistOfLists:
            if len(line) != 2:
                return False
            if not (self._isFloat(line[1])):
                return False
        return True
            

    def _prepareInput_BarChart(self, inputString : str):
        """
        Prepare and validate input data for bar chart generation.

        Converts CSV string to list format, validates it, and organizes data
        into names and values lists for bar chart creation.

        Args:
            inputString (str): The CSV data as a string.

        Returns:
            list or None: [names, values] where names and values are lists of lists,
                         or None if validation fails.
        """
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
        """
        Prepare and validate input data for histogram generation.

        Converts CSV string to list format, validates it, and organizes data
        into values and intervals for histogram creation.

        Args:
            inputString (str): The CSV data as a string.

        Returns:
            list or None: [values, intervals] where values is a list of floats
                         and intervals is a list of (low, high) tuples, or None if validation fails.
        """
        CSVlist = self._csvToListOfLists(inputString)
        if not self._validateInput_For_Histogram(CSVlist):
            return None
        intervals = []
        values = []
        for line in CSVlist:
            intervals.append((float(line[0]),float(line[1])))
            values.append(float(line[2]))
        return [values, intervals]

    def _prepareInput_CandlestickChart(self, inputString : str):
        """
        Prepare and validate input data for candlestick chart generation.

        Converts CSV string to list format, validates it, and organizes data
        into separate lists for names, openings, closings, minima, and maxima.

        Args:
            inputString (str): The CSV data as a string.

        Returns:
            list or None: [names, openings, closings, minima, maxima] as lists,
                         or None if validation fails.
        """
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
    
    def _prepareInput_LineChart(self, inputString : str):
        CSVlist = self._csvToListOfLists(inputString)
        if not self._validateInput_For_LineChart(CSVlist):
            return None
        names, values = [], []
        for line in CSVlist:
            names.append(line[0])
            values.append(float(line[1]))
        return [names,values]
        

    def _runBarChart(self, input : str, width : int, height : int, xLabel : str, yLabel : str):
        """
        Generate and display a bar chart.

        Prepares the input data, validates it, and if valid, destroys the current
        window and opens a new bar chart visualization using UIFactory.

        Args:
            input (str): The CSV data as a string.
            width (int): The width of the plot canvas.
            height (int): The height of the plot canvas.
            xLabel (str): The label for the X axis.
            yLabel (str): The label for the Y axis.
        """
        data = self._prepareInput_BarChart(input)
        if data is None:
            messagebox.showerror("Warning","Input text is not in correct format.")
            return
        names, values = data[0], data[1]
        self.root.destroy()
        UIFactory.CreateBarChart("Title (ToDo)",xLabel,yLabel,values,names,width,height).View()
    
    def _runHistogram(self, input : str, width : int, height : int, xLabel : str, yLabel : str):
        """
        Generate and display a histogram.

        Prepares the input data, validates it, and if valid, destroys the current
        window and opens a new histogram visualization using UIFactory.

        Args:
            input (str): The CSV data as a string.
            width (int): The width of the plot canvas.
            height (int): The height of the plot canvas.
            xLabel (str): The label for the X axis.
            yLabel (str): The label for the Y axis.
        """
        data = self._prepareInput_Histogram(input)
        if data is None:
            messagebox.showerror("Warning","Input text is not in correct format.")
            return
        
        self.root.destroy()
        UIFactory.CreateHistogram("Title (ToDo)",xLabel,yLabel,data[0],data[1],width,height).View()
        

    def _runCandlestickChart(self, input : str, width : int, height : int, xLabel : str, yLabel : str):
        """
        Generate and display a candlestick chart.

        Prepares the input data, validates it, and if valid, destroys the current
        window and opens a new candlestick chart visualization using UIFactory.
        Includes the X axis value from the additional input field.

        Args:
            input (str): The CSV data as a string.
            width (int): The width of the plot canvas.
            height (int): The height of the plot canvas.
            xLabel (str): The label for the X axis.
            yLabel (str): The label for the Y axis.
        """
        data = self._prepareInput_CandlestickChart(input)
        if data is None:
            messagebox.showerror("Warning","Input text is not in correct format.")
            return
        names, openings, closings, minima, maxima = data[0], data[1], data[2], data[3], data[4]
        xAxisValue = float(self.xAxisValueEntry.get()) # pyright: ignore[reportOptionalMemberAccess]
        self.root.destroy()
        UIFactory.CreateCandlesticChart("Title (ToDo)",xLabel,yLabel,xAxisValue,openings,closings,minima,maxima,names,width,height).View()
    
    def _runLineChart(self, input : str, width : int, height : int, xLabel : str, yLabel : str):
        print("Line chart checkpoint 1")
        data = self._prepareInput_LineChart(input)
        if data is None:
            messagebox.showerror("Warning","Input text is not in correct format.")
            return
        names, values = data[0], data[1]
        xAxisValue = float(self.xAxisValueEntry.get()) # pyright: ignore[reportOptionalMemberAccess]
        self.root.destroy()
        UIFactory.CreateLineChart("Title (ToDo)", xLabel,yLabel,xAxisValue,values,names,width,height).View()
        pass
    

if __name__ == "__main__":
    print(kiwisolver.__version__)
    menu = MenuScreen()
    menu.View()