from .chartsolver import ChartSolver
from kiwiplots.variablechart import VariableBarChart, VariableChart
from .barchartsolver import BarChartSolver
from kiwisolver import Solver, Constraint

class HistogramSolver(ChartSolver):
    @classmethod
    def new(cls,width: int, initialHeights: list[float], intervals: list[tuple[float,float]], paddingLeft: int, widthScalesForGroups : list[list[float]], xCoordinate : int = 0, yCoordinate : int = 0):
        chart : VariableBarChart = VariableBarChart([["" for _ in initialHeights]], widthScalesForGroups)
        solver : BarChartSolver = BarChartSolver(variableChart=chart,
                                                 width=width,
                                                 initialHeights=initialHeights,
                                                 spacing=paddingLeft,
                                                 innerSpacing=0,
                                                 xCoordinate=xCoordinate,
                                                 yCoordinate=yCoordinate)
        solver.SetIntervalValues(intervals=intervals)
        return cls(solver)
        


    def __init__(self,solver : BarChartSolver):
        # solver has to have set intervals #TODO
        self.innerSolver : BarChartSolver = solver
        self.solver : Solver = solver.solver
        self.variableChart : VariableBarChart = solver.variableChart
    
    def _setConstraints(self):
        return
    
    def _addEditVariables(self):
        return
    
    def _initialSuggest(self):
        return
    
    def SwitchBucketLock(self, index : int):
        self.innerSolver.SwitchRectangleLock(0,index)
    
    def Feed(self, otherSolver: "HistogramSolver"):
        ChartSolver.Feed(self,otherSolver)

    def Solve(self):
        self.innerSolver.Solve()
    
    def Update(self):
        self.innerSolver.Update()
    
    def GetOrigin(self):
        return self.innerSolver.GetOrigin()
    
    def GetSpacing(self):
        return self.innerSolver.GetSpacing()
    
    def GetWidth(self):
        return self.innerSolver.GetWidth()
    
    def GetAxisHeight(self):
        return self.innerSolver.GetAxisHeight()
    
    def ChangeOrigin(self, newX: int, newY: int):
        self.innerSolver.ChangeOrigin(newX,newY)
    
    def ChangeAxisHeight(self, newHeight : int):
        self.innerSolver.ChangeAxisHeight(newHeight)
    
    def ChangeWidth(self, width: float):
        self.innerSolver.ChangeWidth(width)
    
    def ChangeSpacing(self, spacing: int):
        self.innerSolver.ChangeSpacing(spacing)
    
    def GetRectangleData(self):
        return self.innerSolver.GetRectangleData()
    
    def GetRectangleDataAsList(self):
        return self.innerSolver.GetRectangleDataAsList()
    
    def GetName(self, groupIndex: int, rectangleIndex: int):
        return self.innerSolver.GetName(groupIndex,rectangleIndex)
    
    def ChangeHeight(self, groupIndex: int, rectangleIndex: int, newHeight: int):
        self.innerSolver.ChangeHeight(groupIndex,rectangleIndex,newHeight)
    
    def ChangeColor(self, groupIndex: int, rectangleIndex: int, newColor: str):
        self.innerSolver.ChangeColor(groupIndex,rectangleIndex,newColor)
    
    def ChangeName(self,groupIndex: int, rectangleIndex: int, newName: str):
        self.innerSolver.ChangeName(groupIndex, rectangleIndex, newName)
    
    def ChangeWidthX(self,groupIndex: int, rectangleIndex : int, newX : float):
        self.innerSolver.ChangeWidthX(groupIndex,rectangleIndex,newX)
    
    def ChangeSpacingX(self,groupIndex: int, rectangleIndex : int, newX : float):
        self.innerSolver.ChangeSpacingX(groupIndex,rectangleIndex,newX)
    
    def AddRectangle(self,start: float, end: float, recHeight: float):
        
        print("--- solver.AddRectangle start ---")
        shoretestLength = self._getShortestIntervalLength()
        widthScale = (end-start)/shoretestLength
        height, constraintsToAdd, constraintsToRemove = self.innerSolver.variableChart.AddRectangleAsInterval(0,widthScale,start,end)
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

    def _getShortestIntervalLength(self):
        rectangles = self.GetRectangleDataAsList()
        val = min([abs(float(rec.rightTop.secondaryName) - abs(float(rec.leftBottom.secondaryName))) for rec in rectangles],default=1)
        return val if val > 0 else 1
   