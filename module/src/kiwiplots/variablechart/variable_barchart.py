from .variablechart import VariableChart, MINIMAL_WIDTH
from kiwisolver import Variable, Constraint
from kiwiplots.chartelements import VariableRectangle, VariableRectangleGroup, ValueRectangle, VariableBarGroup
from kiwiplots.plotui.uiconstants import DEFAULT_COLOR
from typing import Union
from .variable_rectanglegroupchart import VariableRectangleGroupChart

class VariableBarChart(VariableRectangleGroupChart):
    """VariableChart implementation for bar charts.

    Manages groups of bar rectangles with shared width, spacing, and inner spacing
    variables, and provides methods for adding bars and groups at runtime.

    Attributes:
        innerSpacing (Variable): Spacing between rectangles within a single group.
        groups (list[VariableBarGroup]): The bar groups that make up the chart.
        leftRectangleXCoordinateConstraint (Constraint): Pins the first group's left edge to the origin.
        leftRectangleYCoordinateConstraint (Constraint): Pins all group bottoms to the origin Y.
    """
    def __init__(self, rectangleNames : list[list[str]]):
        """Initializes the bar chart with the given rectangle name groups.

        Args:
            rectangleNames (list[list[str]]): Names for rectangles in each group.
        """
        
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
    

    def ChangeColor(self, groupIndex: int, rectangleIndex: int, color: Union[str,int]):
        """Changes the color of the specified bar rectangle.

        Args:
            groupIndex (int): Index of the bar group.
            rectangleIndex (int): Index of the rectangle within the group.
            color (Union[str, int]): New color
        """
        self.groups[groupIndex].ChangeColor(rectangleIndex, color)
    
    def ChangeName(self, groupIndex: int, rectangleIndex: int, name: str):
        """Changes the name of the specified bar rectangle.

        Args:
            groupIndex (int): Index of the bar group.
            rectangleIndex (int): Index of the rectangle within the group.
            name (str): New name string.
        """
        self.groups[groupIndex].ChangeName(rectangleIndex,name)
     
    def _createGroupSpacingConstraints(self):
        for index in range(1,len(self.groups)):
            self.groups[index].SetSpacingConstraint((self.groups[index-1].rightMostX + self.spacing == self.groups[index].leftMostX) | "required")
    
    def Value(self):
        """Returns rectangle data for all bar groups."""
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
        """Returns all constraints for the bar chart layout."""
        return self._getGroupConstraints() + self._getSpacingConstraints()+ self._getVerticalGroupAligmentConstraints() + self._getOriginConstraints()
    
    def GetName(self, groupIndex : int, rectangleIndex : int):
        """Returns the display name of the specified bar rectangle."""
        return self.groups[groupIndex].GetName(rectangleIndex)
    
    def GetHeightVariable(self,groupIndex : int, rectangleIndex : int) -> Variable:
        """Returns the kiwisolver height variable for the specified bar rectangle."""
        return self.groups[groupIndex].GetHeightVariable(rectangleIndex)
    
    def AddBarGroup(self,firstRectangleName : str):
        """Appends a new bar group with a single rectangle to the chart.

        Args:
            firstRectangleName (str): Name for the first rectangle in the new group.

        Returns:
            tuple: The new VariableBarGroup and the list of constraints to add.
        """
        lastGroup = self.groups[-1]
        newGroup = VariableBarGroup(self.width, self.innerSpacing, [firstRectangleName])
        self.groups.append(newGroup)
        newGroup.SetSpacingConstraint((lastGroup.rightMostX + self.spacing == newGroup.leftMostX) | "required")
        return newGroup, newGroup.GetAllConstraints() + [(self.origin.Y == newGroup.bottomY) | "required"]

    def AddBar(self,name: str, groupIndex: int):
        """Appends a new bar rectangle to an existing group.

        Args:
            name (str): Name for the new rectangle.
            groupIndex (int): Index of the group to add the rectangle to.

        Returns:
            tuple: The height variable, list of constraints to add, and list of constraints to remove.
        """
        currentGroup = self.groups[groupIndex]
        nextGroup = self.groups[groupIndex + 1] if groupIndex + 1 < len(self.groups) else None 
        constraintsToRemove = [nextGroup.spacingConstraint] if nextGroup != None else []
        constraintsToAdd = []
        currentGroup.AddBar(name)
        if nextGroup != None:
            nextGroup.SetSpacingConstraint((currentGroup.rightMostX + self.spacing == nextGroup.leftMostX)|"required")
            constraintsToAdd.append(nextGroup.spacingConstraint)
        newRec = currentGroup.rectangles[-1]
        constraintsToAdd.extend(newRec.GetAllConstraints())
        constraintsToAdd.append((currentGroup.rectangles[0].leftBottom.Y == newRec.leftBottom.Y)|"required")
        return newRec.height, constraintsToAdd, constraintsToRemove
    