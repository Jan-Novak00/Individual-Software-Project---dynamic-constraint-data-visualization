from .variablechart import VariableChart, MINIMAL_WIDTH
from kiwiplots.chartelements.rectanglegroups import *
from kiwiplots.chartelements.buckets import *
from abc import ABC, abstractmethod

class VariableRectangleGroupChart(VariableChart,ABC):
    def __init__(self):
        super().__init__()
        self.groups : list[VariableRectangleGroup] | None = None
        self.innerSpacing = Variable("global_inner_spacing")
    
    @abstractmethod
    def ChangeColor(self, groupIndex: int, rectangleIndex: int, color: Union[str,int]):
        return
    
    @abstractmethod
    def ChangeName(self, groupIndex: int, rectangleIndex: int, name: str):
        return

    @abstractmethod
    def GetName(self, groupIndex : int, rectangleIndex : int)->str:
        raise NotImplementedError()
    
    @abstractmethod
    def GetHeightVariable(self,groupIndex : int, rectangleIndex : int) -> Variable:
        raise NotImplementedError()
    
