from abc import ABC, abstractmethod
from kiwisolver import Solver, Constraint, Variable
from kiwiplots.variablechart import VariableChart

class ChartSolver(ABC):
    """
    Encapsulates Solver instance and VariableChart instance.
    """
    def __init__(self, chart : VariableChart):
        self.solver : Solver = Solver()
        self.variableChart : VariableChart = chart
        self.data = None
        self._setConstraints()
        self._addEditVariables()
        self._initialSuggest()
        self.Solve()
    
    @abstractmethod
    def _addEditVariables(self):
        raise NotImplementedError("Method must be declared in subclass")

    @abstractmethod
    def _initialSuggest(self):
        raise NotImplementedError("Method must be declared in subclass")

    def _setConstraints(self):
        for constriant in self.variableChart.GetAllConstraints():
            if not self.solver.hasConstraint(constriant):
                self.solver.addConstraint(constriant)

    def switchConstraintLock(self, variable : Variable, constraint : Constraint | None = None)->Constraint | None:
        if not constraint:
            newC = (variable == variable.value()) | "required"
            self.solver.addConstraint(newC)
            return newC
        else:
            self.solver.removeConstraint(constraint)
            return None 
    
    def Feed(self, otherSolver: "ChartSolver"):
        origin = self.GetOrigin()
        otherSolver.ChangeOrigin(origin.X, origin.Y)
        otherSolver.ChangeAxisHeight(self.GetAxisHeight())
        otherSolver.ChangeWidth(self.GetWidth())
        otherSolver.ChangeSpacing(self.GetSpacing())
        otherSolver.Solve()

    def Solve(self):
        """
        Updates all variables
        """
        self.solver.updateVariables()
        self.Update()
    
    def Update(self):
        """
        Updates cached data
        """
        self.data = self.variableChart.Value()
    
    def GetOrigin(self):
        return self.variableChart.GetOrigin()

    def GetSpacing(self):
        return self.variableChart.spacing.value()
    
    def GetWidth(self):
        return self.variableChart.width.value()
    
    def GetAxisHeight(self):
        return self.variableChart.yAxisHeight.value()
    
    def ChangeOrigin(self, newX: float, newY: float):
        self.solver.suggestValue(self.variableChart.origin.X, newX)
        self.solver.suggestValue(self.variableChart.origin.Y, newY)
        self.Solve()
    
    def ChangeAxisHeight(self, newHeight : float):
        self.solver.suggestValue(self.variableChart.yAxisHeight, newHeight)
        self.Solve()
    
    def ChangeWidth(self, width : float):
        self.solver.suggestValue(self.variableChart.width, width)
        self.Solve()
    
    def ChangeSpacing(self, spacing : float):
        self.solver.suggestValue(self.variableChart.spacing, spacing)
        self.Solve()