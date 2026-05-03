from .gameevaluator import GameEvaluator
from kiwiplots import ChartSolver, BarChartSolver, PlotMetadata, BarChartMetadata, LineChartSolver, CandlestickChartSolver, HistogramSolver

class DefaultBarChartEvaluator(GameEvaluator):
    def Eval(self,userData, solutionData) -> int:
        print("solution data",solutionData)
        print("user data",solutionData)
        
        uDataNormalized_ = []
        sDataNormalized_ = []
        isGuessNormalized = []

        for g in userData:
            uDataNormalized_.extend(g)
        
        for g in solutionData:
            sDataNormalized_.extend(g)
        
        for b in self.isGuess:
            isGuessNormalized.extend(b)
        
        uDataNormalized = []
        sDataNormalized = []
        for i in range(len(isGuessNormalized)):
            if isGuessNormalized[i]:
                uDataNormalized.append(uDataNormalized_[i])
                sDataNormalized.append(sDataNormalized_[i])

        totalError = sum([abs(uDataNormalized[i]-sDataNormalized[i]) for i in range(len(sDataNormalized))])
        maxError = sum(sDataNormalized)

        score = 10000*(1-totalError/maxError)

        return round(score)

class DefaultCandlestickChartEvaluator(GameEvaluator):

    def Eval(self,userData, solutionData) -> int:
        uo_, uc_, umin_, umax_ = userData[0], userData[1], userData[2], userData[3]
        so_, sc_, smin_, smax_ = solutionData[0], solutionData[1], solutionData[2], solutionData[3]

        uo, uc, umin, umax = [],[],[],[]
        so, sc, smin, smax = [],[],[],[]

        for i in range(len(self.isGuess)):
            if self.isGuess[i]:
                uo.append(uo_[i])
                uc.append(uc_[i])
                umin.append(umin_[i])
                umax.append(umax_[i])
                so.append(so_[i])
                sc.append(sc_[i])
                smin.append(smin_[i])
                smax.append(smax_[i])

        
        userPriceChanges = [abs(uc[i] - uo[i]) for i in range(len(uo))]
        solutionPriceChanges = [abs(sc[i] - so[i]) for i in range(len(so))]
        userMinMaxChange = [abs(umax[i] - umin[i]) for i in range(len(uo))]
        solutionMinMaxChange = [abs(smax[i] - smin[i]) for i in range(len(so))]


        totalError = sum([abs(userPriceChanges[i] - solutionPriceChanges[i]) for i in range(len(userPriceChanges))]) + sum([abs(userMinMaxChange[i] - solutionMinMaxChange[i]) for i in range(len(userMinMaxChange))])
        maxError = abs(sum(solutionPriceChanges)) + abs(sum(solutionMinMaxChange))
        print("maxError",maxError)
        score = 10000*(1-totalError/maxError)

        return round(score)

class DefaultHistogramEvaluator(GameEvaluator):

    def Eval(self, userData, solutionData) -> int:
        userData_, solutionData_ = [], []
        for i in range(len(self.isGuess)):
            if self.isGuess[i]:
                userData_.append(userData[i])
                solutionData_.append(solutionData[i])

        totalError = sum([abs(userData_[i]-solutionData_[i]) for i in range(len(solutionData_))])

        maxError = sum(solutionData_)
        score = 10000*(1-totalError/maxError)

        return round(score)

class DefaultLineChartEvaluator(GameEvaluator):

    def Eval(self,userData, solutionData) -> int:

        userData_, solutionData_ = [], []
        for i in range(len(self.isGuess)):
            if self.isGuess[i]:
                userData_.append(userData[i])
                solutionData_.append(solutionData[i])

        totalError = sum([abs(userData_[i]-solutionData_[i]) for i in range(len(solutionData_))])

        maxError = sum(solutionData_)
        score = 10000*(1-totalError/maxError)

        return round(score)