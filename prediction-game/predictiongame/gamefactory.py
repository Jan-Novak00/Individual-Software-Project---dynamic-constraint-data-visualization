from kiwiplots import *
from .gameloader import *
from .game_barcharteventhandler import GameBarChartEventHandler
from .game_dataviewer import *
from .game_uicore import GameUI


class GameFactory(UIFactory):

    @staticmethod
    def GetBarChartGame(configFilePath: str):
        pass

    @staticmethod
    def BarChartGameTEST():
        width = 1000
        height = 500
        data = [[1,2,3,4]]
        names = [["a","b","c","d"]]
        allData = []
        for sublist in data:
            allData.extend(sublist)
        userData = [[1,2,0,0]]
        newData = []
        newUserData = []
        scaleFactor = UIFactory._calculateScaleFactor(allData,height)
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
        
        class Mock:
            @staticmethod
            def Eval(a,b,c):
                return 14444444444444444444
            pass
        m = Mock()
        instructionString = "Bars follow the sequence from 1 to 4."
        return GameUI(eventHandler,instructionString,m,userSolver,solutionSolver,plotMetadata,width,height)