from .chartsolver import ChartSolver
from kiwiplots.variablechart import VariableBarChart, VariableChart
from .barchartsolver import BarChartSolver
from kiwisolver import Solver, Constraint
from kiwiplots.variablechart import VariableRectangleGroupChart, VariableHistogram
from .rectanglesolver import RectangleSolver
from kiwiplots.chartelements import ValueRectangle, ValueBucket

class HistogramSolver(RectangleSolver):


    def __init__(self, variableChart : VariableHistogram, width: int, initialHeights: list[float], padding: int,  xCoordinate: int = 0, yCoordinate: int = 0):
        self.initialHeights = initialHeights
        
        super().__init__(variableChart=variableChart,
                         width=width,
                         spacing=padding,
                         innerSpacing=0,
                         xCoordinate=xCoordinate,
                         yCoordinate=yCoordinate)
        
        self.variableChart : VariableHistogram = self.variableChart
    
    def _suggestHeights(self):
        for i in range(len(self.initialHeights)):
            self.solver.suggestValue(self.variableChart.groups[0].rectangles[i].height, self.initialHeights[i])
    

    def _suggestYAxisHeight(self):
        self.solver.suggestValue(self.variableChart.yAxisHeight, max(i for i in self.initialHeights)+10)

    def SwitchRectangleLock(self, groupIndex: int, recIndex: int) -> bool:
        if groupIndex != 0:
            raise ValueError()
        return super().SwitchRectangleLock(groupIndex,recIndex)
    
    def SwitchBucketLock(self, index : int)->bool:
        return self.SwitchRectangleLock(0,index)
    
    def Feed(self, otherSolver: "HistogramSolver"):
        ChartSolver.Feed(self,otherSolver)

    def GetBucketData(self)->list[ValueBucket]:
        return self.variableChart.Value() # pyright: ignore[reportReturnType]
    
  
    def GetGroupData(self)->list[list[ValueRectangle]]:
        return [self.GetBucketData()] # pyright: ignore[reportReturnType]
    

    def GetRectangleDataAsList(self)->list[ValueRectangle]:
        return self.GetBucketData() # pyright: ignore[reportReturnType]
    
    def AddBucket(self,start: float, end: float, recHeight: float):
        print("--- solver.AddRectangle start ---")
        shortestInterval = self.variableChart.GetShortestInterval()
        shoretestLength = shortestInterval[1] - shortestInterval[0]
        widthScale = (end-start)/shoretestLength
        height, constraintsToAdd, constraintsToRemove = self.variableChart.AddBucket(widthScale,start,end)
        for constr in constraintsToRemove:
            if self.solver.hasConstraint(constr): # pyright: ignore[reportArgumentType]
                self.solver.removeConstraint(constr) # pyright: ignore[reportArgumentType]
        for constr in constraintsToAdd:
            self.solver.addConstraint(constr)
        
        self.solver.addEditVariable(height,"strong")
        self.solver.suggestValue(height, recHeight)
        widthLock = self.switchConstraintLock(self.variableChart.width)
        spacingLock = self.switchConstraintLock(self.variableChart.spacing)
        self.Solve()
        self.switchConstraintLock(self.variableChart.width, widthLock)
        self.switchConstraintLock(self.variableChart.spacing, spacingLock)
        print("--- solver.AddRectangle end ---")
        pass
   