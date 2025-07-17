import kiwisolver
from kiwisolver import Variable, Constraint, Solver
import random
from typing import Union
import warnings
import functools
import tkinter as tk
import numpy as np

def obsolete(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"!Method {func.__name__} is obsolete.",
            category=DeprecationWarning,
            stacklevel=2
        )
        return func(*args, **kwargs)
    return wrapper


class ValuePoint2D:
    """
    Holds information about 2D points.
    """
    def __init__(self, X: int, Y: int):
        self.X = X
        self.Y = Y
    def __str__(self):
        return f"({self.X}, {self.Y})"

class ValueRectangle:
    """
    Holds information about given rectangle
    """
    def __init__(self, leftBottomCorner: ValuePoint2D, rightTopCorner: ValuePoint2D, color: Union[str, int] = "blue", name: str = ""):
        self.leftBottom = leftBottomCorner
        self.rightTop = rightTopCorner
        self.color = color
        self.name = name

class VariablePoint2D:
  """
  Used for constraint declaration
  """
  def __init__(self):
      self.X = Variable("X")
      self.Y = Variable("Y")


class ConstraintFactory:
    def GetConstraints(self):
        return self.constraints

class Rectangle_ConstraintFactory(ConstraintFactory):
    """
    Creates constraints for a given rectangle.
    Width is maintained globaly, height localy
    """
    def __init__(self, width: Variable, height: int, name: str, color = "blue"):
        self.height = Variable(f"{name}_height")
        self.width = width
        self.name = name
        self.color = color
        self.leftBottom = VariablePoint2D()
        self.rightTop = VariablePoint2D()

        self.constraints = []
        self.customHeightConstraint = None

        self._createHeightConstraint(height)
        self._createCornerConstraints()

    def _createHeightConstraint(self, height: int):
        self.constraints.append((self.height == height) | "weak")

    def _createCornerConstraints(self):
        self.constraints.append((self.leftBottom.X + self.width == self.rightTop.X) | "weak")
        self.constraints.append((self.leftBottom.Y + self.height == self.rightTop.Y) | "weak")

    def FixBottomLeftCorner(self, X: int, Y: int):
        self.constraints.append((self.leftBottom.X == X) | "weak")
        self.constraints.append((self.leftBottom.Y == Y) | "weak")
    
    def ChangeHeight(self, height: int):
        self.customHeightConstraint = (((self.height == height) | "strong"))

    def GetConstraints(self):
        return self.constraints + ([] if self.customHeightConstraint is None else [self.customHeightConstraint])


class InteractiveRectangle:
    def __init__(self, initialHeight: int):
        self.constraintRectangle: Rectangle_ConstraintFactory = None
        self.values: ValueRectangle = None
        self.height = initialHeight

    def setConstraintRectangle(self, constraitRectangle: Rectangle_ConstraintFactory):
        self.constraintRectangle = constraitRectangle



class BarChart_ConstraintFactory(ConstraintFactory):
  def __init__(self, interactiveRectangles: list[InteractiveRectangle], width: int, spacing: int, xCoordinate: int, yCoordinate: int):
      self.spacing = Variable("spacing")
      self.width = Variable("width")
      self.constraints = []
      self.rectangles = interactiveRectangles

      self.xCoordinate = xCoordinate
      self.yCoordinate = yCoordinate

      self.customWidthConstraint = None
      self.customSpacingConstraint = None

      self._createRectangles(interactiveRectangles)

      self._createSpacingConstraint(spacing)
      self._fixFirstRectangle(xCoordinate, yCoordinate)
      self._sameYCoordinateConstraints()
      self._createWidthConstraint(width)
      self._spaceOutRectangles()

  def _createSpacingConstraint(self, spacing: int):
      self.constraints.append((self.spacing == spacing) | "weak")

  def _createWidthConstraint(self, width: int):
      self.constraints.append((self.width == width) | "weak")

  def _createRectangles(self, interactiveRectangles: list[InteractiveRectangle]):
      for i in range(len(interactiveRectangles)):
          interactiveRectangles[i].setConstraintRectangle(Rectangle_ConstraintFactory(self.width, interactiveRectangles[i].height, f"rectangle_{i}", random.randint(0, 0xFFFFFF)))

  def _fixFirstRectangle(self, X: int, Y: int):
      self.rectangles[0].constraintRectangle.FixBottomLeftCorner(X,Y)

  def _spaceOutRectangles(self):
      for i in range(len(self.rectangles)-1):
          self.constraints.append((self.rectangles[i].constraintRectangle.rightTop.X + self.spacing == self.rectangles[i+1].constraintRectangle.leftBottom.X) | "weak")

  def _sameYCoordinateConstraints(self):
      for i in range(len(self.rectangles)-1):
          self.constraints.append((self.rectangles[i].constraintRectangle.leftBottom.Y == self.rectangles[i+1].constraintRectangle.leftBottom.Y) | "weak") 

  def ChangeWidth(self, width: int):
      self.customWidthConstraint = ((self.width == width) | "strong")

  def ChangeSpacing(self, spacing: int):
      self.customSpacingConstraint = ((self.spacing == spacing) | "strong")

  def GetConstraints(self):
      finalConstraints = []
      finalConstraints += ([] if self.customWidthConstraint is None else [self.customWidthConstraint]) + ([] if self.customSpacingConstraint is None else [self.customSpacingConstraint])
      for rec in self.rectangles:
          finalConstraints += rec.constraintRectangle.GetConstraints()
      return finalConstraints + self.constraints
          

class InteractiveBarChart:
    def __init__(self, width: int, rectangles: list[InteractiveRectangle], spacing: int, xCoordinate: int = 0, yCoordinate: int = 0):
        self.rectangles = rectangles
        self.barchartConstraintFactory = BarChart_ConstraintFactory(self.rectangles, width, spacing, xCoordinate, yCoordinate)
        self.SolveRectangleParameters()
    
    def SolveRectangleParameters(self):
        solver = Solver()
        for constraint in self.barchartConstraintFactory.GetConstraints():
            solver.addConstraint(constraint)
        
        solver.updateVariables()

        for rec in self.rectangles:
            leftBotom = ValuePoint2D(rec.constraintRectangle.leftBottom.X.value(), rec.constraintRectangle.leftBottom.Y.value())
            rightTop = ValuePoint2D(rec.constraintRectangle.rightTop.X.value(), rec.constraintRectangle.rightTop.Y.value())
            rec.values = ValueRectangle(leftBotom,rightTop,rec.constraintRectangle.color,rec.constraintRectangle.name)

    def ChangeWidth(self, width: int):
        self.barchartConstraintFactory.ChangeWidth(width)
        self.SolveRectangleParameters()
    def ChangeSpacing(self, spacing: int):
        self.barchartConstraintFactory.ChangeSpacing(spacing)
        self.SolveRectangleParameters()
    
    def ChangeRectangleHeight(self, recIndex: int, recHeight: int):
        self.rectangles[recIndex].constraintRectangle.ChangeHeight(recHeight)
        self.SolveRectangleParameters()

    def GetRectangleParameters(self):
        self.SolveRectangleParameters()
        return [rec.value for rec in self.rectangles]
    
def int_to_hex(color_int):
    return "#{:06x}".format(color_int & 0xFFFFFF)

class BarChartCanvas:
    def __init__(self, initialHeights: list[int], initialWidth: int, initialSpacing: int, canvasWidth: int, canvasHeight: int):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=canvasWidth, height=canvasHeight, bg="white")
        self.canvas.pack()
        self.canvasHeight = canvasHeight

        self.rectangles = [InteractiveRectangle(height) for height in initialHeights]
        self.barChart = InteractiveBarChart(initialWidth,self.rectangles,initialSpacing,0,0)

        self.dragging_index = None
        self.dragging_edge = None
        self.drag_start = ValuePoint2D(0,0)
        self.start_coords = None
        self.start_left_x = None
        self.draw_rectangles()

        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.check_cursor()
        self.root.mainloop()

        

    def draw_rectangles(self):
        self.canvas.delete("all")
        print(self.canvasHeight)
        for rec in self.rectangles:
            vr = rec.values
            if vr is None:
                continue
            x1 = vr.leftBottom.X
            x2 = vr.rightTop.X
            y1 = self.canvasHeight - vr.leftBottom.Y
            y2 = self.canvasHeight - vr.rightTop.Y
            # Y1 je spodní hrana (větší Y na canvasu), Y2 je horní hrana (menší Y na canvasu)
            # ale v canvas.create_rectangle se musí předat y2, y1, protože y2 < y1 (canvas y roste dolů)
            self.canvas.create_rectangle(x1, y2, x2, y1, fill=int_to_hex(vr.color), outline="black")
            print(f"drawing rectangle ({x1}, {y1}) - ({x2}, {y2})")
            
    
    def is_near(self, val1, val2, tolerance=5):
        return abs(val1 - val2) < tolerance
    
    def isNearRightEdge(self, event, rectangle: ValueRectangle):
        canvas_y_bottom = self.canvasHeight - rectangle.leftBottom.Y
        canvas_y_top = self.canvasHeight - rectangle.rightTop.Y
        return self.is_near(event.x, rectangle.rightTop.X) and canvas_y_top <= event.y <= canvas_y_bottom
    
    def isNearLeftEdge(self, event, rectangle: ValueRectangle):
        canvas_y_bottom = self.canvasHeight - rectangle.leftBottom.Y
        canvas_y_top = self.canvasHeight - rectangle.rightTop.Y
        return self.is_near(event.x, rectangle.leftBottom.X) and canvas_y_top <= event.y <= canvas_y_bottom


    def isNearTopEdge(self, event, rectangle: ValueRectangle):
        canvas_y = self.canvasHeight - rectangle.rightTop.Y
        return self.is_near(event.y, canvas_y) and rectangle.leftBottom.X <= event.x <= rectangle.rightTop.X

    
    def clickedOnRightEdge(self, event, rectangle_index: int):
        self.dragging_edge = 'right'
        self.drag_start = ValuePoint2D(event.x, event.y)
        self.dragging_index = rectangle_index
        self.start_coords = self.rectangles[rectangle_index].values.rightTop
        # Ulož levý okraj pro pozdější výpočet šířky:
        self.start_left_x = self.rectangles[rectangle_index].values.leftBottom.X

    def clickedOnLeftEdge(self, event, rectangle_index: int):
        self.dragging_edge = 'left'
        self.drag_start = ValuePoint2D(event.x, event.y)
        self.dragging_index = rectangle_index
        self.start_left_x = self.rectangles[rectangle_index].values.leftBottom.X
        self.prev_right_x = self.rectangles[rectangle_index - 1].values.rightTop.X
        self.start_spacing = self.start_left_x - self.prev_right_x



    def clickedOnTopEdge(self, event, rectangle_index: int):
        self.dragging_edge = 'top'
        self.drag_start = ValuePoint2D(event.x, event.y)
        self.dragging_index = rectangle_index
        # Převeďte logickou Y souřadnici na canvasovou Y souřadnici:
        canvas_y_top = self.canvasHeight - self.rectangles[rectangle_index].values.rightTop.Y
        # Uložte canvasové souřadnice, aby se neobjevily trhliny/skoky při posunu
        self.start_coords = ValuePoint2D(self.rectangles[rectangle_index].values.rightTop.X, canvas_y_top)



    def on_mouse_down(self, event):
        for idx, rec in enumerate(self.rectangles):
            rectangleParameters = rec.values
            if self.isNearRightEdge(event, rectangleParameters):
                self.clickedOnRightEdge(event, idx)
                return
            elif self.isNearTopEdge(event, rectangleParameters):
                self.clickedOnTopEdge(event, idx)
                return
            elif self.isNearLeftEdge(event, rectangleParameters) and idx > 0:
                self.clickedOnLeftEdge(event, idx)
                return
    
    def on_mouse_move(self, event):
        if self.dragging_index is None or self.dragging_edge is None:
            return
        
        dy = event.y - self.drag_start.Y

        if self.dragging_edge == 'right':
            # nový výpočet šířky: vzdálenost mezi levým okrajem obdélníku a aktuální pozicí kurzoru
            new_width = event.x - self.start_left_x
            if new_width > 10:
                self.barChart.ChangeWidth(new_width)
                self.draw_rectangles()

        elif self.dragging_edge == 'top':
            rect = self.rectangles[self.dragging_index]
            bottom_y = rect.values.leftBottom.Y
            new_canvas_y = self.start_coords.Y + dy
            new_top_y = self.canvasHeight - new_canvas_y  # převedení canvas souřadnice na logickou
            new_height = new_top_y - bottom_y
            if new_height > 10:
                self.barChart.ChangeRectangleHeight(self.dragging_index, new_height)
                self.draw_rectangles()
        elif self.dragging_edge == 'left':
            dx = event.x - self.drag_start.X
            new_spacing = self.start_spacing + dx
            if new_spacing > 0:
                self.barChart.ChangeSpacing(new_spacing)
                self.draw_rectangles()

    def on_mouse_up(self, event):
        self.dragging_index = None
        self.dragging_edge = None
        self.drag_start = ValuePoint2D(0, 0)
        self.start_coords = None
        self.start_left_x = None
    
    def check_cursor(self):
        def on_motion(event):
            for idx, rec in enumerate(self.rectangles):
                rect = rec.values
                if self.isNearRightEdge(event, rect):
                    self.canvas.config(cursor="sb_h_double_arrow")
                    return
                elif self.isNearTopEdge(event, rect):
                    self.canvas.config(cursor="sb_v_double_arrow")
                    return
                elif idx > 0 and self.isNearLeftEdge(event, rect):  # <- přidáno
                    self.canvas.config(cursor="hand2")
                    return
            self.canvas.config(cursor="arrow")

        self.canvas.bind("<Motion>", on_motion)

if __name__ == "__main__":
    #initial_heights = list(map(int, np.random.poisson(50, 200)))
    initial_heights = [60, 20 ,70] 
    initial_width = 20
    initial_spacing = 10
    canvas_width = 1000
    canvas_height = 200

    BarChartCanvas(initial_heights, initial_width, initial_spacing, canvas_width, canvas_height)
