from .variablechart import VariableChart, MINIMAL_WIDTH
from kiwiplots.chartelements.rectanglegroups import *
from kiwiplots.chartelements.buckets import *
from abc import ABC, abstractmethod

class VariableRectangleGroupChart(VariableChart,ABC):
    """Abstract base for charts composed of groups of rectangles.

    Extends VariableChart with an inner spacing variable and abstract methods
    for color, name, and height-variable access that subclasses must implement.

    Attributes:
        groups (list[VariableRectangleGroup] | None): The rectangle groups of the chart.
        innerSpacing (Variable): Spacing between rectangles within a single group.
    """
    def __init__(self):
        """Initializes the rectangle group chart with an inner spacing variable."""
        super().__init__()
        self.groups : list[VariableRectangleGroup] | None = None
        self.innerSpacing = Variable("global_inner_spacing")
    
    @abstractmethod
    def ChangeColor(self, groupIndex: int, rectangleIndex: int, color: Union[str,int]):
        """Changes the color of a rectangle at the given group and rectangle index.

        Args:
            groupIndex (int): Index of the rectangle group.
            rectangleIndex (int): Index of the rectangle within the group.
            color (Union[str, int]): New color.
        """
        raise NotImplementedError("Method must be declared in a subclass.")
    
    @abstractmethod
    def ChangeName(self, groupIndex: int, rectangleIndex: int, name: str):
        """Changes the display name of a rectangle at the given group and rectangle index.

        Args:
            groupIndex (int): Index of the rectangle group.
            rectangleIndex (int): Index of the rectangle within the group.
            name (str): New name.
        """
        raise NotImplementedError("Method must be declared in a subclass.")

    @abstractmethod
    def GetName(self, groupIndex : int, rectangleIndex : int)->str:
        """Returns the display name of a rectangle at the given group and rectangle index.

        Args:
            groupIndex (int): Index of the rectangle group.
            rectangleIndex (int): Index of the rectangle within the group.

        Returns:
            str: Current name of the rectangle.
        """
        raise NotImplementedError("Method must be declared in a subclass.")
    
    @abstractmethod
    def GetHeightVariable(self,groupIndex : int, rectangleIndex : int) -> Variable:
        """Returns the kiwisolver height variable for the specified rectangle.

        Args:
            groupIndex (int): Index of the rectangle group.
            rectangleIndex (int): Index of the rectangle within the group.

        Returns:
            Variable: The height variable for that rectangle.
        """
        raise NotImplementedError("Method must be declared in a subclass.")

