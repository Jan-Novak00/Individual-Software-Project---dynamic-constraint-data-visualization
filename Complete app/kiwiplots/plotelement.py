from kiwisolver import Variable, Constraint
from typing import Union

class ValuePoint2D:
    """
    Holds information about 2D points.
    """
    def __init__(self, X: int, Y: int, name: str = "", secondaryName: str = ""):
        self.X = X
        self.Y = Y
        self.name = name
        self.secondaryName = secondaryName
    def __str__(self):
        return f"({self.X}, {self.Y})"

class ValueRectangle:
    """
    Holds information about a given rectangle
    """
    def __init__(self, leftBottomCorner: ValuePoint2D, rightTopCorner: ValuePoint2D, color: Union[str, int] = "blue", name: str = ""):
        self.leftBottom = leftBottomCorner
        self.rightTop = rightTopCorner
        self.color = color
        self.name = name
    
    def __str__(self):
        return f"{self.name} LB: ({self.leftBottom.X}, {self.leftBottom.Y}), RT: ({self.rightTop.X}, {self.rightTop.Y})"
    def GetHeight(self):
        return self.rightTop.Y-self.leftBottom.Y

class VariablePoint2D:
  """
  Used for constraint declaration. Represents 2D point as a pair of Variable instances-
  """
  def __init__(self, name: str = "", secondaryName = ""):
        self.X = Variable(f"{name}.X")
        self.Y = Variable(f"{name}.Y")
        self.name = name
        self.secondaryName = secondaryName
  def Value(self):
        return ValuePoint2D(self.X.value(), self.Y.value(), self.name, self.secondaryName)

class VariableRectangle:
    """
    Creates constraints for a given rectangle.
    Width is maintained globaly, height localy
    Arguments:
        width - globaly declared Variable of width
        height - pixel height of the rectangle
        name - name of the rectangle
        color - color of the ractangle
        widthScale - scale of the width. Resulting pixel width of the rectangle is widthScale*width.value()
    """
    def __init__(self, width: Variable, height: int, name: str, color = "blue", widthScale : float = 1):
        self.height = Variable(f"{name}_height")
        self.width = width
        self.widthScale = widthScale
        self.name = name
        self.color = color
        self.leftBottom = VariablePoint2D(name+".leftBottom")
        self.rightTop = VariablePoint2D(name+".rightTop")

        self.heightConstraint : Constraint = (self.height == float(height)) | "strong"
        self.horizontalPositionConstraint : Constraint = ((self.leftBottom.X + self.width * self.widthScale == self.rightTop.X) | "required")
        self.verticalPositionConstraint : Constraint = ((self.leftBottom.Y + self.height == self.rightTop.Y) | "required")

        self.bottomLeftXPositionConstraint : Constraint = None
        self.bottomLeftYPositionConstraint : Constraint = None

        self.spacingConstraint : Constraint = None

    def __iter__(self):
        """
        Returns iterator over basic constraints.
        """
        constraints = [self.heightConstraint]
        if self.spacingConstraint is not None:
            constraints.append(self.spacingConstraint)
        if self.bottomLeftXPositionConstraint is not None:
            constraints.append(self.bottomLeftXPositionConstraint)
        if self.bottomLeftYPositionConstraint is not None:
            constraints.append(self.bottomLeftYPositionConstraint)
        constraints.append(self.horizontalPositionConstraint)
        constraints.append(self.verticalPositionConstraint)
        return iter(constraints)
   
    
    def SetSpacingConstraint(self, spacingConstraint : Constraint):
        self.spacingConstraint = spacingConstraint
    
    def GetAllConstraints(self):
        """
        Returns all constraints, both from __iter__ method and constraints which specify domain of variables
        """
        constraints = [constraint for constraint in self] + [(self.height >= 0)|"required",(self.leftBottom.X >= 0) | "required", (self.leftBottom.Y >= 0) | "required", (self.rightTop.X >= 0) | "required", (self.rightTop.Y >= 0) | "required"]
        return constraints
    
    def Value(self):
        """
        Returns ValueRectangle representation of the instance.
        """
        return ValueRectangle(self.leftBottom.Value(), self.rightTop.Value(), self.color, self.name)

class VariableRectangleGroup:
    """
    Represents a group of rectangles. Rectangles are separated by innerSpacing Variable, which is declared globaly.
    """
    def __init__(self, rectangleWidth: Variable, heights: list[int], innerSpacing: Variable, names: list[str], color: str = "blue", widthScales : list[float] = None):
        self.rectangles = [VariableRectangle(rectangleWidth, height, names[i] if names is not None else "", color, (1 if widthScales is None else widthScales[i])) for i,height in enumerate(heights)]
        self.innerSpacing = innerSpacing


        for i in range(1,len(self.rectangles)):
            self.rectangles[i].SetSpacingConstraint((self.rectangles[i-1].rightTop.X + self.innerSpacing == self.rectangles[i].leftBottom.X) | "required")

        self.leftMostX : Variable = self.rectangles[0].leftBottom.X
        self.rightMostX : Variable = self.rectangles[-1].rightTop.X
        self.bottomY : Variable = self.rectangles[0].leftBottom.Y

        self.spacingConstraint : Constraint = None
    
    def __iter__(self):
        return iter(self.rectangles)

    def SetSpacingConstraint(self, constraint: Constraint):
        self.spacingConstraint = constraint
    
    def GetAllConstraints(self):
        """
        Returns all constraints.
        """
        result = []
        for rec in self.rectangles:
            constraints = rec.GetAllConstraints()
            result += constraints
        return result \
                    + [self.rectangles[i-1].leftBottom.Y == self.rectangles[i].leftBottom.Y for i in range(1,len(self.rectangles))] \
                    + ([] if self.spacingConstraint == None else [self.spacingConstraint])
    
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

    def NumberOfRectangles(self):
        return len(self.rectangles)

class ValueCandle(ValueRectangle):
    """
    Holds information about a given candle.
    """
    def __init__(self, openingCorner : ValuePoint2D, closingCorner : ValuePoint2D, wickBottom : ValuePoint2D, wickTop : ValuePoint2D, color = "blue", name = "", nameVisible : bool = False):
        super().__init__(openingCorner, closingCorner, color, name)
        self.openingCorner : ValuePoint2D = self.leftBottom
        self.closingCorner : ValuePoint2D = self.rightTop

        self.wickBottom : ValuePoint2D = wickBottom
        self.wickTop : ValuePoint2D = wickTop
        self.nameVisible = nameVisible
    def __str__(self):
        return f"{self.name} opening: ({self.leftBottom.X}, {self.leftBottom.Y}), closing: ({self.rightTop.X}, {self.rightTop.Y}) Wick: bottom: ({self.wickBottom.X}, {self.wickBottom.Y}) top: ({self.wickTop.X}, {self.wickTop.Y})"

class VariableCandle(VariableRectangle):
    """
    Creates constraints for a given candle.
    Width is maintained globaly, height localy
    Arguments:
        width - globaly declared Variable of width
        height - pixel height of the rectangle
        openingPosition - pixel height of the candle
        minPosition - pixel height of the minimum
        maxPosition - pixel height of the maximum
        name - name of the candle
        positiveColor - color of the candle when it represents positive value
        negativeColor - color of the candle when it represents negative value
        widthScale - scale of the width. Resulting pixel width of the rectangle is widthScale*width.value()
    """    
    def __init__(self, width: Variable, height: int, openingPosition: int, minPosition: int, maxPosition: int, name: str = "candle", positiveColor="green", negativeColor="red"):
        
        super().__init__(width, height, name, positiveColor if height >= 0 else negativeColor)


        self.openingCorner : VariablePoint2D = self.leftBottom
        self.closingCorner : VariablePoint2D = self.rightTop

        self.wickBottom : VariablePoint2D = VariablePoint2D(self.name+".wickBottom")
        self.wickTop : VariablePoint2D = VariablePoint2D(self.name+".wickTop")
        
        self.wickXConstraint : Constraint = ((self.wickBottom.X == (self.leftBottom.X + self.rightTop.X)/2) | "required")
        self.straightWickConstraint : Constraint = ((self.wickBottom.X == self.wickTop.X) | "required")
        
        self.wickBottomConstraint : Constraint = ((self.wickBottom.Y == minPosition) | "weak")
        self.wickTopConstraint : Constraint = ((self.wickTop.Y == maxPosition) | "weak")

        self.wickBottomTrueMinimumConstraints : list[Constraint] = [((self.wickBottom.Y <= self.closingCorner.Y) | "required"), ((self.wickBottom.Y <= self.openingCorner.Y) | "required")]
        self.wickTopTrueMaximumConstraints : list[Constraint] = [((self.wickTop.Y >= self.closingCorner.Y) | "required"), ((self.wickTop.Y >= self.openingCorner.Y) | "required")]

        self.openingCornerConstraint : Constraint = ((self.openingCorner.Y == openingPosition) | "weak")

        self.positiveColor = positiveColor
        self.negativeColor = negativeColor
        self.nameVisible : bool = False

    def __iter__(self):
        """
        Returns basic constraints.
        """
        result = list(super().__iter__())
        result.extend([self.wickXConstraint, self.straightWickConstraint])
        result.extend([self.wickBottomConstraint, self.wickTopConstraint])
        result.append(self.openingCornerConstraint)
        return iter(result)
        
    def GetAllConstraints(self):
        """
        Returns all constraints, both from __iter__ method and constraints which specify domain of variables
        """
        return [constraint for constraint in self] + [(self.closingCorner.X >= 0) | "required", (self.openingCorner.X >= 0) | "required", (self.wickBottom.X >= 0) | "required", (self.wickTop.X >= 0) | "required"] \
                +self.wickBottomTrueMinimumConstraints+self.wickTopTrueMaximumConstraints
    
    def Value(self):
        """
        Return ValueCandle instances for each rectangle in the group as a list
        """
        return ValueCandle(self.openingCorner.Value(), self.closingCorner.Value(), self.wickBottom.Value(), self.wickTop.Value(), self.positiveColor if self.height.value() >= 0 else self.negativeColor, self.name, self.nameVisible)
        
    def ChangePositiveColor(self, color: str):
        self.positiveColor = color
    def ChangeNegativeColor(self, color: str):
        self.negativeColor = color
    def SwitchNameVisibility(self):
        self.nameVisible = not self.nameVisible