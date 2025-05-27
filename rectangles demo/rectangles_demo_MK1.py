from kiwisolver import Variable, Solver
from PIL import Image, ImageDraw
from IPython.display import display
class Rectangle:
  def __init__(self, name, color = "blue"):
    self.name = name
    self.leftBottomX = Variable(name+"LB"+"x")
    self.leftBottomY = Variable(name+"LB"+"y")
    self.rightTopX = Variable(name+"RT"+"x")
    self.rightTopY = Variable(name+"RT"+"y")
    self.color = color

  def generateSizeConstraints(self, height, width):
    constraints = [self.rightTopX >= self.leftBottomX + width, self.rightTopY >= self.leftBottomY + height]
    return constraints

  def ToString(self):
    return f"{self.name}LB = ({self.leftBottomX.value()}, {self.leftBottomY.value()}), {self.name}RT = ({self.rightTopX.value()}, {self.rightTopY.value()})"






def generateRectangleImage(rectangles, height, width, spacing):
  constraints = []

  initialSizeConstraints = []
  initialPositionConstraints = [rectangles[0].leftBottomX == 0, rectangles[0].leftBottomY == 0] # fix first rectangle in place
  for rectangle in rectangles:
    initialSizeConstraints += rectangle.generateSizeConstraints(height, width)
    initialPositionConstraints += [rectangle.leftBottomX >= 0, rectangle.leftBottomY >= 0, rectangle.rightTopX >= 0, rectangle.rightTopY >= 0]

  #initialSpacingConstraints = []
  #for i in range(1, len(rectangles)):
  #  initialSpacingConstraints.append(rectangles[i].leftBottomX >= rectangles[i-1].rightTopX + spacing)



  initialSpacingConstraints = [] if len(rectangles) < 2 else [rectangles[1].leftBottomX >= rectangles[0].rightTopX + spacing] # fix spacing between the first and second rectangle
  if len(rectangles) >= 3:
     for i in range(2, len(rectangles)):
      initialSpacingConstraints.append(rectangles[i].leftBottomX - rectangles[i-1].rightTopX >= rectangles[i-1].leftBottomX - rectangles[i-2].rightTopX)


  constraints = initialSizeConstraints + initialPositionConstraints + initialSpacingConstraints

  solver = Solver()
  for constraint in constraints:
    solver.addConstraint(constraint | "weak")


  solver.updateVariables()

  for rectangle in rectangles:
    print(rectangle.ToString())

  #print(solver.dumps())


  img = Image.new("RGB", (1000, 1000), "white")
  draw = ImageDraw.Draw(img)

  for rec in rectangles:
    draw.rectangle([rec.leftBottomX.value(), rec.leftBottomY.value(), rec.rightTopX.value(), rec.rightTopY.value()], fill=rec.color, outline = "black")

  display(img)






generateRectangleImage([Rectangle("a","red"), Rectangle("b", "lightblue"), Rectangle("c","lime")], 100, 60, 140)
