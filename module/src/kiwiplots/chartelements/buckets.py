from .rectangles import ValueRectangle, VariableRectangle
from typing import Union
from .basicelements import ValuePoint2D, VariablePoint2D
from kiwisolver import Constraint, Variable
import warnings
from kiwiplots.utils import MethodWithoutEffectWarning

class ValueBucket(ValueRectangle):
    """
    Value representaion of histogram bucket.
    """
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
    """
    Representation of histogram bucket.
    """
    def __init__(self, width: Variable, 
                       interval: tuple[float,float], 
                       color : Union[str,int] = "blue", 
                       widthScale : float = 1):
        """
        Bucket constructor. Calls VariableRectangle constructor.

        Args:
            width (Variable): width variable for VariableRectangle constructor.
            interval (tuple[float,float]): interval the bucket represents.
            color (Union[str,int], optional): color of the bucke for VariableRectangle constructor. Defaults to "blue".
            widthScale (float, optional): width scale of the bucket for VariableRectangle constructor. Defaults to 1.
        """
        
        super().__init__(width=width,
                         name=f"[{interval[0]}, {interval[1]}]",
                         color=color,
                         widthScale=widthScale)
        self.interval : tuple[float,float] = interval

    def ChangeName(self, name: str):
        """
        Name setter. Has no effect when called.

        Args:
            name (str): argument has no effect on the call result.
        """
        warnings.warn(message=f"Method {type(self).__name__}.ChangeName has no effect. This is intentional.",
                      category=MethodWithoutEffectWarning,
                      stacklevel=2)
    
    def GetInterval(self)->tuple[float,float]:
        """
        Interval getter.
        
        Returns:
            tuple[float,float]: interval the bucket represents
        """
        return self.interval
    
    def Value(self)->ValueBucket:
        """
        Value representation of the bucket.
        
        Returns:
            ValueBucket: Snapshot of the bucket.
        """
        return ValueBucket(self.leftBottom.Value(), self.rightTop.Value(), self.interval, self.color)