from .variablechart import VariableChart,MINIMAL_WIDTH
from kiwiplots.chartelements.rectanglegroups import *
from kiwiplots.chartelements.buckets import *
from .variable_rectanglegroupchart import VariableRectangleGroupChart
import warnings
from kiwiplots.utils import MethodWithoutEffectWarning

class VariableHistogram(VariableRectangleGroupChart):
    """VariableChart implementation for histograms.

    Manages a single group of buckets whose widths are proportional to their
    interval lengths. Provides methods for appending new intervals at runtime.

    Attributes:
        shortestInterval (tuple[float, float]): The interval with the smallest width, used for scaling.
        groups (list[VariableBucketGroup]): Contains the single bucket group for this histogram.
        leftRectangleXCoordinateConstraint (Constraint): Pins the group's left edge to the origin.
        leftRectangleYCoordinateConstraint (Constraint): Pins the group's bottom to the origin Y.
    """
    def __init__(self, intervals : list[tuple[float,float]], widthScales: list[float]):
        """Initializes the histogram with interval definitions and width scales.

        Args:
            intervals (list[tuple[float, float]]): Start/end pairs for each bucket interval.
            widthScales (list[float]): Relative width scale for each bucket.
        """
        
        super().__init__()

        self.shortestInterval : tuple[float,float] = min(intervals, key= lambda i: abs(i[1]-i[0]))
        
        self.groups : list[VariableBucketGroup] = [VariableBucketGroup(bucketWidth=self.width,
                                                               innerSpacing=self.innerSpacing,
                                                               intervals=intervals,
                                                               widthScales=widthScales)]

        self._createGroupSpacingConstraints()

        self.leftRectangleXCoordinateConstraint : Constraint = (self.groups[0].leftMostX == self.origin.X + self.spacing) | "required"
        self.leftRectangleYCoordinateConstraint : Constraint = (self.groups[0].bottomY == self.origin.Y) | "required"
    

    def ChangeColor(self, groupIndex: int, bucketIndex: int, color: Union[str,int]):
        """Changes the color of the specified bucket.

        Args:
            groupIndex (int): Must be 0 (histogram has a single group).
            bucketIndex (int): Index of the bucket within the group.
            color (Union[str, int]): New color value.
        """
        if groupIndex !=0:
            raise ValueError()
        self.groups[0].ChangeColor(bucketIndex, color)
     
    def _createGroupSpacingConstraints(self):
        """No-op — histogram has a single group so no inter-group spacing constraints are needed."""
        return
        self.group.SetSpacingConstraint((self.groups[index-1].rightMostX + self.spacing == self.groups[index].leftMostX) | "required")
    
    def Value(self):
        """Returns the resolved data for all histogram buckets."""
        return self.groups[0].Value()
    
    def _getGroupConstraints(self) -> list[Constraint]:
        """Returns all constraints from the histogram's single bucket group."""
        return self.groups[0].GetAllConstraints()
    
    def _getSpacingConstraints(self)-> list[Constraint]:
        """Returns constraints that enforce minimum width and non-negative spacing."""
        global MINIMAL_WIDTH
        return [(self.width >= MINIMAL_WIDTH) | "required", (self.spacing >= 0) | "required", (self.innerSpacing >= 0) | "required"]
    
    def _getVerticalGroupAligmentConstraints(self) -> list[Constraint]:
        """Returns a constraint that aligns the bucket group bottom to the origin Y."""
        return [(self.origin.Y == self.groups[0].bottomY) | "required"]
    
    def _getOriginConstraints(self) -> list[Constraint]:
        """Returns constraints that pin the first bucket to the chart origin."""
        return [self.leftRectangleXCoordinateConstraint,self.leftRectangleYCoordinateConstraint]

    def GetAllConstraints(self)-> list[Constraint]:
        """Returns all constraints for the histogram layout."""
        return self._getGroupConstraints() + self._getSpacingConstraints()+ self._getVerticalGroupAligmentConstraints() + self._getOriginConstraints()
    
    def GetHeightVariable(self, groupIndex: int, bucketIndex : int) -> Variable:
        """Returns the kiwisolver height variable for the specified bucket.

        Args:
            groupIndex (int): Must be 0 (histogram has a single group).
            bucketIndex (int): Index of the bucket.
        """
        if groupIndex !=0:
            raise ValueError()
        return self.groups[0].GetHeightVariable(bucketIndex)
    
    def AddBucket(self,widthScale: float, intervalStart: float, intervalEnd: float):
        """Appends a new bucket to the histogram.

        Args:
            widthScale (float): Relative width scale for the new bucket.
            intervalStart (float): Start of the new interval.
            intervalEnd (float): End of the new interval.

        Returns:
            tuple: The height variable, list of constraints to add, and list of constraints to remove.
        """
        constraintsToRemove = [] 
        constraintsToAdd = []
        self.shortestInterval = self.shortestInterval if abs(intervalEnd - intervalStart) >= abs(self.shortestInterval[1]-self.shortestInterval[0]) else (intervalStart,intervalEnd)
        newBucket = self.groups[0].AddBucket((intervalStart,intervalEnd),widthScale)
        constraintsToAdd.extend(newBucket.GetAllConstraints())
        constraintsToAdd.append((self.groups[0].rectangles[0].leftBottom.Y == newBucket.leftBottom.Y)|"required")
        return newBucket.height, constraintsToAdd, constraintsToRemove
    
    def GetName(self, groupIndex: int, rectangleIndex: int) -> str:
        """Returns the display name of the specified bucket.

        Args:
            groupIndex (int): Must be 0 (histogram has a single group).
            rectangleIndex (int): Index of the bucket.
        """
        if groupIndex != 0:
            raise ValueError()
        return self.groups[0].rectangles[rectangleIndex].GetName()
    
    def ChangeName(self, groupIndex: int, rectangleIndex: int, name: str):
        """Has no effect — histogram bucket names cannot be changed."""
        warnings.warn(f"Method {type(VariableHistogram).__name__}.CahngeName has no effect by design.",category=MethodWithoutEffectWarning,stacklevel=2)
        return
    
    def GetShortestInterval(self)->tuple[float,float]:
        """Returns the interval with the smallest width in the histogram."""
        return self.shortestInterval
    