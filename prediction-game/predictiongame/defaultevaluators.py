from .gameevaluator import GameEvaluator
from kiwiplots import ChartSolver, BarChartSolver, PlotMetadata, BarChartMetadata, LineChartSolver, CandlestickChartSolver

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
    def Eval(userSolver: CandlestickChartSolver, solutionSolver: CandlestickChartSolver, plotMetadata: PlotMetadata) -> int:
        userCandles = userSolver.GetCandleData()
        solutionCandles = solutionSolver.GetCandleData()

        userPriceChanges = [candle.GetHeight() for candle in userCandles]
        solutionPriceChanges = [candle.GetHeight() for candle in solutionCandles]
        userMinMaxChange = [candle.wickTop.Y - candle.wickBottom.Y for candle in userCandles]
        solutionMinMaxChange = [candle.wickTop.Y - candle.wickBottom.Y for candle in solutionCandles]

        assert len(userCandles) == len(solutionCandles)

        totalError = sum([abs(userPriceChanges[i] - solutionPriceChanges[i]) for i in range(len(userPriceChanges))]) + sum([abs(userMinMaxChange[i] - solutionMinMaxChange[i]) for i in range(len(userMinMaxChange))])
        maxError = sum(solutionPriceChanges) + sum(solutionMinMaxChange)
        
        score = 10000*(1-totalError/maxError)

        return round(score)

class DefaultHistogramEvaluator(GameEvaluator):
    @staticmethod
    def Eval(userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata) -> int:
        return 0

class DefaultLineChartEvaluator(GameEvaluator):
    @staticmethod
    def Eval(userSolver: ChartSolver, solutionSolver: ChartSolver, plotMetadata: PlotMetadata) -> int:
        return 0