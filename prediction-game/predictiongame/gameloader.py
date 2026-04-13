from kiwiplots import *
from abc import ABC
from .gameevaluator import *
from .defaultevaluators import *
import tomllib
from typing import Any, Type
import importlib
import importlib.util
import sys
from pathlib import Path
from .gamemodes import GameModes

INITIAL_WIDTH : int   = 100
INITIAL_SPACING : int = 15
INITIAL_INNER_SPACING = 10
INITIAL_ORIGIN_X : int = 50
INITIAL_ORIGIN_Y : int = 30
INITIAL_PADDING : int = 10
INITIAL_COLOR : Union[str,int] = "blue"
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

IS_GUESS_KEYWORD = "is_guess"
NAMES_KEYWORD    = "names"

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
        modulePart, className = source.split(":")

        if modulePart.endswith(".py"):
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

GROUPS_KEYWORD = "groups"

class BarChartGameLoader(GameLoader):
    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
    
    @staticmethod
    def _validateData(data: list[list[float]], whatToGuess: list[list[bool]], names: list[list[str]]):
        if not isinstance(data,list):
            raise InvalidDataFormatException("Data under \"groups\" keyword must be a list of lists of floats.",GROUPS_KEYWORD)
        
        if not isinstance(whatToGuess,list):
            raise InvalidDataFormatException("Data under \"is_guess\" keyword must be a list of lists of booleans.",IS_GUESS_KEYWORD)
        
        if not isinstance(names, list):
            raise InvalidDataFormatException("Data under \"names\" keyword must be a list of lists of strings.",NAMES_KEYWORD)
        
        if len(data) != len(whatToGuess) or len(data) != len(names):
            raise InvalidDataFormatException("List under \"groups\" keyword, under \"is_guess\" keyword and under \"names\" keyword must be of the same length.",GROUPS_KEYWORD)
        
        for i in range(len(data)):
            if not isinstance(data[i],list) or not isinstance(whatToGuess[i],list) or not isinstance(names[i],list):
                raise InvalidDataFormatException("Data under \"groups\" keyword, under \"is_guess\" keyword and under \"names\" keyword must be lists of lists", GROUPS_KEYWORD)
            if len(data[i]) != len(whatToGuess[i]) or len(data[i]) != len(names[i]):
                raise InvalidDataFormatException("Sublists of lists under \"groups\" keyword, under \"is_guess\" keyword and under \"names\" keyword must be of the same length for every index.",GROUPS_KEYWORD)
            for j in range(len(data[i])):
                if not isinstance(data[i][j],int) or isinstance(data[i][j],float):
                    raise InvalidDataFormatException("Data under \"groups\" keyword must be a list of lists of floats.",GROUPS_KEYWORD)
                if not isinstance(whatToGuess[i][j],bool):
                    raise InvalidDataFormatException("Data under \"is_guess\" keyword must be a list of lists of booleans.",IS_GUESS_KEYWORD)
                if not isinstance(names[i][j],str):
                    raise InvalidDataFormatException("Data under \"names\" keyword must be a list of lists of strings.",NAMES_KEYWORD)
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
        groups  : list[list[float]] = None # pyright: ignore[reportAssignmentType]
        isGuess : list[list[bool]]  = None # pyright: ignore[reportAssignmentType]
        names   : list[list[str]]   = None  # pyright: ignore[reportAssignmentType]

        if GROUPS_KEYWORD in gameData:
            groups = gameData[GROUPS_KEYWORD]
        else:
            raise InvalidDataConfigSectionException(GROUPS_KEYWORD,BARCHART_DATA_CONFIG_SECTION_HEADER)
        
        if IS_GUESS_KEYWORD in gameData:
            isGuess = gameData[IS_GUESS_KEYWORD]
        else:
            raise InvalidDataConfigSectionException(IS_GUESS_KEYWORD,BARCHART_DATA_CONFIG_SECTION_HEADER)
        
        if NAMES_KEYWORD in gameData:
            names = gameData[NAMES_KEYWORD]
        else:
            raise InvalidDataConfigSectionException(NAMES_KEYWORD,BARCHART_DATA_CONFIG_SECTION_HEADER)
        
        BarChartGameLoader._validateData(groups,isGuess, names)
        userData = BarChartGameLoader._createUserData(groups,isGuess)
        solutionData = groups
        metadata : BarChartMetadata = CreateBarChartMetadata(self.title, self.xAxisLabel, self.yAxisLabel, solutionData, self.plotHeight)

        rescaledUserData = RescaleListOfLists(userData,metadata.heightScaleFactor)
        rescaledSolutionData = RescaleListOfLists(solutionData,metadata.heightScaleFactor)

        self.solutionSolver = BarChartSolver(width=INITIAL_WIDTH,
                                             initialHeights=rescaledSolutionData,
                                             spacing=INITIAL_SPACING, 
                                             innerSpacing=INITIAL_INNER_SPACING, 
                                             rectangleNames=names, 
                                             xCoordinate=self.originX, 
                                             yCoordinate=self.originY)
        
        self.userSolver = BarChartSolver(width=INITIAL_WIDTH,
                                             initialHeights=rescaledUserData,
                                             spacing=INITIAL_SPACING, 
                                             innerSpacing=INITIAL_INNER_SPACING, 
                                             rectangleNames=names, 
                                             xCoordinate=self.originX, 
                                             yCoordinate=self.originY)
        
        for i in range(len(isGuess)):
            for j in range(len(isGuess[i])):
                if not isGuess[i][j]:
                    self.userSolver.SwitchRectangleLock(i,j)

        self.plotMetadata = metadata
    
    @staticmethod
    def GetGameMode() -> GameModes:
        return GameModes.BarChart

class LineChartGameLoader(GameLoader):
    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
    
    def _loadData(self, data: dict[str, Any]):
        gameData = data[LINECHART_DATA_CONFIG_SECTION_HEADER]
        pass

    def _getDefaultEvaluatorType(self)->Type[GameEvaluator]:
        return DefaultLineChartEvaluator
    @staticmethod
    def GetGameMode() -> GameModes:
        return GameModes.LineChart

class CandlestickChartGameLoader(GameLoader):
    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
    
    def _loadData(self, data: dict[str, Any]):
        gameData = data[CANDLESTICK_DATA_CONFIG_SECTION_HEADER]
        pass

    def _getDefaultEvaluatorType(self)->Type[GameEvaluator]:
        return DefaultCandlestickChartEvaluator
    @staticmethod
    def GetGameMode() -> GameModes:
        return GameModes.CandlestickChart

class HistogramGameLoader(GameLoader):
    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
    
    def _loadData(self, data: dict[str, Any]):
        gameData = data[HISTOGRAM_DATA_CONFIG_SECTION_HEADER]
        pass

    def _getDefaultEvaluatorType(self)->Type[GameEvaluator]:
        return DefaultHistogramEvaluator
    
    @staticmethod
    def GetGameMode() -> GameModes:
        return GameModes.Histogram