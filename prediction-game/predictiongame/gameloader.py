from kiwiplots import *
from abc import ABC
from .defaultevaluators import *
import tomllib
from typing import Any, Type, Optional, get_args, get_origin
import importlib
import importlib.util
import sys
from pathlib import Path
from .gamemodes import GameModes
from .gameevaluator import GameEvaluator
from dataclasses import dataclass
from .utils import *

INITIAL_WIDTH : int   = 100
INITIAL_SPACING : int = 15
INITIAL_INNER_SPACING = 10
INITIAL_ORIGIN_X : int = 50
INITIAL_ORIGIN_Y : int = 30
INITIAL_PADDING : int = 10
DEFAULT_COLOR : Union[str,int] = "blue"
INITIAL_PADDING : int = 10

GENERAL_CONFIG_SECTION_HEADER           = "game_config"
BARCHART_DATA_CONFIG_SECTION_HEADER     = "bar_chart"
HISTOGRAM_DATA_CONFIG_SECTION_HEADER    = "histogram"
CANDLESTICK_DATA_CONFIG_SECTION_HEADER  = "candlestick_chart"
LINECHART_DATA_CONFIG_SECTION_HEADER    = "line_chart"
ORIGIN_HEADER                           = "origin"

X_AXIS_LABEL_KEY = "x_axis_label"
Y_AXIS_LABEL_KEY = "y_axis_label"
TITLE_KEY        = "title"
EVALUATOR_KEY    = "evaluator"
INSTRUCTIONS_KEY = "instructions"
WIDTH_KEY        = "plot_width"
HEIGHT_KEY       = "plot_height"
ORIGIN_X_KEY     = "x"
ORIGIN_Y_KEY     = "y"
X_AXIS_VALUE_KEY     = "x_axis_value"

IS_GUESS_KEY = "is_guess"
NAMES_KEY    = "names"

class LoadFailedException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class DataConfigSectionMissingException(LoadFailedException):
    def __init__(self):
        super().__init__(f"Data config section missing. Possible names: {BARCHART_DATA_CONFIG_SECTION_HEADER}, {CANDLESTICK_DATA_CONFIG_SECTION_HEADER}, {HISTOGRAM_DATA_CONFIG_SECTION_HEADER}, {LINECHART_DATA_CONFIG_SECTION_HEADER}")

class InvalidGeneralConfigException(LoadFailedException):
    def __init__(self, missingItem: str):
        super().__init__(f"Item {missingItem} is missing in the config file in section {GENERAL_CONFIG_SECTION_HEADER}")

class InvalidEvaluatorException(LoadFailedException):
    def __init__(self, source: str):
        super().__init__(f"Evaluator class provided in {source} is not valid. Make sure it inherits from GameEvaluator class.")

class EvaluatorLoadFailedException(LoadFailedException):
    def __init__(self):
        super().__init__("Fatal error occured when loading game evaluator.")

class InvalidDataConfigSectionException(LoadFailedException):
    def __init__(self, missingItem: str, dataSectionHeader: str):
        super().__init__(f"Item {missingItem} is missing from {dataSectionHeader}.")

class InvalidDataFormatException(LoadFailedException):
    def __init__(self, message: str, invalidKey: str):
        self.invalidKey = invalidKey
        super().__init__(message)

class GameLoader(ABC):
    """
    Abstract class responsible for loading game data and preparing them for object creation.
    Instance should be acquired using GameLoader.GetLoader static method which will take care of determening type of the chart.
    After load the instnace can be queried for loaded data.
    """
    def __init__(self, data: dict[str,Any]):
        self.evaluatorType : Type[GameEvaluator] = self._getDefaultEvaluatorType()  # pyright: ignore[reportAttributeAccessIssue]
        
        self.xAxisLabel   : str = None # pyright: ignore[reportAttributeAccessIssue]
        self.yAxisLabel   : str = None # pyright: ignore[reportAttributeAccessIssue]
        self.title        : str = None # pyright: ignore[reportAttributeAccessIssue]
        self.instructions : str = None # pyright: ignore[reportAttributeAccessIssue]

        self.userSolver     : ChartSolver  = None # pyright: ignore[reportAttributeAccessIssue]
        self.solutionSolver : ChartSolver  = None # pyright: ignore[reportAttributeAccessIssue]
        self.plotMetadata   : PlotMetadata = None # pyright: ignore[reportAttributeAccessIssue]

        self.originX    : int = None # pyright: ignore[reportAttributeAccessIssue]
        self.originY    : int = None # pyright: ignore[reportAttributeAccessIssue]
        self.plotWidth  : int = None # pyright: ignore[reportAttributeAccessIssue]
        self.plotHeight : int = None # pyright: ignore[reportAttributeAccessIssue]

        self._loadGeneralConfig(data)
        self._loadData(data)
    
  
    @abstractmethod
    def _getDefaultEvaluatorType(self)->Type[GameEvaluator]:
        """
        This method determines type fo the default evaluator for given implementation of GameLoader.

        Returns:
            Type[GameEvaluator]: Type of the default game evaluator.
        """
        pass

    @staticmethod
    def GetLoader(configFilePath: str)->"GameLoader":
        """
        Loads game config.

        Returns:
            GameLoader instance for querying.
        """
        data = GameLoader._loadConfig(configFilePath=configFilePath)
        if BARCHART_DATA_CONFIG_SECTION_HEADER in data:
            return BarChartGameLoader(data)
        if HISTOGRAM_DATA_CONFIG_SECTION_HEADER in data:
            return HistogramGameLoader(data)
        if CANDLESTICK_DATA_CONFIG_SECTION_HEADER in data:
            return CandlestickChartGameLoader(data)
        if LINECHART_DATA_CONFIG_SECTION_HEADER in data:
            return LineChartGameLoader(data)
        raise DataConfigSectionMissingException()

    @staticmethod
    def _loadConfig(configFilePath: str)->dict[str,Any]:
        """
        Loads TOML configuration file.

        Args:
            configFilePath (str): Path to the config file.

        Returns:
            dict[str,Any]: Representation of the config file.
        """
        with open(configFilePath,"rb") as configFile:
            data = tomllib.load(configFile)
            return data
    
    def _loadEvaluatorClass(self, source: str) -> None:
        """
        Detemines final type of the evaluator.
        It loads file with the class as a module and stores type information.
        
        Args:
            source (str): Module or file with the class implementing GameEvaluator.

        Raises:
            EvaluatorLoadFailedException: Unknown error.
            InvalidEvaluatorException: Provided class does not inherit from GameEvaluator.
        """
        parts = modulePart, className = source.rsplit(":", 1)
        modulePart, className = parts[0], parts[1]
        path = Path(modulePart)

        if path.suffix == ".py":
            filePath = Path(modulePart)
            spec = importlib.util.spec_from_file_location(filePath.stem, filePath)
            if spec is None:
                raise EvaluatorLoadFailedException()
            module = importlib.util.module_from_spec(spec=spec)
            sys.modules[filePath.stem] = module
            spec.loader.exec_module(module) # pyright: ignore[reportOptionalMemberAccess]
        else:
            module = importlib.import_module(modulePart)
        
        evaluatorClass = getattr(module,className)
        if not issubclass(evaluatorClass, GameEvaluator):
            raise InvalidEvaluatorException(source)
        self.evaluatorType = evaluatorClass

    
    def _loadGeneralConfig(self, data: dict[str,Any]):
        """
        Loads general config, such as the title, x and y axis labels and evaluator.
        Evaluator is optional

        Args:
            data (dict[str,Any]): Loaded config file.

        Raises:
            InvalidGeneralConfigException: Required key is missing.
        """
        if X_AXIS_LABEL_KEY in data[GENERAL_CONFIG_SECTION_HEADER]:
            self.xAxisLabel = data[GENERAL_CONFIG_SECTION_HEADER][X_AXIS_LABEL_KEY]
        else:
            raise InvalidGeneralConfigException(X_AXIS_LABEL_KEY)
        
        if Y_AXIS_LABEL_KEY in data[GENERAL_CONFIG_SECTION_HEADER]:
            self.yAxisLabel = data[GENERAL_CONFIG_SECTION_HEADER][Y_AXIS_LABEL_KEY]
        else:
            raise InvalidGeneralConfigException(Y_AXIS_LABEL_KEY)
        
        if TITLE_KEY in data[GENERAL_CONFIG_SECTION_HEADER]:
            self.title = data[GENERAL_CONFIG_SECTION_HEADER][TITLE_KEY]
        else:
            raise InvalidGeneralConfigException(TITLE_KEY)
        
        if INSTRUCTIONS_KEY in data[GENERAL_CONFIG_SECTION_HEADER]:
            self.instructions = data[GENERAL_CONFIG_SECTION_HEADER][INSTRUCTIONS_KEY]
        else:
            raise InvalidGeneralConfigException(INSTRUCTIONS_KEY)
        
        if WIDTH_KEY in data[GENERAL_CONFIG_SECTION_HEADER]:
            self.plotWidth = data[GENERAL_CONFIG_SECTION_HEADER][WIDTH_KEY]
            if not isinstance(self.plotWidth, int):
                raise InvalidDataFormatException("Plot width must be an integer.",WIDTH_KEY)
            if self.plotWidth < 0:
                raise InvalidDataFormatException("Plot width must be non negative.", WIDTH_KEY)

        else:
            raise InvalidGeneralConfigException(WIDTH_KEY)
        
        if HEIGHT_KEY in data[GENERAL_CONFIG_SECTION_HEADER]:
            self.plotHeight = data[GENERAL_CONFIG_SECTION_HEADER][HEIGHT_KEY]
            if not isinstance(self.plotHeight, int):
                raise InvalidDataFormatException("Plot height must be an integer.",HEIGHT_KEY)
            if self.plotHeight < 0:
                raise InvalidDataFormatException("Plot height must be non negative.", HEIGHT_KEY)
        else:
            raise InvalidGeneralConfigException(HEIGHT_KEY)
        
        if ORIGIN_HEADER in data[GENERAL_CONFIG_SECTION_HEADER]:
            if ORIGIN_X_KEY in data[GENERAL_CONFIG_SECTION_HEADER][ORIGIN_HEADER] and ORIGIN_Y_KEY in data[GENERAL_CONFIG_SECTION_HEADER][ORIGIN_HEADER]:
                self.originX = data[GENERAL_CONFIG_SECTION_HEADER][ORIGIN_HEADER][ORIGIN_X_KEY]
                self.originY = data[GENERAL_CONFIG_SECTION_HEADER][ORIGIN_HEADER][ORIGIN_Y_KEY]
                if not isinstance(self.originX, int) or not isinstance(self.originY, int):
                    raise InvalidDataFormatException("Origin coordinates must be integers.",ORIGIN_HEADER)
                if self.originX < 0 or self.originY < 0:
                    raise InvalidDataFormatException("Origin coordinates must be non negative.",ORIGIN_HEADER)
            else:
                raise InvalidGeneralConfigException(ORIGIN_HEADER)
        else:
            raise InvalidGeneralConfigException(ORIGIN_HEADER)
        
        if EVALUATOR_KEY in data[GENERAL_CONFIG_SECTION_HEADER]:
            self._loadEvaluatorClass(data[GENERAL_CONFIG_SECTION_HEADER][EVALUATOR_KEY])
    
    @abstractmethod
    def _loadData(self, data: dict[str,Any]):
        """
        Loads plot data from the config file.

        Args:
            data (dict[str,Any]): Loaded config file.
        """
        pass

    def GetUserSolver(self)->ChartSolver:
        return self.userSolver

    def GetSolutionSolver(self)->ChartSolver:
        return self.solutionSolver

    def GetPlotMetadata(self)->PlotMetadata:
        return self.plotMetadata

    def GetEvaluator(self)->GameEvaluator:
        return self.evaluatorType()
    
    def GetInstructions(self):
        return self.instructions
    
    def GetWidth(self):
        return self.plotWidth
    
    def GetHeight(self):
        return self.plotHeight
    
    @staticmethod
    @abstractmethod
    def GetGameMode()->GameModes:
        pass

def ValidateListUnderKeyword(keyword : str, listToValidate : list, itemType : type|Union[Any,Any]):
    #TODO better using get_args abd get_origin
    typeName = itemType.__name__ if itemType != Union[int,float] else float.__name__
    if not isinstance(listToValidate, list):
        raise InvalidDataFormatException(f"Data under \"{keyword}\" keyword must be a list of {typeName}.",keyword)
    for item in listToValidate:
        if not isinstance(item,itemType):
            raise InvalidDataFormatException(f"List under \"{keyword}\" key must be a list of {typeName}.",keyword)


GROUPS_KEY = "groups"

class BarChartGameLoader(GameLoader):
    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
        self.userSolver : BarChartSolver = self.userSolver
        self.solutionSolver : BarChartSolver = self.solutionSolver
    
    @staticmethod
    def _validateData(data: list[list[float]], whatToGuess: list[list[bool]], names: list[list[str]]):
        if not isinstance(data,list):
            raise InvalidDataFormatException(f"Data under \"{GROUPS_KEY}\" keyword must be a list of lists of floats.",GROUPS_KEY)
        
        if not isinstance(whatToGuess,list):
            raise InvalidDataFormatException(f"Data under \"{IS_GUESS_KEY}\" keyword must be a list of lists of booleans.",IS_GUESS_KEY)
        
        if not isinstance(names, list):
            raise InvalidDataFormatException(f"Data under \"{NAMES_KEY}\" keyword must be a list of lists of strings.",NAMES_KEY)
        
        if len(data) != len(whatToGuess) or len(data) != len(names):
            raise InvalidDataFormatException(f"Lists under \"{GROUPS_KEY}\" keyword, under \"{IS_GUESS_KEY}\" keyword and under \"{NAMES_KEY}\" keyword must be of the same length.",GROUPS_KEY)
        
        for i in range(len(data)):
            if not isinstance(data[i],list) or not isinstance(whatToGuess[i],list) or not isinstance(names[i],list):
                raise InvalidDataFormatException(f"Data under \"{GROUPS_KEY}\" keyword, under \"{IS_GUESS_KEY}\" keyword and under \"{NAMES_KEY}\" keyword must be lists of lists.", GROUPS_KEY)
            if len(data[i]) != len(whatToGuess[i]) or len(data[i]) != len(names[i]):
                raise InvalidDataFormatException(f"Sublists of lists under \"{GROUPS_KEY}\" keyword, under \"{IS_GUESS_KEY}\" keyword and under \"{NAMES_KEY}\" keyword must be of the same length for every index.",GROUPS_KEY)
            for j in range(len(data[i])):
                if not isinstance(data[i][j],int) and not isinstance(data[i][j],float):
                    raise InvalidDataFormatException(f"Data under \"{GROUPS_KEY}\" keyword must be a list of lists of floats.",GROUPS_KEY)
                if not isinstance(whatToGuess[i][j],bool):
                    raise InvalidDataFormatException(f"Data under \"{IS_GUESS_KEY}\" keyword must be a list of lists of booleans.",IS_GUESS_KEY)
                if not isinstance(names[i][j],str):
                    raise InvalidDataFormatException(f"Data under \"{NAMES_KEY}\" keyword must be a list of lists of strings.",NAMES_KEY)
    @staticmethod    
    def _createUserData(data: list[list[float]], isGuess: list[list[bool]])->list[list[float]]:
        result = []
        assert len(data) == len(isGuess)
        for i in range(len(data)):
            assert len(data[i]) == len(isGuess[i])
            newSublist = []
            for j in range(len(data[i])):
                if not isGuess[i][j]:
                    newSublist.append(data[i][j])
                else:
                    newSublist.append(0)
            result.append(newSublist)
        return result
    
    def _getDefaultEvaluatorType(self)->Type[GameEvaluator]:
        return DefaultBarChartEvaluator
    
    def _loadData(self, data: dict[str, Any]):
        gameData = data[BARCHART_DATA_CONFIG_SECTION_HEADER]
        groups  : Optional[list[list[float]]] = None 
        isGuess : Optional[list[list[bool ]]] = None 
        names   : Optional[list[list[str  ]]] = None

        if GROUPS_KEY in gameData:
            groups = gameData[GROUPS_KEY]
        else:
            raise InvalidDataConfigSectionException(GROUPS_KEY,BARCHART_DATA_CONFIG_SECTION_HEADER)
        
        if IS_GUESS_KEY in gameData:
            isGuess = gameData[IS_GUESS_KEY]
        else:
            raise InvalidDataConfigSectionException(IS_GUESS_KEY,BARCHART_DATA_CONFIG_SECTION_HEADER)
        
        if NAMES_KEY in gameData:
            names = gameData[NAMES_KEY]
        else:
            raise InvalidDataConfigSectionException(NAMES_KEY,BARCHART_DATA_CONFIG_SECTION_HEADER)
        
        assert groups  is not None
        assert isGuess is not None
        assert names   is not None
        
        BarChartGameLoader._validateData(groups,isGuess, names)
        userData = BarChartGameLoader._createUserData(groups,isGuess)
        solutionData = groups
        metadata : BarChartMetadata = CreateBarChartMetadata(self.title, self.xAxisLabel, self.yAxisLabel, solutionData, self.plotHeight)

        rescaledUserData = RescaleListOfLists(userData,metadata.heightScaleFactor)
        rescaledSolutionData = RescaleListOfLists(solutionData,metadata.heightScaleFactor)

        solutionChart : VariableBarChart = VariableBarChart(names,None)
        userChart : VariableBarChart = VariableBarChart(names,None)


        self.solutionSolver = BarChartSolver(variableChart=solutionChart,
                                             width=INITIAL_WIDTH,
                                             initialHeights=rescaledSolutionData,
                                             spacing=INITIAL_SPACING, 
                                             innerSpacing=INITIAL_INNER_SPACING, 
                                             xCoordinate=self.originX, 
                                             yCoordinate=self.originY)
        
        self.userSolver = BarChartSolver(variableChart=userChart,
                                         width=INITIAL_WIDTH,
                                         initialHeights=rescaledUserData,
                                         spacing=INITIAL_SPACING, 
                                         innerSpacing=INITIAL_INNER_SPACING,  
                                         xCoordinate=self.originX, 
                                         yCoordinate=self.originY)

        self.plotMetadata = metadata
        self._lock(isGuess)
    
    @staticmethod
    def GetGameMode() -> GameModes:
        return GameModes.BarChart
    
    def _lock(self, isGuess : list[list[bool]]):
        for i in range(len(isGuess)):
            for j in range(len(isGuess[i])):
                if not isGuess[i][j]:
                    self.userSolver.SwitchRectangleLock(i,j)


POINTS_KEY = "points"

class LineChartGameLoader(GameLoader):
    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
        self.userSolver : LineChartSolver = self.userSolver
        self.solutionSolver : LineChartSolver = self.solutionSolver
    
    @staticmethod
    def _validateData(data : list[float], isGuess : list[bool], names : list[str]):
        ValidateListUnderKeyword(POINTS_KEY,data,Union[int,float])
        ValidateListUnderKeyword(IS_GUESS_KEY,isGuess,bool)
        ValidateListUnderKeyword(NAMES_KEY,names,str)
        if len(data) != len(isGuess) or len(data) != len(names):
            raise InvalidDataFormatException(f"Lists under \"{POINTS_KEY}\" key, \"{IS_GUESS_KEY}\" key and \"{NAMES_KEY}\" key must be of the same length.",POINTS_KEY)
    
    @staticmethod
    def _createUserData(data: list[float], isGuess: list[bool], xAxisValue : float = 0)->list[float]:
        assert len(data) == len(isGuess)
        return [data[i] if not isGuess[i] else xAxisValue for i in range(len(data))]
    
    def _loadData(self, data: dict[str, Any]):
        gameData = data[LINECHART_DATA_CONFIG_SECTION_HEADER]
        points  : Optional[list[float]] = None
        isGuess : Optional[list[bool ]] = None
        names   : Optional[list[str  ]] = None
        xAxisValue : float = 0

        if POINTS_KEY in gameData:
            points = gameData[POINTS_KEY]
        else:
            raise InvalidDataConfigSectionException(POINTS_KEY, LINECHART_DATA_CONFIG_SECTION_HEADER)
        
        if NAMES_KEY in gameData:
            names = gameData[NAMES_KEY]
        else:
            raise InvalidDataConfigSectionException(NAMES_KEY, LINECHART_DATA_CONFIG_SECTION_HEADER)
        
        if IS_GUESS_KEY in gameData:
            isGuess = gameData[IS_GUESS_KEY]
        else:
            raise InvalidDataConfigSectionException(IS_GUESS_KEY, LINECHART_DATA_CONFIG_SECTION_HEADER)
        
        if X_AXIS_VALUE_KEY in gameData:
            xAxisValue = gameData[X_AXIS_VALUE_KEY]
            if not isinstance(xAxisValue,float) and not isinstance(xAxisValue, int):
                raise InvalidDataFormatException(f"Value under \"{X_AXIS_VALUE_KEY}\" must be float.",X_AXIS_VALUE_KEY)
        
        assert points  is not None
        assert isGuess is not None
        assert names   is not None

        LineChartGameLoader._validateData(points, isGuess, names)
        solutionData = points

        metadata: LineChartMetadata = CreateLineChartMetadata(self.title, xAxisValue, solutionData, self.xAxisLabel, self.yAxisLabel, self.plotHeight)

        rescaledXAxisValue = xAxisValue*metadata.heightScaleFactor
        userData = LineChartGameLoader._createUserData(points,isGuess, xAxisValue)

        rescaledUserData = RescaleList(userData, metadata.heightScaleFactor, rescaledXAxisValue)
        rescaledSolutionData = RescaleList(solutionData, metadata.heightScaleFactor, rescaledXAxisValue)

        solutionChart : VariableLineChart = VariableLineChart(names)
        userChart : VariableLineChart = VariableLineChart(names)

        self.solutionSolver = LineChartSolver(variableChart=solutionChart,
                                              width=INITIAL_WIDTH, 
                                              initialValues=rescaledSolutionData, 
                                              xCoordinate=self.originX,
                                              yCoordinate=self.originY,
                                              padding=INITIAL_PADDING)
        
        self.userSolver = LineChartSolver(variableChart=userChart,
                                          width=INITIAL_WIDTH,
                                          initialValues=rescaledUserData,
                                          xCoordinate=self.originX,
                                          yCoordinate=self.originY,
                                          padding=INITIAL_PADDING)
        self.plotMetadata = metadata

        self._lock(isGuess)

    def _getDefaultEvaluatorType(self)->Type[GameEvaluator]:
        return DefaultLineChartEvaluator
    
    def _lock(self, isGuess: list[bool]):
        for i in range(len(isGuess)):
            if not isGuess[i]:
                self.userSolver.SwitchPointLock(i)


    @staticmethod
    def GetGameMode() -> GameModes:
        return GameModes.LineChart

OPENINGS_KEY = "openings"
CLOSINGS_KEY = "closings"
MAXIMUMS_KEY = "maximums"
MINIMUMS_KEY = "minimums"

class CandlestickChartGameLoader(GameLoader):
    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
        self.userSolver : CandlestickChartSolver = self.userSolver
        self.solutionSolver : CandlestickChartSolver = self.solutionSolver

    @dataclass
    class CandleData:
        openings: list[float]
        closings: list[float]
        minimums: list[float]
        maximums: list[float]
    
    def _loadData(self, data: dict[str, Any]):
        gameData = data[CANDLESTICK_DATA_CONFIG_SECTION_HEADER]
        openings : Optional[list[float]] = None
        closings : Optional[list[float]] = None
        maximums : Optional[list[float]] = None
        minimums : Optional[list[float]] = None
        isGuess  : Optional[list[bool ]] = None
        names    : Optional[list[str  ]] = None
        xAxisValue : float   = 0

        if X_AXIS_VALUE_KEY in gameData:
            xAxisValue = gameData[X_AXIS_VALUE_KEY]
            if not isinstance(xAxisValue,float) and not isinstance(xAxisValue, int):
                raise InvalidDataFormatException(f"Value under \"{X_AXIS_VALUE_KEY}\" must be float.",X_AXIS_VALUE_KEY)
        
        if OPENINGS_KEY in gameData:
            openings = gameData[OPENINGS_KEY]
        else:
            raise InvalidDataConfigSectionException(OPENINGS_KEY, CANDLESTICK_DATA_CONFIG_SECTION_HEADER)
        
        if CLOSINGS_KEY in gameData:
            closings = gameData[CLOSINGS_KEY]
        else:
            raise InvalidDataConfigSectionException(CLOSINGS_KEY,CANDLESTICK_DATA_CONFIG_SECTION_HEADER)
        
        if MAXIMUMS_KEY in gameData:
            maximums = gameData[MAXIMUMS_KEY]
        else:
            raise InvalidDataConfigSectionException(MAXIMUMS_KEY,CANDLESTICK_DATA_CONFIG_SECTION_HEADER)
        
        if MINIMUMS_KEY in gameData:
            minimums = gameData[MINIMUMS_KEY]
        else:
            raise InvalidDataConfigSectionException(MINIMUMS_KEY,CANDLESTICK_DATA_CONFIG_SECTION_HEADER)
        
        if IS_GUESS_KEY in gameData:
            isGuess = gameData[IS_GUESS_KEY]
        else:
            raise InvalidDataConfigSectionException(IS_GUESS_KEY, CANDLESTICK_DATA_CONFIG_SECTION_HEADER)

        if NAMES_KEY in gameData:
            names = gameData[NAMES_KEY]
        else:
            raise InvalidDataConfigSectionException(NAMES_KEY,CANDLESTICK_DATA_CONFIG_SECTION_HEADER)
        
        assert openings is not None
        assert closings is not None
        assert minimums is not None
        assert maximums is not None
        assert names    is not None
        assert isGuess  is not None

        CandlestickChartGameLoader._validateData(openings,closings,minimums,maximums,names,isGuess)
        userData = CandlestickChartGameLoader._createUserData(openings,closings,minimums,maximums,isGuess, xAxisValue)

        metadata : CandlesticPlotMetadata = CreateCandlesticChartMetadata(self.title,self.xAxisLabel,self.yAxisLabel,xAxisValue,openings,closings,minimums,maximums,self.plotHeight)
        
        rescaledXAxisValue = xAxisValue*metadata.heightScaleFactor
        rescaledUserData = self.CandleData(openings=RescaleList(userData.openings,metadata.heightScaleFactor,rescaledXAxisValue), # pyright: ignore[reportArgumentType]
                                           closings=RescaleList(userData.closings,metadata.heightScaleFactor,rescaledXAxisValue), # pyright: ignore[reportArgumentType]
                                           minimums=RescaleList(userData.minimums,metadata.heightScaleFactor,rescaledXAxisValue), # pyright: ignore[reportArgumentType]
                                           maximums=RescaleList(userData.maximums,metadata.heightScaleFactor,rescaledXAxisValue)) # pyright: ignore[reportArgumentType]
        rescaledSolutionData = self.CandleData(openings=RescaleList(openings,metadata.heightScaleFactor,rescaledXAxisValue), # pyright: ignore[reportArgumentType]
                                               closings=RescaleList(closings,metadata.heightScaleFactor,rescaledXAxisValue), # pyright: ignore[reportArgumentType]
                                               minimums=RescaleList(minimums,metadata.heightScaleFactor,rescaledXAxisValue), # pyright: ignore[reportArgumentType]
                                               maximums=RescaleList(maximums,metadata.heightScaleFactor,rescaledXAxisValue)) # pyright: ignore[reportArgumentType]
        
        isPositive = [openings[i] - closings[i] >= 0 for i in range(len(openings))]
        solutionChart : VariableCandlesticChart = VariableCandlesticChart(isPositive,names)
        userChart : VariableCandlesticChart = VariableCandlesticChart(isPositive,names)

        self.solutionSolver = CandlestickChartSolver(variableChart=solutionChart,
                                                     width=INITIAL_WIDTH,
                                                     initialOpening=rescaledSolutionData.openings, 
                                                     initialClosing=rescaledSolutionData.closings, 
                                                     initialMinimum=rescaledSolutionData.minimums, 
                                                     initialMaximum=rescaledSolutionData.maximums, 
                                                     spacing=INITIAL_SPACING,
                                                     xCoordinate=self.originX,
                                                     yCoordinate=self.originY)
        
        self.userSolver = CandlestickChartSolver(variableChart=userChart,
                                                 width=INITIAL_WIDTH,
                                                 initialOpening=rescaledUserData.openings, 
                                                 initialClosing=rescaledUserData.closings, 
                                                 initialMinimum=rescaledUserData.minimums, 
                                                 initialMaximum=rescaledUserData.maximums, 
                                                 spacing=INITIAL_SPACING,
                                                 xCoordinate=self.originX,
                                                 yCoordinate=self.originY)
        self.plotMetadata = metadata
        self._lock(isGuess)

    @staticmethod
    def _validateData(openings : list[float], closings : list[float], minimums : list[float], maximums : list[float], names : list[str], isGuess : list[bool]):
        ValidateListUnderKeyword(OPENINGS_KEY,openings,Union[int,float])
        ValidateListUnderKeyword(CLOSINGS_KEY,closings,Union[int,float])
        ValidateListUnderKeyword(MINIMUMS_KEY,minimums,Union[int,float])
        ValidateListUnderKeyword(MAXIMUMS_KEY,maximums,Union[int,float])
        ValidateListUnderKeyword(NAMES_KEY,names,str)
        ValidateListUnderKeyword(IS_GUESS_KEY,isGuess,bool)

        if len(openings) != len(closings) or len(openings) != len(maximums) or len(openings) != len(minimums) or len(openings) != len(names) or len(openings) != len(isGuess):
            raise InvalidDataFormatException(f"Lists under \"{OPENINGS_KEY}\" key, \"{CLOSINGS_KEY}\" key, \"{MINIMUMS_KEY}\" key, \"{MAXIMUMS_KEY}\" key, \"{IS_GUESS_KEY}\" key and \"{NAMES_KEY}\" key must be of the same length.",OPENINGS_KEY)

    def _getDefaultEvaluatorType(self)->Type[GameEvaluator]:
        return DefaultCandlestickChartEvaluator
    
    @staticmethod
    def _createUserData(openings : list[float], closings : list[float], minimums : list[float], maximums : list[float], isGuess : list[bool], xAxisValue : float =0)->CandleData:
        userOpenings, userClosings, userMinimums, userMaximums = [],[],[],[]
        for i in range(len(openings)):
            if isGuess[i]:
                userOpenings.append(xAxisValue)
                userClosings.append(xAxisValue)
                userMinimums.append(xAxisValue)
                userMaximums.append(xAxisValue)
            else:
                userOpenings.append(openings[i])
                userClosings.append(closings[i])
                userMinimums.append(minimums[i])
                userMaximums.append(maximums[i])

        return CandlestickChartGameLoader.CandleData(userOpenings,userClosings,userMinimums,userMaximums)

    @staticmethod
    def GetGameMode() -> GameModes:
        return GameModes.CandlestickChart
    
    def _lock(self,isGuess: list[bool]):
        for i in range(len(isGuess)):
            if not isGuess[i]:
                self.userSolver.SwitchCandleLock(i)

INTERVALS_KEY = "interval_boundries"
BUCKET_VALUE_KEY = "values"

class HistogramGameLoader(GameLoader):
    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
        self.userSolver : HistogramSolver = self.userSolver
        self.solutionSolver : HistogramSolver = self.solutionSolver
    
    @staticmethod
    def _validateData(intervals : list[float], values : list[float], isGuess: list[bool]):

        ValidateListUnderKeyword(INTERVALS_KEY, intervals, Union[int,float])
        ValidateListUnderKeyword(BUCKET_VALUE_KEY, values, Union[int,float])
        ValidateListUnderKeyword(IS_GUESS_KEY,    isGuess, bool)

        if len(intervals) <= 1:
            raise InvalidDataFormatException(f"List under \"{INTERVALS_KEY}\" key must contain at least 2 items.",INTERVALS_KEY)

        if len(values) != len(isGuess):
            raise InvalidDataFormatException(f"Lists under \"{BUCKET_VALUE_KEY}\" key and \"{IS_GUESS_KEY}\" key msut be of the same length.",BUCKET_VALUE_KEY)
        
        if len(intervals)-1 != len(values):
            raise InvalidDataFormatException(f"Invalid amount of interval boundaries. List under \"{INTERVALS_KEY}\" key must contain one less item than list under \"{BUCKET_VALUE_KEY}\" key.", INTERVALS_KEY) 

        boundary = intervals[0]
        for i in range(1,len(intervals)):
            current = intervals[i]
            if current <= boundary:
                raise InvalidDataFormatException(f"Interval boundries in under \"{INTERVALS_KEY}\" key must be ordered and non-equal. Values {boundary} and {current} are either equal or in wrong order.",INTERVALS_KEY)
            boundary = current

    @staticmethod
    def _getUserData(data: list[float], isGuess : list[bool]):
        assert len(data) == len(isGuess)
        return [data[i] if not isGuess[i] else 0 for i in range(len(data))]

    @staticmethod
    def _getIntervals(boundries: list[float]):
        assert len(boundries) > 1
        return list(pairwise(boundries))


    def _loadData(self, data: dict[str, Any]):
        gameData = data[HISTOGRAM_DATA_CONFIG_SECTION_HEADER]
        intervals : Optional[list[float]] = None
        values    : Optional[list[float]] = None
        isGuess   : Optional[list[bool ]] = None

        if INTERVALS_KEY in gameData:
            intervals = gameData[INTERVALS_KEY]
        else:
            raise InvalidDataConfigSectionException(INTERVALS_KEY, HISTOGRAM_DATA_CONFIG_SECTION_HEADER)
        
        if BUCKET_VALUE_KEY in gameData:
            values = gameData[BUCKET_VALUE_KEY]
        else:
            raise InvalidDataConfigSectionException(BUCKET_VALUE_KEY,HISTOGRAM_DATA_CONFIG_SECTION_HEADER)
        
        if IS_GUESS_KEY in gameData:
            isGuess = gameData[IS_GUESS_KEY]
        else:
            raise InvalidDataConfigSectionException(IS_GUESS_KEY,HISTOGRAM_DATA_CONFIG_SECTION_HEADER)

        assert intervals is not None
        assert values    is not None
        assert isGuess   is not None

        HistogramGameLoader._validateData(intervals,values,isGuess)
        userValues = HistogramGameLoader._getUserData(values,isGuess)
        intervalTuples = HistogramGameLoader._getIntervals(intervals)

        metadata = CreateHistogramMetadata(title=self.title, 
                                           xAxisLabel=self.xAxisLabel, 
                                           yAxisLabel=self.yAxisLabel, 
                                           initialValues=values, 
                                           intervals=intervalTuples,
                                           plotHeight=self.plotHeight)
        
        rescaledUserValues = [RescaleList(userValues,metadata.heightScaleFactor)]
        rescaledSolutionValues = [RescaleList(values,metadata.heightScaleFactor)]

        print("user data", rescaledUserValues)
        print("solution data", rescaledSolutionValues)
        print("intervals",intervalTuples)
        #input()

        
        
        self.solutionSolver = HistogramSolver.new(width=INITIAL_WIDTH,
                                                  initialHeights=rescaledSolutionValues,
                                                  intervals=intervalTuples,
                                                  paddingLeft=INITIAL_PADDING,
                                                  widthScalesForGroups=metadata.widthScaleFactor,
                                                  xCoordinate=self.originX,
                                                  yCoordinate=self.originY)
        
        self.userSolver = HistogramSolver.new(width=INITIAL_WIDTH,
                                                  initialHeights=rescaledUserValues,
                                                  intervals=intervalTuples,
                                                  paddingLeft=INITIAL_PADDING,
                                                  widthScalesForGroups=metadata.widthScaleFactor,
                                                  xCoordinate=self.originX,
                                                  yCoordinate=self.originY)
        self.plotMetadata = metadata
        self._lock(isGuess)

    def _getDefaultEvaluatorType(self)->Type[GameEvaluator]:
        return DefaultHistogramEvaluator
    
    def _lock(self, isGuess : list[bool]):
        for i in range(len(isGuess)):
            if not isGuess[i]:
                self.userSolver.SwitchBucketLock(i)
    
    @staticmethod
    def GetGameMode() -> GameModes:
        return GameModes.Histogram