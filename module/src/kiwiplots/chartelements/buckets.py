from .rectangles import ValueRectangle, VariableRectangle
from typing import Union
from .basicelements import ValuePoint2D, VariablePoint2D
from kiwisolver import Constraint, Variable
import warnings
from kiwiplots.utils import MethodWithoutEffectWarning

class ValueBucket(ValueRectangle):
    def __init__(self, leftBottomCorner: ValuePoint2D, 
                       rightTopCorner: ValuePoint2D,
                       interval : tuple[float,float],
                       color: str | int = "blue"):
        super().__init__(leftBottomCorner=leftBottomCorner,
                         rightTopCorner=rightTopCorner,
                         color=color,
                         name=f"[{interval[0]}, {interval[1]}]")
        self.interval : tuple[float,float] = interval

class VariableBucket(VariableRectangle):
    def __init__(self, width: Variable, 
                       interval: tuple[float,float], 
                       color : Union[str,int] = "blue", 
                       widthScale : float = 1):
        
        super().__init__(width=width,
                         name=f"[{interval[0]}, {interval[1]}]",
                         color=color,
                         widthScale=widthScale)
        self.interval : tuple[float,float] = interval

    def ChangeName(self, name: str):
        warnings.warn(message=f"Method {type(self).__name__}.ChangeName has no effect. This is intentional.",
                      category=MethodWithoutEffectWarning,
                      stacklevel=2)
    
    def GetInterval(self)->tuple[float,float]:
        return self.interval
    
    def Value(self)->ValueBucket:
        return ValueBucket(self.leftBottom.Value(), self.rightTop.Value(), self.interval, self.color)