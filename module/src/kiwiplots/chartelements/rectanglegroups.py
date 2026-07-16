from kiwisolver import Variable, Constraint
from .basicelements import VariableElement
from .rectangles import *
from .buckets import *
from kiwiplots.utils import inheritdocstring

class VariableRectangleGroup(VariableElement):
    """
    Represents a group of rectangles. Rectangles are separated by innerSpacing Variable, which is declared globaly.

    Attributes:
        rectangles (list[VariableRectangle]) : rectangles in the group
        width (Variable) : globaly declared width Variable, shared among all rectangles
        innerSpacing (Variable) : globaly declared spacing Variable - spacing between rectnagles in the group
        leftMostX (Variable) : x coordinate of the left most edge of the left most rectangle in the group
        rightMostX (Variable) : x coordinate of the right most edge of the right most rectangle i nthe group
        bottomY (Variable) : y coordinate of the bottom side of every rectangle
        spacingConstraint (Union[Constraint,None]) : spacing constraint of the whole group. Is set externaly using SetSpacingConstraint method.

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
            self.rectangles[i].SetSpacingConstraint((self.rectangles[i-1].rightTop.X + self.innerSpacing == self.rectangles[i].leftBottom.X) | "required") # for each rectangle we set its spacing constraint relative to the previous rectangle

        self.leftMostX : Variable = self.rectangles[0].leftBottom.X
        self.rightMostX : Variable = self.rectangles[-1].rightTop.X
        self.bottomY : Variable = self.rectangles[0].leftBottom.Y

        self.spacingConstraint : Constraint | None = None
    
    def __iter__(self):
        """Returns an iterator of VariableRectangle instances

        Returns:
            iterator: rectangle iterator. Iterates in the order from left to right.
        """
        return iter(self.rectangles)

    def SetSpacingConstraint(self, constraint: Constraint):
        """Group spacing constraint setter.

        Args:
            constraint (Constraint): Spacing constraint of the whole group.
        """
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
        return self._getRectangleConstraints() + self._getVerticalAligmentConstraints() + ([] if self.spacingConstraint == None else [self.spacingConstraint])
    
    def Value(self) -> list[ValueRectangle]:
        """
        Return ValueRectangle instances for each rectangle in the group as a list

        Returns:
            list[ValueRectangle] : rectangles in the group
        """
        return [rec.Value() for rec in self.rectangles]
    
    def Max(self)->float:
        """
        Returns maximal pixel height from the group.

        Returns:
            float : height of the highest rectangle
        """
        return max([rec.rightTop.Y - rec.leftBottom.Y for rec in self.Value()])

    def GetNumberOfRectangles(self)->int:
        """Number of rectangles getter

        Returns:
            int: Number of rectangles
        """
        return len(self.rectangles)

    def ChangeColor(self, rectangleIndex : int, color: Union[str,int])-> None:
        """Rectangle color setter

        Args:
            rectangleIndex (int): index of the rectangle whose color is supposed to change
            color (Union[str,int]): new color
        """
        self.rectangles[rectangleIndex].ChangeColor(color)
    
    def GetHeightVariable(self, rectangleIndex: int) -> Variable:
        """Getter for height variable of the given rectangle.

        Args:
            rectangleIndex (int): index of the rectangle

        Returns:
            Variable: rectangle height Variable
        """
        return self.rectangles[rectangleIndex].GetHeightVariable()
    

class VariableBarGroup(VariableRectangleGroup):
    """Represents group of bars for bar chart
    """
    def __init__(self, rectangleWidth: Variable, innerSpacing: Variable, names: list[str], color: str | int = "blue"):
        widthScales = [1. for name in names]
        super().__init__(rectangleWidth, innerSpacing, names, widthScales, color)

    def AddBar(self, name: str)->VariableRectangle:
        """Appends a new bar to the end of the bar group

        Args:
            name (str): name of the new bar

        Returns:
            VariableRectangle: added rectangle
        """
        newRectangle = VariableRectangle(width=self.width,name=name,widthScale=1)
        lastRectangle = self.rectangles[-1]
        self.rectangles.append(newRectangle)
        newRectangle.SetSpacingConstraint((lastRectangle.rightTop.X + self.innerSpacing == newRectangle.leftBottom.X) | "required")
        self.rightMostX = newRectangle.rightTop.X
        return newRectangle
    
    def GetName(self, rectangleIndex : int)->str:
        """Rectangle name getter

        Args:
            rectangleIndex (int): index of the rectangle

        Returns:
            str: name of the rectangle
        """
        return self.rectangles[rectangleIndex].GetName()
    
    def ChangeName(self, rectangleIndex : int, name : str) -> None:
        """Rectangle name setter

        Args:
            rectangleIndex (int): index of the rectangle
            name (str): new name
        """
        self.rectangles[rectangleIndex].ChangeName(name)


class VariableBucketGroup(VariableRectangleGroup):
    """Represents group of buckets for histogram
    """
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
        """Appends new bucket to the group

        Args:
            interval (tuple[float,float]): interval of the new bucket
            widthScale (float, optional): width scale of the bucket. Defaults to 1.

        Returns:
            VariableBucket: new bucket
        """
        newBucket = VariableBucket(width=self.width, interval=interval, widthScale=widthScale)
        lastRectangle = self.rectangles[-1]
        self.rectangles.append(newBucket)
        newBucket.SetSpacingConstraint((lastRectangle.rightTop.X + self.innerSpacing == newBucket.leftBottom.X) | "required")
        self.rightMostX = newBucket.rightTop.X
        return newBucket