from kiwiplots import *
from .gameloader import *
from .game_barcharteventhandler import GameBarChartEventHandler
from .game_dataviewer import *
from .game_uicore import GameUI
from .defaultevaluators import *
from .gamemodes import GameModes

class GameFactory(UIFactory):

    @staticmethod
    def GetBarChartGame(configFilePath: str):
        pass

    @staticmethod
    def BarChartGameTEST():
        width = 1000
        height = 500
        data = [[1,2,3,4],[1]]
        names = [["a","b","c","d"],["z"]]
        allData = []
        for sublist in data:
            allData.extend(sublist)
        userData = [[1,2,0,0],[0]]
        newData = []
        newUserData = []
        scaleFactor = CalculateScaleFactor(allData,height)
        for i in range(len(data)):
            newList = []
            newUserList = []
            for j in range(len(data[i])):
                newList.append(scaleFactor*data[i][j])
                newUserList.append(scaleFactor*userData[i][j])
            newData.append(newList)
            newUserData.append(newUserList)
        data = newData
        userData = newUserData

        print(data)
        print(userData)


        plotMetadata = BarChartMetadata("My bar chart game",scaleFactor,"x axis", "y axis")
        solutionSolver = BarChartSolver(100, data, 15, 10,names,50,30)
        userSolver = BarChartSolver(100,userData,15,10,names,50,30)
        userSolver.SwitchRectangleLock(0,0)
        userSolver.SwitchRectangleLock(0,1)
        eventHandler = GameBarChartEventHandler(plotMetadata=plotMetadata, solver=userSolver, dataViewerClass=GameBarChartDataViewer)
        
        evaluator = DefaultBarChartEvaluator()
        instructionString = "Bars follow the sequence from 1 to 4."
        return GameUI(eventHandler,instructionString,evaluator,userSolver,solutionSolver,plotMetadata,width,height)
    
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
            raise NotImplementedError()
        elif (loader.GetGameMode() == GameModes.CandlestickChart):
            raise NotImplementedError()
        elif (loader.GetGameMode() == GameModes.Histogram):
            raise NotImplementedError()
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