from .chartsolver import ChartSolver
from kiwiplots.variablechart import VariableBarChart, VariableChart
from typing import Union
from kiwiplots.chartelements import ValueRectangle, VariableRectangle
from kiwisolver import Variable, Solver, Constraint
from .rectanglesolver import RectangleSolver

class BarChartSolver(RectangleSolver):
    """
    ChartSolver version for bar chart and histogram.
    """
    def __init__(self, variableChart : VariableBarChart, width: int, initialHeights: list[list[float]], spacing: int, innerSpacing: int, xCoordinate: int = 0, yCoordinate: int = 0):
        self.initialHeights = initialHeights

        super().__init__(variableChart=variableChart,
                         width=width,
                         spacing=spacing,
                         innerSpacing=innerSpacing,
                         xCoordinate=xCoordinate,
                         yCoordinate=yCoordinate)
        
        self.variableChart : VariableBarChart = self.variableChart
   
    def _suggestHeights(self):
         for ig in range(len(self.variableChart.groups)):
            group = self.variableChart.groups[ig]
            for ir, rec in enumerate(group):
                self.solver.suggestValue(rec.height,self.initialHeights[ig][ir])
    
    def _suggestYAxisHeight(self):
        self.solver.suggestValue(self.variableChart.yAxisHeight, max(max(group) for group in self.initialHeights)+10)

    def GetBarData(self):
        return self.data
    
    def GetBarDataAsList(self) -> list[ValueRectangle]:
        result = []
        data = self.GetBarData()
        for group in data: # pyright: ignore[reportOptionalIterable]
            result.extend(group)
        return result

    
    def AddGroup(self, firstRectangleName: str, firstRectangleHeight: float):
        print("--- solver.AddGroup method start ---")
        newGroup, newConstraints = self.variableChart.AddBarGroup(firstRectangleName=firstRectangleName)
        for constr in newConstraints:
            self.solver.addConstraint(constr)

        newRectangle = newGroup.rectangles[0]
        
        self.solver.addEditVariable(newRectangle.height,"strong")
        self.solver.suggestValue(newRectangle.height, firstRectangleHeight)

        widthLock = self.switchConstraintLock(self.variableChart.width)
        spacingLock = self.switchConstraintLock(self.variableChart.spacing)
        innerSpacingLock = self.switchConstraintLock(self.variableChart.innerSpacing)

        self.Solve()

        self.switchConstraintLock(self.variableChart.width, widthLock)
        self.switchConstraintLock(self.variableChart.spacing, spacingLock)
        self.switchConstraintLock(self.variableChart.innerSpacing,innerSpacingLock)
        
        print("--- solver.AddGroup method end ---")
    
    def AddBar(self, name: str, groupIndex: int, recHeight: float):
        print("--- solver.AddRectangle start ---")
        height, constraintsToAdd, constraintsToRemove = self.variableChart.AddBar(groupIndex=groupIndex,name=name)
        for constr in constraintsToRemove:
            if self.solver.hasConstraint(constr): # pyright: ignore[reportArgumentType]
                self.solver.removeConstraint(constr) # pyright: ignore[reportArgumentType]
        for constr in constraintsToAdd:
            self.solver.addConstraint(constr)
        
        self.solver.addEditVariable(height,"strong")
        self.solver.suggestValue(height, recHeight)

        widthLock = self.switchConstraintLock(self.variableChart.width)
        spacingLock = self.switchConstraintLock(self.variableChart.spacing)
        innerSpacingLock = self.switchConstraintLock(self.variableChart.innerSpacing)

        self.Solve()

        self.switchConstraintLock(self.variableChart.width, widthLock)
        self.switchConstraintLock(self.variableChart.spacing, spacingLock)
        self.switchConstraintLock(self.variableChart.innerSpacing,innerSpacingLock)
        print("--- solver.AddRectangle end ---")
    
    def GetGroupData(self)->list[list[ValueRectangle]]:
        return self.GetBarData() # pyright: ignore[reportReturnType]
    
    def GetRectangleDataAsList(self)->list[ValueRectangle]:
        return self.GetBarDataAsList()