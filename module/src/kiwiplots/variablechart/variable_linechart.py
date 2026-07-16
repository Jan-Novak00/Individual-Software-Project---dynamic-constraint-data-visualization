from kiwisolver import Constraint, Variable
from kiwiplots.chartelements import VariableLine
from kiwiplots.utils import pairwise
from .variablechart import VariableChart

class VariableLineChart(VariableChart):
    """VariableChart implementation for line charts.

    Manages a sequence of line segments connecting named points, with shared
    width, spacing, and padding variables. Supports adding new points at runtime.

    Attributes:
        pointNames (list[str]): Names of all data points, including the right endpoint.
        lines (list[VariableLine]): The line segments that connect consecutive points.
        padding (Variable): Horizontal padding from the origin to the first point.
        leftMostPointConstraint (Constraint): Pins the first point's X to the origin plus padding.
        continuityConstraints (list[Constraint]): Constraints that ensure consecutive lines share endpoints.
    """
    def __init__(self,pointNames : list[str]):
        """Initializes the line chart with the given point names.

        Args:
            pointNames (list[str]): Names of the data points. A temporary point is appended
                internally if only one name is provided.
        """
        super().__init__()
        #can not handle only one point TODO
        self.pointNames : list[str] = pointNames
        singlePoint = len(self.pointNames) == 1

        if singlePoint:
            self.pointNames.append("__tmp_point__")

        self.lines : list[VariableLine] = []

        self.padding = Variable("Padding left")

        indexA = 0
        indexB = 1                                                                                                            
        for pointA, pointB in list(pairwise(pointNames)):
            self.lines.append(VariableLine(self.width, self.origin.Y, f"{self.pointNames[indexA]}", f"{self.pointNames[indexB]}")) 
            indexA = indexB
            indexB += 1

        if singlePoint:
            self.lines[-1].SwitchIgnoreRight()

        self.leftMostPointConstraint : Constraint = ((self.lines[0].leftEnd.X == self.origin.X + self.padding)|"required") 
        self.continuityConstraints : list[Constraint] = self._getContinuityConstraints()
    
    def AddPoint(self, name: str):
        """Appends a new point to the right end of the line chart.

        Args:
            name (str): Display name for the new point.

        Returns:
            tuple: The new VariableLine and the list of constraints to add.
        """
        self.pointNames.append(name)
        lastLine = self.lines[-1]
        newLine = VariableLine(self.width, self.origin.Y,f"{self.pointNames[-2]}",f"{self.pointNames[-1]}")
        xContinuityConstraint, yContinuityConstraint = ((lastLine.rightEnd.X == newLine.leftEnd.X) | "required"), ((lastLine.rightEnd.Y == newLine.leftEnd.Y) | "required")
        self.lines.append(newLine)
        self.continuityConstraints.append(xContinuityConstraint)
        self.continuityConstraints.append(yContinuityConstraint)
        return newLine, [xContinuityConstraint, yContinuityConstraint] + newLine.GetAllConstraints()
    
    def _getContinuityConstraints(self):
        result : list[Constraint] = []
        for lineA, lineB in list(pairwise(self.lines)):
            result.append(((lineA.rightEnd.X == lineB.leftEnd.X) | "required"))
            result.append(((lineA.rightEnd.Y == lineB.leftEnd.Y) | "required"))
        return result
    
    def _getAllLineConstraints(self) -> list[Constraint]:
        result : list[Constraint] = []
        for line in self.lines:
            result.extend(line.GetAllConstraints())
        return result

    def GetAllConstraints(self):
        """Returns all constraints for the line chart layout."""
        return self.continuityConstraints + [self.leftMostPointConstraint, (self.width >= 5) | "required", (self.padding >= 0) | "required"] + self._getAllLineConstraints()

    def Value(self):
        """Returns the resolved data for all line segments."""
        return [line.Value() for line in self.lines]
    
    def GetHeightList(self):
        """Returns all height variables for the chart, one per point."""
        return [line.leftHeight for line in self.lines] + [self.lines[-1].rightHeight]

    def ChangeName(self, pointIndex: int, name: str):
        """Changes the display name of the point at the given index.

        Args:
            pointIndex (int): Index of the point. When equal to the number of lines,
                the rightmost endpoint is renamed.
            name (str): New name string.
        """
        if pointIndex == len(self.lines):
            self.lines[-1].ChangeName(name,"right")
            return
        self.lines[pointIndex].ChangeName(name,"left")
        if pointIndex != 0:
            self.lines[pointIndex-1].ChangeName(name,"right")