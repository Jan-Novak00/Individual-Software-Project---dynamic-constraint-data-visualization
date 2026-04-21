from .chartsolver import ChartSolver
from kiwiplots.variablechart import VariableBarChart, VariableChart
from typing import Union
from kiwiplots.chartelements import ValueRectangle, VariableRectangle

class BarChartSolver(ChartSolver):
    """
    ChartSolver version for bar chart and histogram.
    """
    def __init__(self, variableChart : VariableBarChart, width: int, initialHeights: Union[list[float], list[list[float]]], spacing: int, innerSpacing: int, xCoordinate: int = 0, yCoordinate: int = 0):
        self.initialHeights = initialHeights
        self.initialWidth = width
        self.initialSpacing = spacing
        self.initialInnerSpacing = innerSpacing
        self.initialxCoordinate = xCoordinate
        self.initialyCoordinate = yCoordinate

        super().__init__(variableChart)
        
        self.variableChart : VariableBarChart = self.variableChart

        self.lockedRectangles: set[tuple[int,int]] = set()

    def _setConstraints(self):
        barChartConstraints = set(self.variableChart.GetAllConstraints())
        for constraint in barChartConstraints:
            self.solver.addConstraint(constraint)
    
    def _addEditVariables(self):
        self.solver.addEditVariable(self.variableChart.width, "strong")
        self.solver.addEditVariable(self.variableChart.spacing, "strong")
        self.solver.addEditVariable(self.variableChart.innerSpacing, "strong")
        for group in self.variableChart.groups:
            for rec in group:
                self.solver.addEditVariable(rec.height, "strong")
        
        self.solver.addEditVariable(self.variableChart.origin.X, "strong")
        self.solver.addEditVariable(self.variableChart.origin.Y, "strong")
        self.solver.addEditVariable(self.variableChart.yAxisHeight, "strong")
    
    def _initialSuggest(self):
        self.solver.suggestValue(self.variableChart.yAxisHeight, max(max(group) for group in self.initialHeights)+10) # pyright: ignore[reportArgumentType]
        self.solver.suggestValue(self.variableChart.origin.X, self.initialxCoordinate)
        self.solver.suggestValue(self.variableChart.origin.Y, self.initialyCoordinate)
        self.solver.suggestValue(self.variableChart.innerSpacing, self.initialInnerSpacing)
        self.solver.suggestValue(self.variableChart.spacing,self.initialSpacing)
        self.solver.suggestValue(self.variableChart.width,self.initialWidth)
        for ig in range(len(self.variableChart.groups)):
            group = self.variableChart.groups[ig]
            for ir, rec in enumerate(group):
                self.solver.suggestValue(rec.height,self.initialHeights[ig][ir]) # pyright: ignore[reportIndexIssue] #TODO type safety
    
    def _refreshSuggestions(self):
        self.solver.suggestValue(self.variableChart.width, self.variableChart.width.value())
        self.solver.suggestValue(self.variableChart.spacing, self.variableChart.spacing.value())
        self.solver.suggestValue(self.variableChart.innerSpacing, self.variableChart.innerSpacing.value())
        self.solver.suggestValue(self.variableChart.origin.X, self.variableChart.origin.X.value())
    
    def SwitchRectangleLock(self, groupIndex: int, recIndex: int) -> bool:
        if (groupIndex,recIndex) in self.lockedRectangles:
            self.lockedRectangles.remove((groupIndex,recIndex))
            return False
        else:
            self.lockedRectangles.add((groupIndex,recIndex))
            return True
        
    def SetIntervalValues(self, intervals: list[tuple[float,float]]):
        self.variableChart.SetIntervalValues(intervals)
    
    def Feed(self, otherSolver: "BarChartSolver"):
        print("feeding...")
        otherSolver.ChangeInnerSpacing(self.GetInnerSpacing())
        super().Feed(otherSolver)

    def GetRectangleData(self):
        return self.data
    
    def GetRectangleDataAsList(self) -> list[ValueRectangle]:
        result = []
        data = self.GetRectangleData()
        for group in data: # pyright: ignore[reportOptionalIterable]
            result.extend(group)
        return result

    def GetInnerSpacing(self):
        return self.variableChart.innerSpacing.value()
    
    def GetName(self, groupIndex: int, rectangleIndex: int):
        return self.variableChart.GetName(groupIndex, rectangleIndex)
    
    def ChangeHeight(self, groupIndex: int, rectangleIndex: int, newHeight: int):
        if (groupIndex, rectangleIndex) in self.lockedRectangles:
            return
        self.solver.suggestValue(self.variableChart.GetHeightVariable(groupIndex, rectangleIndex), newHeight)
        
        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        innerSpacingConstrLock = self.switchConstraintLock(self.variableChart.innerSpacing)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
    
    def ChangeInnerSpacing(self, newInnerSpacing: float):
        self.solver.suggestValue(self.variableChart.innerSpacing, newInnerSpacing)
        self.Solve()

    def ChangeColor(self, groupIndex: int, rectangleIndex: int, newColor: str):
        self.variableChart.ChangeColor(groupIndex,rectangleIndex, newColor)
        self.Update()
    
    def ChangeName(self,groupIndex: int, rectangleIndex: int, newName: str):
        self.variableChart.ChangeName(groupIndex,rectangleIndex, newName)
        self.Update()
    
    def ChangeWidthX(self,groupIndex: int, rectangleIndex : int, newX : float):
        var = self.variableChart.groups[groupIndex].rectangles[rectangleIndex].rightTop.X
        if self.solver.hasEditVariable(var):
            self.solver.removeEditVariable(var)
        self.solver.addEditVariable(var, 1e+8)
        self.solver.suggestValue(var,newX)

        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        innerSpacingConstrLock = self.switchConstraintLock(self.variableChart.innerSpacing)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)

        self.Solve()
        self.solver.removeEditVariable(var)

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()

    
    def ChangeSpacingX(self,groupIndex: int, rectangleIndex : int, newX : float):
        var = self.variableChart.groups[groupIndex].rectangles[rectangleIndex].leftBottom.X
        if self.solver.hasEditVariable(var):
            self.solver.removeEditVariable(var)
        self.solver.addEditVariable(var, 1e+8)
        self.solver.suggestValue(var,newX)

        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        innerSpacingConstrLock = self.switchConstraintLock(self.variableChart.innerSpacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()
        self.solver.removeEditVariable(var)

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()
    
    def ChangeInnerSpacingX(self,groupIndex: int, rectangleIndex : int, newX : float):
        var = self.variableChart.groups[groupIndex].rectangles[rectangleIndex].leftBottom.X
        if self.solver.hasEditVariable(var):
            self.solver.removeEditVariable(var)
        self.solver.addEditVariable(var, 1e+8)
        self.solver.suggestValue(var,newX)

        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)

        self.Solve()
        self.solver.removeEditVariable(var)

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)  # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()
    
    def ChangeOrigin(self, newX: int, newY: int):
        innerSpacingConstrLock = self.switchConstraintLock(self.variableChart.innerSpacing)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)
        super().ChangeOrigin(newX, newY)
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()
    
    def ChangeAxisHeight(self, newHeight: int):
        innerSpacingConstrLock = self.switchConstraintLock(self.variableChart.innerSpacing)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)
        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        super().ChangeAxisHeight(newHeight)
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) # pyright: ignore[reportArgumentType]
        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) # pyright: ignore[reportArgumentType]
        self._refreshSuggestions()
    
    def AddGroup(self, firstRectangleName: str, firstRectangleHeight: float):
        print("--- solver.AddGroup method start ---")
        newGroup, newConstraints = self.variableChart.AddGroup(firstRectangleName=firstRectangleName)
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
    
    def AddRectangle(self, name: str, groupIndex: int, recHeight: float):
        print("--- solver.AddRectangle start ---")
        height, constraintsToAdd, constraintsToRemove = self.variableChart.AddRectangle(groupIndex=groupIndex,name=name)
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