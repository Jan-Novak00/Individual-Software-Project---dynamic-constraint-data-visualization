from .variablechart import VariableChart,MINIMAL_WIDTH
from kiwiplots.chartelements.rectanglegroups import *
from kiwiplots.chartelements.buckets import *
from .variable_rectanglegroupchart import VariableRectangleGroupChart
import warnings
from kiwiplots.utils import MethodWithoutEffectWarning

class VariableHistogram(VariableRectangleGroupChart):
    def __init__(self, intervals : list[tuple[float,float]], widthScales: list[float]):
        
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
        if groupIndex !=0:
            raise ValueError()
        self.groups[0].ChangeColor(bucketIndex, color)
     
    def _createGroupSpacingConstraints(self):
        return
        self.group.SetSpacingConstraint((self.groups[index-1].rightMostX + self.spacing == self.groups[index].leftMostX) | "required")
    
    def Value(self):
        return self.groups[0].Value()
    
    def _getGroupConstraints(self) -> list[Constraint]:
        return self.groups[0].GetAllConstraints()
    
    def _getSpacingConstraints(self)-> list[Constraint]:
        global MINIMAL_WIDTH
        return [(self.width >= MINIMAL_WIDTH) | "required", (self.spacing >= 0) | "required", (self.innerSpacing >= 0) | "required"]
    
    def _getVerticalGroupAligmentConstraints(self) -> list[Constraint]:
        return [(self.origin.Y == self.groups[0].bottomY) | "required"]
    
    def _getOriginConstraints(self) -> list[Constraint]:
        return [self.leftRectangleXCoordinateConstraint,self.leftRectangleYCoordinateConstraint]

    def GetAllConstraints(self)-> list[Constraint]:
        return self._getGroupConstraints() + self._getSpacingConstraints()+ self._getVerticalGroupAligmentConstraints() + self._getOriginConstraints()
    
    def GetHeightVariable(self, groupIndex: int, bucketIndex : int) -> Variable:
        if groupIndex !=0:
            raise ValueError()
        return self.groups[0].GetHeightVariable(bucketIndex)
    
    def AddBucket(self,widthScale: float, intervalStart: float, intervalEnd: float):
        constraintsToRemove = [] 
        constraintsToAdd = []
        self.shortestInterval = self.shortestInterval if abs(intervalEnd - intervalStart) >= abs(self.shortestInterval[1]-self.shortestInterval[0]) else (intervalStart,intervalEnd)
        newBucket = self.groups[0].AddBucket((intervalStart,intervalEnd),widthScale)
        constraintsToAdd.extend(newBucket.GetAllConstraints())
        constraintsToAdd.append((self.groups[0].rectangles[0].leftBottom.Y == newBucket.leftBottom.Y)|"required")
        return newBucket.height, constraintsToAdd, constraintsToRemove
    
    def GetName(self, groupIndex: int, rectangleIndex: int) -> str:
        if groupIndex != 0:
            raise ValueError()
        return self.groups[0].rectangles[rectangleIndex].GetName()
    
    def ChangeName(self, groupIndex: int, rectangleIndex: int, name: str):
        warnings.warn(f"Method {type(VariableHistogram).__name__}.CahngeName has no effect by design.",category=MethodWithoutEffectWarning,stacklevel=2)
        return
    
    def GetShortestInterval(self)->tuple[float,float]:
        return self.shortestInterval
    