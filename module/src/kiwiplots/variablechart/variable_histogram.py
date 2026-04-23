from .variablechart import VariableChart,MINIMAL_WIDTH
from .variable_barchart import VariableBarChart
from kiwiplots.chartelements.rectanglegroups import *
from kiwiplots.chartelements.buckets import *

class VariableHistogram(VariableChart):
    def __init__(self, intervals : list[tuple[float,float]], widthScales: list[float]):
        
        super().__init__()

        self.innerSpacing = Variable("global_inner_spacing")
        
        self.group : VariableBucketGroup = VariableBucketGroup(bucketWidth=self.width,
                                                               innerSpacing=self.innerSpacing,
                                                               intervals=intervals,
                                                               widthScales=widthScales)

        self._createGroupSpacingConstraints()

        self.leftRectangleXCoordinateConstraint : Constraint = (self.group.leftMostX == self.origin.X + self.spacing) | "required"
        self.leftRectangleYCoordinateConstraint : Constraint = (self.group.bottomY == self.origin.Y) | "required"
    
    def SetIntervalValues(self, intervals: list[tuple[float,float]]):
        """
        Sets interval scales for histogram.
        """
        for index, rec in enumerate(self.group.rectangles):
            interval = intervals[index]
            rec.leftBottom.secondaryName, rec.rightTop.secondaryName = f"{interval[0]}", f"{interval[1]}"

    def ChangeColor(self, bucketIndex: int, color: Union[str,int]):
        self.group.ChangeColor(bucketIndex, color)
    
     
    def _createGroupSpacingConstraints(self):
        return
        self.group.SetSpacingConstraint((self.groups[index-1].rightMostX + self.spacing == self.groups[index].leftMostX) | "required")
    
    def Value(self):
        return self.group.Value()
    
    def _getGroupConstraints(self) -> list[Constraint]:
        return self.group.GetAllConstraints()
    
    def _getSpacingConstraints(self)-> list[Constraint]:
        global MINIMAL_WIDTH
        return [(self.width >= MINIMAL_WIDTH) | "required", (self.spacing >= 0) | "required", (self.innerSpacing >= 0) | "required"]
    
    def _getVerticalGroupAligmentConstraints(self) -> list[Constraint]:
        return [(self.origin.Y == self.group.bottomY) | "required"]
    
    def _getOriginConstraints(self) -> list[Constraint]:
        return [self.leftRectangleXCoordinateConstraint,self.leftRectangleYCoordinateConstraint]

    def GetAllConstraints(self)-> list[Constraint]:
        return self._getGroupConstraints() + self._getSpacingConstraints()+ self._getVerticalGroupAligmentConstraints() + self._getOriginConstraints()
    
    
    def GetHeightVariable(self,bucketIndex : int) -> Variable:
        return self.group.GetHeightVariable(bucketIndex)
    
    def AddRectangleAsInterval(self,widthScale: float, intervalStart: float, intervalEnd: float):
        constraintsToRemove = [] 
        constraintsToAdd = []
        newBucket = self.group.AddBucket((intervalStart,intervalEnd),widthScale)
        constraintsToAdd.extend(newBucket.GetAllConstraints())
        constraintsToAdd.append((self.group.rectangles[0].leftBottom.Y == newBucket.leftBottom.Y)|"required")
        return newBucket.height, constraintsToAdd, constraintsToRemove