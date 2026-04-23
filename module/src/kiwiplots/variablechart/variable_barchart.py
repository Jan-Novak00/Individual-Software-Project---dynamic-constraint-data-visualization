from .variablechart import VariableChart, MINIMAL_WIDTH
from kiwisolver import Variable, Constraint
from kiwiplots.chartelements import VariableRectangle, VariableRectangleGroup, ValueRectangle, VariableBarGroup
from kiwiplots.plotui.uiconstants import DEFAULT_COLOR
from typing import Union

class VariableBarChart(VariableChart):
    """
    VariableChart version for bar chart and histogram
    """
    def __init__(self, rectangleNames : list[list[str]]):
        
        super().__init__()

        self.innerSpacing = Variable("global_inner_spacing")
        
        self.groups : list[VariableBarGroup] = [VariableBarGroup(rectangleWidth=self.width,
                                                                             innerSpacing = self.innerSpacing, 
                                                                             names        = rectangleNames[i] if rectangleNames is not None else [], 
                                                                             color        = DEFAULT_COLOR) 
                                                                             for i, name in enumerate(rectangleNames)]
        self._createGroupSpacingConstraints()

        self.leftRectangleXCoordinateConstraint : Constraint = (self.groups[0].leftMostX == self.origin.X + self.spacing) | "required"
        self.leftRectangleYCoordinateConstraint : Constraint = (self.groups[0].bottomY == self.origin.Y) | "required"
    
    def SetIntervalValues(self, intervals: list[tuple[float,float]]):
        """
        Sets interval scales for histogram.
        """
        firstGroup = self.groups[0]
        for index, rec in enumerate(firstGroup.rectangles):
            interval = intervals[index]
            rec.leftBottom.secondaryName, rec.rightTop.secondaryName = f"{interval[0]}", f"{interval[1]}"

    def ChangeColor(self, groupIndex: int, rectangleIndex: int, color: Union[str,int]):
        self.groups[groupIndex].ChangeColor(rectangleIndex, color)
    
    def ChangeName(self, groupIndex: int, rectangleIndex: int, name: str):
        self.groups[groupIndex].ChangeName(rectangleIndex,name)
     
    def _createGroupSpacingConstraints(self):
        for index in range(1,len(self.groups)):
            self.groups[index].SetSpacingConstraint((self.groups[index-1].rightMostX + self.spacing == self.groups[index].leftMostX) | "required")
    
    def Value(self):
        return [group.Value() for group in self.groups]
    
    def _getGroupConstraints(self) -> list[Constraint]:
        result = []
        for group in self.groups:
            result.extend(group.GetAllConstraints())
        return result 
    
    def _getSpacingConstraints(self)-> list[Constraint]:
        global MINIMAL_WIDTH
        return [(self.width >= MINIMAL_WIDTH) | "required", (self.spacing >= 0) | "required", (self.innerSpacing >= 0) | "required"]
    
    def _getVerticalGroupAligmentConstraints(self) -> list[Constraint]:
        return [(self.origin.Y == self.groups[i].bottomY) | "required" for i in range(1,len(self.groups))]
    
    def _getOriginConstraints(self) -> list[Constraint]:
        return [self.leftRectangleXCoordinateConstraint,self.leftRectangleYCoordinateConstraint]

    def GetAllConstraints(self)-> list[Constraint]:
        return self._getGroupConstraints() + self._getSpacingConstraints()+ self._getVerticalGroupAligmentConstraints() + self._getOriginConstraints()
    
    def GetName(self, groupIndex : int, rectangleIndex : int):
        return self.groups[groupIndex].GetName(rectangleIndex)
    
    def GetHeightVariable(self,groupIndex : int, rectangleIndex : int) -> Variable:
        return self.groups[groupIndex].GetHeightVariable(rectangleIndex)
    
    def AddGroup(self,firstRectangleName : str):
        lastGroup = self.groups[-1] #TODO first one
        newGroup = VariableBarGroup(self.width, self.innerSpacing, [firstRectangleName])
        self.groups.append(newGroup)
        newGroup.SetSpacingConstraint((lastGroup.rightMostX + self.spacing == newGroup.leftMostX) | "required")
        return newGroup, newGroup.GetAllConstraints() + [(self.origin.Y == newGroup.bottomY) | "required"]

    def AddRectangle(self,name: str, groupIndex: int):
        currentGroup = self.groups[groupIndex]
        nextGroup = self.groups[groupIndex + 1] if groupIndex + 1 < len(self.groups) else None 
        constraintsToRemove = [nextGroup.spacingConstraint] if nextGroup != None else [] #TODO better system
        constraintsToAdd = []
        currentGroup.AddBar(name)
        if nextGroup != None:
            nextGroup.SetSpacingConstraint((currentGroup.rightMostX + self.spacing == nextGroup.leftMostX)|"required")
            constraintsToAdd.append(nextGroup.spacingConstraint)
        newRec = currentGroup.rectangles[-1]
        constraintsToAdd.extend(newRec.GetAllConstraints())
        constraintsToAdd.append((currentGroup.rectangles[0].leftBottom.Y == newRec.leftBottom.Y)|"required")
        return newRec.height, constraintsToAdd, constraintsToRemove
    