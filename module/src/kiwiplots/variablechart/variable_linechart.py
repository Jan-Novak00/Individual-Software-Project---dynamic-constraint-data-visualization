from kiwisolver import Constraint, Variable
from kiwiplots.chartelements import VariableLine
from kiwiplots.utils import pairwise
from .variablechart import VariableChart

class VariableLineChart(VariableChart):
    def __init__(self,pointNames : list[str]):
        super().__init__()
        #can not handle only one point TODO
        self.pointNames : list[str] = pointNames
        self.lines : list[VariableLine] = []

        self.padding = Variable("Padding left")

        indexA = 0
        indexB = 1                                                                                                            
        for pointA, pointB in list(pairwise(pointNames)):
            self.lines.append(VariableLine(self.width, self.origin.Y, f"{self.pointNames[indexA]}", f"{self.pointNames[indexB]}")) # ToDo add names
            indexA = indexB
            indexB += 1
        self.leftMostPointConstraint : Constraint = ((self.lines[0].leftEnd.X == self.origin.X + self.padding)|"required") # less coupling please

        self.continuityConstraints : list[Constraint] = self._getContinuityConstraints()
    
    def AddPoint(self, name: str):
        print("--- chart.AddPoint method start ---")
        self.pointNames.append(name)
        lastLine = self.lines[-1]
        newLine = VariableLine(self.width, self.origin.Y,f"{self.pointNames[-2]}",f"{self.pointNames[-1]}")
        xContinuityConstraint, yContinuityConstraint = ((lastLine.rightEnd.X == newLine.leftEnd.X) | "required"), ((lastLine.rightEnd.Y == newLine.leftEnd.Y) | "required")
        self.lines.append(newLine)
        self.continuityConstraints.append(xContinuityConstraint)
        self.continuityConstraints.append(yContinuityConstraint)
        print("--- chart.AddPoint method end ---")
        return newLine, [xContinuityConstraint, yContinuityConstraint] + newLine.GetAllConstraints() #TODO better return
    
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
        return self.continuityConstraints + [self.leftMostPointConstraint, (self.width >= 5) | "required", (self.padding >= 0) | "required"] + self._getAllLineConstraints()

    def Value(self):
        return [line.Value() for line in self.lines]
    
    def GetHeightList(self): # better less coupled implementation required TODO
        return [line.leftHeight for line in self.lines] + [self.lines[-1].rightHeight]