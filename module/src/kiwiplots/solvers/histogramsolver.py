from .chartsolver import ChartSolver
from kiwiplots.variablechart import VariableBarChart, VariableChart
from .barchartsolver import BarChartSolver
from kiwisolver import Solver, Constraint
from kiwiplots.variablechart import VariableRectangleGroupChart, VariableHistogram
from .rectanglesolver import RectangleSolver
from kiwiplots.chartelements import ValueRectangle, ValueBucket
from kiwiplots.utils import inheritdocstring

class HistogramSolver(RectangleSolver):
    """
    ChartSolver version for histogram.
    Manages constraint solving for histogram charts.
    """
    def __init__(self, variableChart : VariableHistogram, width: int, initialHeights: list[float], padding: int,  xCoordinate: int = 0, yCoordinate: int = 0):
        self.initialHeights = initialHeights
        
        super().__init__(variableChart=variableChart,
                         width=width,
                         spacing=padding,
                         innerSpacing=0,
                         xCoordinate=xCoordinate,
                         yCoordinate=yCoordinate)
        
        self.variableChart : VariableHistogram = self.variableChart
    
    @inheritdocstring(RectangleSolver._suggestHeights)
    def _suggestHeights(self):
        for i in range(len(self.initialHeights)):
            self.solver.suggestValue(self.variableChart.groups[0].rectangles[i].height, self.initialHeights[i])
    

    @inheritdocstring(RectangleSolver._suggestYAxisHeight)
    def _suggestYAxisHeight(self):
        self.solver.suggestValue(self.variableChart.yAxisHeight, max(i for i in self.initialHeights)+10)

    def SwitchRectangleLock(self, groupIndex: int, recIndex: int) -> bool:
        """Locks or unlocks a bucket from being edited. Histogram only has one group, so groupIndex must be 0.

        Args:
            groupIndex (int): Index of the group (must be 0 for histogram)
            recIndex (int): Index of the bucket within the group

        Returns:
            bool: True if the method call has locked the bucket, False if unlocked.

        Raises:
            ValueError: If groupIndex is not 0.
        """
        if groupIndex != 0:
            raise ValueError()
        return super().SwitchRectangleLock(groupIndex,recIndex)
    
    def SwitchBucketLock(self, index : int)->bool:
        """Locks or unlocks a bucket from being edited.

        Args:
            index (int): Index of the bucket

        Returns:
            bool: True if the method call has locked the bucket, False if unlocked.
        """
        return self.SwitchRectangleLock(0,index)
    
    def Feed(self, otherSolver: "HistogramSolver"):
        """Loads all solutions into another histogram solver. It is expected that the other solver operates above the same data.

        Args:
            otherSolver (HistogramSolver): Histogram solver to which the solutions are supposed to be loaded.
        """
        ChartSolver.Feed(self,otherSolver)

    def GetBucketData(self)->list[ValueBucket]:
        """Retrieves the bucket data for the histogram.

        Returns:
            list[ValueBucket]: List of all buckets in the histogram.
        """
        return self.variableChart.Value() # pyright: ignore[reportReturnType]
    
  
    def GetGroupData(self)->list[list[ValueRectangle]]:
        """Retrieves the group data for the histogram. Histogram only has one group.

        Returns:
            list[list[ValueRectangle]]: List containing a single group of rectangles representing histogram buckets.
        """
        return [self.GetBucketData()] # pyright: ignore[reportReturnType]
    

    def GetRectangleDataAsList(self)->list[ValueRectangle]:
        """Retrieves all rectangles (buckets) as a flat list.

        Returns:
            list[ValueRectangle]: List of all rectangles representing histogram buckets.
        """
        return self.GetBucketData() # pyright: ignore[reportReturnType]
    
    def AddBucket(self, start: float, end: float, recHeight: float):
        """Appends a new bucket to the histogram.

        Args:
            start (float): Start value of the bucket range
            end (float): End value of the bucket range
            recHeight (float): Initial height of the bucket rectangle
        """
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

   