from .chartsolver import ChartSolver
from kiwiplots.variablechart import VariableRectangleGroupChart
from abc import ABC, abstractmethod
from kiwiplots.chartelements import ValueRectangle

class RectangleSolver(ChartSolver,ABC):
    """
    ChartSolver version for bar chart and histogram.
    """
    def __init__(self, variableChart : VariableRectangleGroupChart, width: int, spacing: int, innerSpacing: int, xCoordinate: int = 0, yCoordinate: int = 0):
        self.initialWidth = width
        self.initialSpacing = spacing
        self.initialInnerSpacing = innerSpacing
        self.initialxCoordinate = xCoordinate
        self.initialyCoordinate = yCoordinate

        super().__init__(variableChart)
        
        self.variableChart : VariableRectangleGroupChart = self.variableChart

        self.lockedRectangles: set[tuple[int,int]] = set()

    def _setConstraints(self):
        barChartConstraints = set(self.variableChart.GetAllConstraints())
        for constraint in barChartConstraints:
            self.solver.addConstraint(constraint)
    
    def _addEditVariables(self):
        self.solver.addEditVariable(self.variableChart.width, "strong")
        self.solver.addEditVariable(self.variableChart.spacing, "strong")
        self.solver.addEditVariable(self.variableChart.innerSpacing, "strong")
        
        assert self.variableChart.groups is not None
        for group in self.variableChart.groups:
            for rec in group:
                self.solver.addEditVariable(rec.height, "strong")
        
        self.solver.addEditVariable(self.variableChart.origin.X, "strong")
        self.solver.addEditVariable(self.variableChart.origin.Y, "strong")
        self.solver.addEditVariable(self.variableChart.yAxisHeight, "strong")
    
    def _initialSuggest(self):
        assert self.variableChart.groups is not None
        self.solver.suggestValue(self.variableChart.origin.X, self.initialxCoordinate)
        self.solver.suggestValue(self.variableChart.origin.Y, self.initialyCoordinate)
        self.solver.suggestValue(self.variableChart.innerSpacing, self.initialInnerSpacing)
        self.solver.suggestValue(self.variableChart.spacing,self.initialSpacing)
        self.solver.suggestValue(self.variableChart.width,self.initialWidth)

        self._suggestYAxisHeight()
        self._suggestHeights()
    
    @abstractmethod
    def _suggestHeights(self):
        return
    
    @abstractmethod
    def _suggestYAxisHeight(self):
        return
    
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
        
    
    def Feed(self, otherSolver: "RectangleSolver"):
        print("feeding...")
        otherSolver.ChangeInnerSpacing(self.GetInnerSpacing())
        super().Feed(otherSolver)


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

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) 
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock) 
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)  
        self.switchConstraintLock(self.variableChart.width, widthConstrLock) 
    
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
        assert self.variableChart.groups is not None
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

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock) 
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock)
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)
        self._refreshSuggestions()

    
    def ChangeSpacingX(self,groupIndex: int, rectangleIndex : int, newX : float):
        assert self.variableChart.groups is not None
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

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock)
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock)
        self.switchConstraintLock(self.variableChart.width, widthConstrLock)
        self._refreshSuggestions()
    
    def ChangeInnerSpacingX(self,groupIndex: int, rectangleIndex : int, newX : float):
        assert self.variableChart.groups is not None
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

        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock)
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)
        self.switchConstraintLock(self.variableChart.width, widthConstrLock)
        self._refreshSuggestions()
    
    def ChangeOrigin(self, newX: int, newY: int):
        innerSpacingConstrLock = self.switchConstraintLock(self.variableChart.innerSpacing)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)
        super().ChangeOrigin(newX, newY)
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock) 
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock) 
        self.switchConstraintLock(self.variableChart.width, widthConstrLock)
        self._refreshSuggestions()
    
    def ChangeAxisHeight(self, newHeight: int):
        innerSpacingConstrLock = self.switchConstraintLock(self.variableChart.innerSpacing)
        spacingConstrLock = self.switchConstraintLock(self.variableChart.spacing)
        widthConstrLock = self.switchConstraintLock(self.variableChart.width)
        originConstrLock = self.switchConstraintLock(self.variableChart.origin.X)
        super().ChangeAxisHeight(newHeight)
        self.switchConstraintLock(self.variableChart.innerSpacing, innerSpacingConstrLock)
        self.switchConstraintLock(self.variableChart.spacing, spacingConstrLock)
        self.switchConstraintLock(self.variableChart.width, widthConstrLock)
        self.switchConstraintLock(self.variableChart.origin.X, originConstrLock)
        self._refreshSuggestions()
    
    @abstractmethod
    def GetGroupData(self)->list[list[ValueRectangle]]:
        raise NotImplementedError()
    
    @abstractmethod
    def GetRectangleDataAsList(self)->list[ValueRectangle]:
        raise NotImplementedError()
    