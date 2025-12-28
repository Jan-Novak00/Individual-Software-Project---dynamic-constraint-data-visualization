from .plotelement import VariableRectangleGroup, VariablePoint2D, VariableCandle, ValuePoint2D, VariableLine, ValueLine
from kiwisolver import Variable, Constraint
from typing import Union
from abc import ABC, abstractmethod
from .utils import *


MINIMAL_WIDTH : float = 10

class VariableChart(ABC):
    """
    Encapsulates all variables of all plot elemenets
    """
    def __init__(self, width : int, spacing : int, xCoordinate : int, yCoordinate : int):
        self.width = Variable("global_width")
        self.widthValueConstraint : Constraint = ((self.width == width) | "strong")

        self.spacing = Variable("global_spacing")
        self.spacingValueConstraint : Constraint = ((self.spacing == spacing) | "strong")

        self.origin: VariablePoint2D = VariablePoint2D("origin")
        self.yAxisHeight: Variable = Variable("axisTop")

        self.originXCoordinateConstraint: Constraint = Constraint(self.origin.X - xCoordinate, "==", "strong")
        self.originYCoordinateConstraint: Constraint = Constraint(self.origin.Y - yCoordinate, "==", "strong")
    
    @abstractmethod
    def GetAllConstraints(self)->list[Constraint]:
        raise NotImplementedError("Method on_left_down must be declared in subclass")
    
    @abstractmethod
    def Value(self):
        raise NotImplementedError("Method on_left_down must be declared in subclass")
    
    def GetOrigin(self)-> ValuePoint2D:
        return self.origin.Value()



class VariableBarChart(VariableChart):
    """
    VariableChart version for bar chart and histogram
    """
    def __init__(self, width: int, initialHeights: list[list[int]], spacing: int, innerSpacing: int, rectangleNames : list[list[str]], xCoordinate: int = 0, yCoordinate: int = 0, widthScalesForGroups : list[list[float]] = None):
        
        super().__init__(width, spacing, xCoordinate, yCoordinate)

        self.innerSpacing = Variable("global_inner_spacing")
        self.innerSpacingValueConstraint : Constraint = (self.innerSpacing == innerSpacing) | "strong"
        
        self.groups : list[VariableRectangleGroup] = [VariableRectangleGroup(self.width,heights,self.innerSpacing, rectangleNames[i] if rectangleNames is not None else None, "blue" ,None if widthScalesForGroups is None else widthScalesForGroups[i]) for i, heights in enumerate(initialHeights)]
        self._createGroupSpacingConstraints()

        self.leftRectangleXCoordinateConstraint : Constraint = (self.groups[0].leftMostX == self.origin.X + self.spacing) | "required"
        self.leftRectangleYCoordinateConstraint : Constraint = (self.groups[0].bottomY == self.origin.Y) | "required"
    
    def SetIntervalValues(self, intervals: list[list[float,float]]):
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
        return [(self.width >= MINIMAL_WIDTH) | "required", (self.spacing >= 0) | "required", (self.innerSpacing >= 0) | "required",self.widthValueConstraint, self.spacingValueConstraint, self.innerSpacingValueConstraint]
    
    def _getVerticalGroupAligmentConstraints(self) -> list[Constraint]:
        return [(self.groups[i-1].bottomY == self.groups[i].bottomY) | "required" for i in range(1,len(self.groups))]
    
    def _getOriginConstraints(self) -> list[Constraint]:
        return [self.originXCoordinateConstraint,self.originYCoordinateConstraint,self.leftRectangleXCoordinateConstraint,self.leftRectangleYCoordinateConstraint]

    def GetAllConstraints(self)-> list[Constraint]:
        return self._getGroupConstraints() + self._getSpacingConstraints()+ self._getVerticalGroupAligmentConstraints() + self._getOriginConstraints()
    
    def GetName(self, groupIndex : int, rectangleIndex : int):
        return self.groups[groupIndex].GetName(rectangleIndex)
    
    def GetHeightVariable(self,groupIndex : int, rectangleIndex : int) -> Variable:
        return self.groups[groupIndex].GetHeightVariable(rectangleIndex)
    
class VariableCandlesticChart(VariableChart):
    """
    VariableChart version for candlestick chart
    """
    def __init__(self, width : int, initialOpening : list[int], initialClosing : list[int], initialMinimum : list[int], initialMaximum : list[int], spacing : int, names : list[str], xCoordinate : int = 0, yCoordinate : int = 0):
        super().__init__(width, spacing, xCoordinate, yCoordinate)

        self.candles = [VariableCandle(self.width, initialClosing[i] - initialOpening[i], initialOpening[i], initialMinimum[i], initialMaximum[i],names[i]) for i in range(len(initialOpening))]
        
        self.leftMostCandleConstriant : Constraint = (self.candles[0].openingCorner.X >= self.origin.X) | "required"

        self._createCandleSpacingConstraints()

    def _createCandleSpacingConstraints(self):
        self.candles[0].SetSpacingConstraint((self.candles[0].openingCorner.X - self.spacing == self.origin.X) | "required")
        for index in range(1, len(self.candles)):
            self.candles[index].SetSpacingConstraint((self.candles[index-1].closingCorner.X + self.spacing == self.candles[index].openingCorner.X) | "required")
    
    def Value(self):
        return [candle.Value() for candle in self.candles]
    
    def _getCandleConstraints(self)-> list[Constraint]:
        result = []
        for candle in self.candles:
            result.extend(candle.GetAllConstraints())
        return result
    
    def _getPositionConstraints(self)-> list[Constraint]:
        return [(self.width >= MINIMAL_WIDTH) | "required", (self.spacing >= 0) | "required", self.originXCoordinateConstraint,self.originYCoordinateConstraint,self.leftMostCandleConstriant]

    def _getGlobalShapeConstraints(self)-> list[Constraint]:
        return [self.widthValueConstraint, self.spacingValueConstraint]

    def GetAllConstraints(self)-> list[Constraint]:
        return self._getCandleConstraints() + self._getPositionConstraints() + self._getGlobalShapeConstraints()
    
    def ChangePositiveColor(self, color : Union[str,int]):
        for candle in self.candles:
            candle.ChangePositiveColor(color)
    
    def ChangeNegativeColor(self, color : Union[str,int]):
        for candle in self.candles:
            candle.ChangeNegativeColor(color)
    
    def SwitchNameVisibility(self, index : int):
        self.candles[index].SwitchNameVisibility()
    
    def ChangeName(self, index: int, name: str):
        self.candles[index].ChangeName(name)
    
    def GetHeightVariable(self, candleIndex : int) -> Variable:
        return self.candles[candleIndex].GetHeightVariable()
    
    def GetName(self, index: int):
        return self.candles[index].GetName()
    
    def GetOpeningCorner(self, index : int) -> VariablePoint2D:
        return self.candles[index].GetOpeningCorner()

    def GetClosingCorner(self, index : int) -> VariablePoint2D:
        return self.candles[index].GetClosingCorner()
    
    def GetWickBottom(self, index : int) -> VariablePoint2D:
        return self.candles[index].GetWickBottom()
    
    def GetWickTop(self, index : int) -> VariablePoint2D:
        return self.candles[index].GetWickTop()

class VariableLineChart(VariableChart):
    def __init__(self, width : int, initialValues : list[int], pointNames : list[str] = [], xCoordinate : int = 0, yCoordinate : int = 0):
        super().__init__(width, 0, xCoordinate, yCoordinate)
        #can not handle only one point
        self.lines : list[VariableLine] = []
        name = 0                                                                                                                #tmp
        for pointA, pointB in list(pairwise(initialValues)):
            self.lines.append(VariableLine(self.width, self.origin.Y, pointA, pointB, f"line{name}:left", f"line{name}:right")) # ToDo add names
            name += 1
        self.leftMostPointConstraint : Constraint = ((self.lines[0].leftEnd.X == self.origin.X)|"required") # less coupling please

        self.continuityConstraints : list[Constraint] = self._getContinuityConstraints()
    
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
        return self.continuityConstraints + [self.leftMostPointConstraint] + self._getAllLineConstraints()

    def Value(self):
        return [line.Value() for line in self.lines]
    
    def GetHeightList(self): # better less couplet implementation required
        return [line.leftHeight for line in self.lines] + [self.lines[-1].rightHeight]
