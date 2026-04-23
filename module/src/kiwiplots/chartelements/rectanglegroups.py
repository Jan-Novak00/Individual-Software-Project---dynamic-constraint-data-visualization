from kiwisolver import Variable, Constraint
from .basicelements import VariableElement
from .rectangles import *
from .buckets import *

class VariableRectangleGroup(VariableElement):
    """
    Represents a group of rectangles. Rectangles are separated by innerSpacing Variable, which is declared globaly.
    """
    def __init__(self, rectangleWidth: Variable, innerSpacing: Variable, names: list[str], widthScales : list[float], color : Union[str,int] = "blue"):
        assert len(widthScales) == len(names)
        self.rectangles = [VariableRectangle(width      = rectangleWidth, 
                                             name       = names[i] if names is not None else "", 
                                             color      = color, 
                                             widthScale = widthScales[i]
                                             ) 
                                             for i in range(len(names))]
        self.innerSpacing = innerSpacing
        self.width = rectangleWidth

        for i in range(1,len(self.rectangles)):
            self.rectangles[i].SetSpacingConstraint((self.rectangles[i-1].rightTop.X + self.innerSpacing == self.rectangles[i].leftBottom.X) | "required")

        self.leftMostX : Variable = self.rectangles[0].leftBottom.X
        self.rightMostX : Variable = self.rectangles[-1].rightTop.X
        self.bottomY : Variable = self.rectangles[0].leftBottom.Y

        self.spacingConstraint : Constraint | None = None
    
    def __iter__(self):
        return iter(self.rectangles)

    def SetSpacingConstraint(self, constraint: Constraint):
        self.spacingConstraint = constraint
    
    def _getRectangleConstraints(self)->list[Constraint]:
        result = []
        for rec in self.rectangles:
            constraints = rec.GetAllConstraints()
            result += constraints
        return result
    
    def _getVerticalAligmentConstraints(self)->list[Constraint]:
        return [self.rectangles[i-1].leftBottom.Y == self.rectangles[i].leftBottom.Y for i in range(1,len(self.rectangles))]


    def GetAllConstraints(self)->list[Constraint]:
        """
        Returns all constraints.
        """
        return self._getRectangleConstraints() + self._getVerticalAligmentConstraints() + ([] if self.spacingConstraint == None else [self.spacingConstraint])
    
    def Value(self):
        """
        Return ValueRectangle instances for each rectangle in the group as a list
        """
        return [rec.Value() for rec in self.rectangles]
    
    def Max(self):
        """
        Returns maximal pixel height from the group.
        """
        return max([rec.rightTop.Y - rec.leftBottom.Y for rec in self.Value()])

    def NumberOfRectangles(self)->int:
        return len(self.rectangles)

    def ChangeColor(self, rectangleIndex : int, color: Union[str,int])-> None:
        self.rectangles[rectangleIndex].ChangeColor(color)
    
    def GetHeightVariable(self, rectangleIndex: int) -> Variable:
        return self.rectangles[rectangleIndex].GetHeightVariable()
    

class VariableBarGroup(VariableRectangleGroup):
    def __init__(self, rectangleWidth: Variable, innerSpacing: Variable, names: list[str], color: str | int = "blue"):
        widthScales = [1. for name in names]
        super().__init__(rectangleWidth, innerSpacing, names, widthScales, color)

    def AddBar(self, name: str, widthScale: float = 1):
        print("--- rectangleGroup.AddRectangle start ---")
        #TODO this method can only be called on a group with at least one rectangle
        newRectangle = VariableRectangle(width=self.width,name=name,widthScale=widthScale)
        lastRectangle = self.rectangles[-1]
        self.rectangles.append(newRectangle)
        newRectangle.SetSpacingConstraint((lastRectangle.rightTop.X + self.innerSpacing == newRectangle.leftBottom.X) | "required")
        self.rightMostX = newRectangle.rightTop.X
        print("--- rectangleGroup.AddRectangle end ---")
        return newRectangle
    
    def GetName(self, rectangleIndex : int):
        return self.rectangles[rectangleIndex].GetName()
    
    def ChangeName(self, rectangleIndex : int, name : str) -> None:
        self.rectangles[rectangleIndex].ChangeName(name)


class VariableBucketGroup(VariableRectangleGroup):
    def __init__(self, bucketWidth: Variable, innerSpacing: Variable, intervals: list[tuple[float,float]], widthScales : list[float], color : Union[str,int] = "blue"):
        assert len(intervals) == len(widthScales)
        self.buckets = [VariableBucket(width=bucketWidth,
                                       interval=intervals[i],
                                       color=color,
                                       widthScale=widthScales[i])
                                       for i in range(len(intervals))]
        self.rectangles = self.buckets
        self.innerSpacing = innerSpacing
        self.width = bucketWidth

        for i in range(1,len(self.rectangles)):
            self.rectangles[i].SetSpacingConstraint((self.rectangles[i-1].rightTop.X + self.innerSpacing == self.rectangles[i].leftBottom.X) | "required")

        self.leftMostX : Variable = self.rectangles[0].leftBottom.X
        self.rightMostX : Variable = self.rectangles[-1].rightTop.X
        self.bottomY : Variable = self.rectangles[0].leftBottom.Y

        self.spacingConstraint : Constraint | None = None
    
    def AddBucket(self, interval: tuple[float,float], widthScale: float = 1):
        print("--- histogramGroup.AddHistogram start ---")
        #TODO this method can only be called on a group with at least one rectangle
        newBucket = VariableBucket(width=self.width, interval=interval, widthScale=widthScale)
        lastRectangle = self.rectangles[-1]
        self.rectangles.append(newBucket)
        newBucket.SetSpacingConstraint((lastRectangle.rightTop.X + self.innerSpacing == newBucket.leftBottom.X) | "required")
        self.rightMostX = newBucket.rightTop.X
        print("--- histogramGroup.AddHistogram end ---")
        return newBucket