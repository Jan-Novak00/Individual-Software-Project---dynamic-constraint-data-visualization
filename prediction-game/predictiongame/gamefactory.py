from kiwiplots import *
from .gameloader import *
from .game_barcharteventhandler import GameBarChartEventHandler
from .game_linecharteventhandler import GameLineChartEventHandler
from .game_candelstickeventhandler import GameCandlestickChartEventHandler
from .game_histogramhandler import GameHistogramEventHandler
from .game_dataviewer import *
from .game_uicore import GameUI
from .defaultevaluators import *
from .gamemodes import GameModes

class GameFactory(UIFactory):

    @staticmethod
    def LoadGameFromConfig(configFilePath : str):
        loader: GameLoader = GameLoader.GetLoader(configFilePath=configFilePath)

        solutionSolver = loader.GetSolutionSolver()
        userSolver = loader.GetUserSolver()
        metadata = loader.GetPlotMetadata()

        eventHandler = None

        if (loader.GetGameMode() == GameModes.BarChart):
            eventHandler = GameBarChartEventHandler(metadata,userSolver,GameBarChartDataViewer) # pyright: ignore[reportArgumentType]
        elif (loader.GetGameMode() == GameModes.LineChart):
            eventHandler = GameLineChartEventHandler(metadata,userSolver,GameLineChartDataViewer) # pyright: ignore[reportArgumentType]
        elif (loader.GetGameMode() == GameModes.CandlestickChart):
            eventHandler = GameCandlestickChartEventHandler(metadata,userSolver,GameCandlestickChartDataViewer) # pyright: ignore[reportArgumentType]
        elif (loader.GetGameMode() == GameModes.Histogram):
            eventHandler = GameHistogramEventHandler(metadata,userSolver,GameHistogramDataViewer) # pyright: ignore[reportArgumentType]
        else:
            assert False, "Unreachable reached"
        
        evaluator = loader.GetEvaluator()
        instructions = loader.GetInstructions()
        width = loader.GetWidth()
        height = loader.GetHeight()

        return GameUI(gameEventHandler=eventHandler,
                      instructionString=instructions,
                      userSolver=userSolver,
                      solutionSolver=solutionSolver,
                      plotMetadata=metadata,
                      evaluator=evaluator,
                      plotWidth=width,
                      plotHeight=height)