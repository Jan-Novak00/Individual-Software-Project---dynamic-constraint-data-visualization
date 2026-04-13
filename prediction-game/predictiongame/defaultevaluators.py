from .gameevaluator import GameEvaluator
from kiwiplots import ChartSolver, BarChartSolver, PlotMetadata, BarChartMetadata

class DefaultBarChartEvaluator(GameEvaluator):
    @staticmethod
    def Eval(userSolver: BarChartSolver, solutionSolver: BarChartSolver, plotMetadata : BarChartMetadata) -> int:
        userGuess = [rec.GetHeight() for rec in userSolver.GetRectangleDataAsList()]
        realVals = [rec.GetHeight() for rec in solutionSolver.GetRectangleDataAsList()]

        assert len(realVals) == len(userGuess)

        totalError = sum([abs(userGuess[i]-realVals[i]) for i in range(len(realVals))])
        maxError = sum(realVals)

        score = 10000*(1-totalError/maxError)

        return round(score)

class DefaultCandlestickChartEvaluator(GameEvaluator):
    @staticmethod
    def Eval(userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata) -> int:
        return 0

class DefaultHistogramEvaluator(GameEvaluator):
    @staticmethod
    def Eval(userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata) -> int:
        return 0

class DefaultLineChartEvaluator(GameEvaluator):
    @staticmethod
    def Eval(userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata) -> int:
        return 0