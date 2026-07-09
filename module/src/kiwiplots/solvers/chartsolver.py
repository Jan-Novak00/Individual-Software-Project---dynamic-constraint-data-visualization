from abc import ABC, abstractmethod
from kiwisolver import Solver, Constraint, Variable
from kiwiplots.variablechart import VariableChart

class ChartSolver(ABC):
    """
    Abstract class.
    Encapsulates Solver instance and VariableChart instance.
    Serves as communication layer between UI and constraint system.

    Attributes:
        solve (Solver) : constraint solver instance
        variableChart (VariableChart) : VaraibleChart which is solved by the solver
        data (Any) : data cache. Type depends on the chart type

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
        """Loads edit variables to the solver.
        """
        raise NotImplementedError("Method must be declared in a subclass")

    @abstractmethod
    def _initialSuggest(self):
        """Makes initial suggest to the registered edit variables.
        """
        raise NotImplementedError("Method must be declared in a subclass")

    def _setConstraints(self):
        """Loads constraints of the chart to the solver
        """
        for constriant in self.variableChart.GetAllConstraints():
            if not self.solver.hasConstraint(constriant):
                self.solver.addConstraint(constriant)

    def switchConstraintLock(self, variable : Variable, constraint : Constraint | None = None)->Constraint | None:
        """Utility method for locking and unlocking kiwisolvber variables. Locked variable is se to its value by a required constraint.
        The constraint parameter is set to None, the provided variable is locked and the new constraint is returned.
        If the constraint parameter is not None, given constraint is removed fro mthe solver and None is returned.


        Args:
            variable (Variable): Variable to lock/unlock
            constraint (Constraint | None, optional): If it is None, the variable is locked, a new required constraint is added to the solver and the constraint is returned. If it is not None, then the constraint is removed form the solver. Defaults to None.

        Returns:
            Constraint | None: Either the new required constraint (result of locking) or None (result of unlocking).
        """
        if not constraint:
            newC = (variable == variable.value()) | "required"
            self.solver.addConstraint(newC)
            return newC
        else:
            self.solver.removeConstraint(constraint)
            return None 
    
    def Feed(self, otherSolver: "ChartSolver"):
        """Loads all solutions into another solver. It is expected that the other solver operates above the same data.

        Args:
            otherSolver (ChartSolver): Solver to which the solutions are supposed to be loaded.
        """
        origin = self.GetOrigin()
        otherSolver.ChangeOrigin(origin.X, origin.Y)
        otherSolver.ChangeAxisHeight(self.GetAxisHeight())
        otherSolver.ChangeWidth(self.GetWidth())
        otherSolver.ChangeSpacing(self.GetSpacing())
        otherSolver.Solve()

    def Solve(self):
        """
        Updates all variables (performes constraint solving).
        """
        self.solver.updateVariables()
        self.Update()
    
    def Update(self):
        """
        Updates cached data.
        """
        self.data = self.variableChart.Value()
    
    def GetOrigin(self):
        """Origin value getter

        Returns:
            ValuePoint2D: origin of the chart
        """
        return self.variableChart.GetOrigin()

    def GetSpacing(self):
        """Spacing value getter

        Returns:
            float: spacing of elements
        """
        return self.variableChart.spacing.value()
    
    def GetWidth(self):
        """Width value getter

        Returns:
            float: value of the global width
        """
        return self.variableChart.width.value()
    
    def GetAxisHeight(self):
        """Value getter for the Y axis height

        Returns:
            float: Y axis height
        """
        return self.variableChart.yAxisHeight.value()
    
    def ChangeOrigin(self, newX: float, newY: float):
        """Changes the position of the origin.

        Args:
            newX (float): new X coordinate
            newY (float): new Y coordinate
        """
        self.solver.suggestValue(self.variableChart.origin.X, newX)
        self.solver.suggestValue(self.variableChart.origin.Y, newY)
        self.Solve()
    
    def ChangeAxisHeight(self, newHeight : float):
        """Changes height of the y axis

        Args:
            newHeight (float): new axis height
        """
        self.solver.suggestValue(self.variableChart.yAxisHeight, newHeight)
        self.Solve()
    
    def ChangeWidth(self, width : float):
        """Changes global element width.

        Args:
            width (float): new element width
        """
        self.solver.suggestValue(self.variableChart.width, width)
        self.Solve()
    
    def ChangeSpacing(self, spacing : float):
        """Changes global element spacing

        Args:
            spacing (float): new elment spacing
        """
        self.solver.suggestValue(self.variableChart.spacing, spacing)
        self.Solve()