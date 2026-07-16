"""Factory for creating game instances from configuration files."""
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
    """Loads game configurations and creates GameUI instances with appropriate handlers."""

    @staticmethod
    def LoadGameFromConfig(configFilePath : str):
        """Loads a game from a config file and returns a GameUI instance.

        Args:
            configFilePath: Path to the game configuration TOML file.

        Returns:
            GameUI: Configured game interface ready to play.
        """
        loader: GameLoader = GameLoader.GetLoader(configFilePath=configFilePath)

        solutionSolver = loader.GetSolutionSolver()
        userSolver = loader.GetUserSolver()
        metadata = loader.GetPlotMetadata()

        eventHandler = None

        if (loader.GetGameMode() == GameModes.BarChart):
            eventHandler = GameBarChartEventHandler(metadata,userSolver,GameBarChartDataViewer) # pyright: ignore[reportArgumentType]
        elif (loader.GetGameMode() == GameModes.LineChart):
            assert isinstance(loader,LineChartGameLoader)
            eventHandler = GameLineChartEventHandler(metadata,userSolver,GameLineChartDataViewer, loader.GetSolutionColor()) # pyright: ignore[reportArgumentType]
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

        return GameUI(gameEventHandler=eventHandler, # pyright: ignore[reportArgumentType]
                      instructionString=instructions,
                      userSolver=userSolver,
                      solutionSolver=solutionSolver,
                      plotMetadata=metadata,
                      evaluator=evaluator,
                      plotWidth=width,
                      plotHeight=height)