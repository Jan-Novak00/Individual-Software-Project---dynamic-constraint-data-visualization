from abc import ABC
from .plotmetadata import *
from kiwiplots.solvers import *
from kiwiplots.chartelements import ValuePoint2D, ValueBucket
from PIL import Image, ImageDraw, ImageFont
from .plotmath import ceilToNearestTen, divideInterval

class PictureDrawer(ABC):
    """
    Abstract class for generating image output of plots.
    """
    
    def draw(self, plotMetada : PlotMetadata, solver: ChartSolver, width: int, height: int, file : str):
        """
        Generates and saves an image of the plot.
        
        This method should create an image representation of the plot,
        including all data elements, axes, and labels, and save it to a file.
        
        Args:
            plotMetada: Metadata about the plot including scale factor and axis values.
            solver: The solver containing the plot data to be rendered.
            width: The width of the output image in pixels. Corresponds to canvas width.
            height: The height of the output image in pixels. Corresponds to canvas height.
        """
        raise NotImplementedError("Method PictureDrawer.draw must ASVbe declared in subclass")
    
    def _drawAxes(self, scaleFactor: float, height: int, xAxisValue: float, draw: ImageDraw.ImageDraw, maximumValue: float, leftCornerXAxis: int, origin : ValuePoint2D, minimumValue : int = 0, xAxisLabel:str = "", yAxisLabel: str = ""):  
        """
        Draws axes on the picture output
        """
        topNumber = ceilToNearestTen(maximumValue) 

        marks = divideInterval(minimumValue,topNumber, 5)
      
        draw.line((origin.X, height - origin.Y, leftCornerXAxis + 10, height - origin.Y), fill=(0,0,0), width=1)
        draw.line((origin.X, height - origin.Y - minimumValue, origin.X, height - origin.Y - topNumber), fill=(0,0,0), width=1)

        for mark in marks:
            y = height - origin.Y - mark
            draw.line((origin.X - 5, y, origin.X, y), fill=(0,0,0))

            trueValue = mark/scaleFactor + xAxisValue
            valueString = f"{(trueValue):.2g}" if (trueValue <= 1e-04 or trueValue >= 1e06) else f"{(trueValue):.2f}"
            font = ImageFont.load_default()

            # get text size
            bbox = font.getbbox(valueString)
            textWidth = bbox[2] - bbox[0]
            textHeight = bbox[3] - bbox[1]

            draw.text((origin.X - 10 - textWidth, y - textHeight/2), text=f"{valueString}", fill = (0,0,0))
        
        #Axis labels
        font = ImageFont.truetype("arialbd.ttf", 12)
        bbox = font.getbbox(xAxisLabel)
        textW = bbox[2] - bbox[0]
        textH = bbox[3] - bbox[1]
        draw.text(
            (leftCornerXAxis + 10 - textW/2, height - origin.Y + 10), 
            text=xAxisLabel, fill=(0,0,0), font=font
        )

        bbox = font.getbbox(yAxisLabel)
        textW = bbox[2] - bbox[0]
        textH = bbox[3] - bbox[1]
        draw.text(
            (origin.X - textW/2, height - origin.Y - topNumber - textH - 5), 
            text=yAxisLabel, fill=(0,0,0), font=font
        )
    def _writePlotTitle(self, draw: ImageDraw.ImageDraw, solver: ChartSolver, width: int, title: str):
        font = ImageFont.truetype("arialbd.ttf", 16)
        text = title
        bbox = font.getbbox(text)
        textWidth = bbox[2] - bbox[0]
        draw.text((width / 2 - textWidth/2, 20),text=text,font=font,fill = (0,0,0))

class CandlesticPictureDrawer(PictureDrawer):
    """
    Picture drawer for candlestick charts.
    
    Renders candlestick data with wicks, body rectangles, and optional candle names.
    """
    def _drawCandles(self, solver: CandlestickChartSolver, draw : ImageDraw.ImageDraw, height: int):
        """Draws candlesticks with wicks and names on the image.

        Args:
            solver (CandlestickChartSolver): Solver containing candle data.
            draw (ImageDraw.ImageDraw): PIL ImageDraw object for rendering.
            height (int): Height of the plot area in pixels.
        """
        candles = solver.GetCandleData()
        origin = solver.GetOrigin()
        for candle in candles:
            leftBottomX, leftBottomY = None, None
            rightTopX, rightTopY = None, None

            if candle.closingCorner.Y - candle.openingCorner.Y >= 0:
                leftBottomX, leftBottomY = candle.openingCorner.X, candle.openingCorner.Y
                rightTopX, rightTopY = candle.closingCorner.X, candle.closingCorner.Y
            else:
                leftBottomX, leftBottomY = candle.openingCorner.X, candle.closingCorner.Y
                rightTopX, rightTopY = candle.closingCorner.X, candle.openingCorner.Y


            x1 = leftBottomX
            y1 = height - leftBottomY - origin.Y
            
            x2 = rightTopX
            y2 = height - rightTopY - origin.Y

            draw.rectangle((x1,y2,x2,y1), fill=candle.color, outline="black")

            xMax, yMax = candle.wickTop.X, height - candle.wickTop.Y - origin.Y
            xMin, yMin = candle.wickBottom.X, height - candle.wickBottom.Y - origin.Y
            draw.line((xMax,yMax,xMin,yMin), fill=candle.color, width=1) 

            if candle.nameVisible:
                font = ImageFont.load_default()
                text = candle.name

                # get text size
                bbox = font.getbbox(text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # text position
                x_center = (x1 + x2) / 2
                y_text = height - origin.Y + 10

                draw.text(
                    (x_center - text_width / 2, y_text - text_height/2),
                    text,
                    fill="black",
                    font=font)
    
    def draw(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver, width: int, height: int, file : str): # pyright: ignore[reportIncompatibleMethodOverride]
        """Generates and saves image of candlestick chart.

        Args:
            plotMetadata (CandlesticPlotMetadata): Metadata about the plot.
            solver (CandlestickChartSolver): Solver containing candle data.
            width (int): Width of output image in pixels.
            height (int): Height of output image in pixels.
            file (str): File path to save image.
        """
        candles = solver.GetCandleData()
        lowestWickHeight = min([candle.wickBottom.Y for candle in candles])
        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)
        self._drawCandles(solver, draw, height)
        self._drawAxes(plotMetadata.heightScaleFactor,height, plotMetadata.xAxisValue,draw, solver.GetAxisHeight(), candles[-1].rightTop.X, solver.GetOrigin(), min(0, lowestWickHeight)) # pyright: ignore[reportArgumentType]
        self._writePlotTitle(draw,solver,width,plotMetadata.title)
        img.save(file)

class BarChartPictureDrawer(PictureDrawer):
    """
    Picture drawer for bar charts.
    
    Renders grouped bar rectangles with names and axes.
    """
    def _drawRectangles(self, draw: ImageDraw.ImageDraw, solver: BarChartSolver, height: int):
        """Draws rectangles (bars) with names on the image.

        Args:
            draw (ImageDraw.ImageDraw): PIL ImageDraw object for rendering.
            solver (BarChartSolver): Solver containing rectangle data.
            height (int): Height of the plot area in pixels.
        """
        rectangles = solver.GetBarDataAsList()
        origin = solver.GetOrigin()
        for rec in rectangles:
            x1 = rec.leftBottom.X
            y1 = height - rec.leftBottom.Y
            
            x2 = rec.rightTop.X
            y2 = height - rec.rightTop.Y
            draw.rectangle((x1,y2,x2,y1), fill=rec.color, outline="black")
            font = ImageFont.load_default()
            text = rec.name

            # get text size
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # text position
            x_center = (x1 + x2) / 2
            y_text = (y1 + 10)

            draw.text(
                (x_center - text_width / 2, y_text - text_height/2),
                text,
                fill="black",
                font=font)


    def draw(self, plotMetadata: BarChartMetadata, solver: BarChartSolver, width:int, height: int, file : str):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Generates and saves image of bar chart.

        Args:
            plotMetadata (BarChartMetadata): Metadata about the plot.
            solver (BarChartSolver): Solver containing rectangle data.
            width (int): Width of output image in pixels.
            height (int): Height of output image in pixels.
            file (str): File path to save image.
        """
        rectangles = solver.GetRectangleDataAsList()
        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)
        self._drawRectangles(draw,solver, height)
        self._drawAxes(plotMetadata.heightScaleFactor, 
                          height, 
                          plotMetadata.xAxisValue, 
                          draw, 
                          solver.GetAxisHeight(), 
                          rectangles[-1].rightTop.X,  # pyright: ignore[reportArgumentType]
                          solver.GetOrigin(), 
                          0, 
                          plotMetadata.xAxisLabel, 
                          plotMetadata.yAxisLabel)
        self._writePlotTitle(draw, solver,width,plotMetadata.title)
        img.save(file)

class HistorgramPictureDrawer(BarChartPictureDrawer):
    """
    Picture drawer for histograms.
    
    Extends BarChartPictureDrawer to render histogram buckets with interval labels.
    """
    def _drawRectangles(self, draw: ImageDraw.ImageDraw, solver: BarChartSolver, height: int):
        """Draws histogram buckets with interval labels on the image.

        Args:
            draw (ImageDraw.ImageDraw): PIL ImageDraw object for rendering.
            solver (BarChartSolver): Solver containing bucket data.
            height (int): Height of the plot area in pixels.
        """
        rectangles : list[ValueBucket] = solver.GetRectangleDataAsList() # pyright: ignore[reportAssignmentType]
        for rec in rectangles:
            x1 = rec.leftBottom.X
            y1 = height - rec.leftBottom.Y
            
            x2 = rec.rightTop.X
            y2 = height - rec.rightTop.Y
            draw.rectangle((x1,y2,x2,y1), fill=rec.color, outline="black")
            font = ImageFont.load_default()
            textLeft = str(rec.interval[0])
            textRight = str(rec.interval[1])

            # get text size
            bboxLeft = font.getbbox(textLeft)
            textLeft_width = bboxLeft[2] - bboxLeft[0]
            textLeft_height = bboxLeft[3] - bboxLeft[1]

            bboxRight = font.getbbox(textRight)
            textRight_width = bboxRight[2] - bboxRight[0]
            textRight_height = bboxRight[3] - bboxRight[1]

            y_text = (y1 + 10)

            draw.text(
                (x1 - textLeft_width / 2, y_text - textLeft_height/2),
                textLeft,
                fill="black",
                font=font)
            draw.text(
                (x2 - textRight_width / 2, y_text - textRight_height/2),
                textRight,
                fill="black",
                font=font)
            
class LineChartPictureDrawer(PictureDrawer):
    """
    Picture drawer for line charts.
    
    Renders connected line segments with colored data points and point names.
    """
    def _drawLines(self, plotMetadata: LineChartMetadata, solver: LineChartSolver, draw: ImageDraw.ImageDraw, height: int):
        """Draws line segments with data points and point names on the image.

        Args:
            plotMetadata (LineChartMetadata): Metadata containing line color.
            solver (LineChartSolver): Solver containing line data.
            draw (ImageDraw.ImageDraw): PIL ImageDraw object for rendering.
            height (int): Height of the plot area in pixels.
        """
        RADIUS: int = 4
        lines = solver.GetLineData()
        origin = solver.GetOrigin()

        color = plotMetadata.color if isinstance(plotMetadata.color, str) else f"#{plotMetadata.color:06x}"

        for index, line in enumerate(lines):
            x1, y1 = line.leftEnd.X, height - line.leftEnd.Y
            x2, y2 = line.rightEnd.X, height - line.rightEnd.Y
            
            if not line.ignoreRight: 
                draw.line((x1, y1, x2, y2), fill=(0, 0, 0), width=1)

                draw.ellipse(
                    (x1 - RADIUS, y1 - RADIUS, x1 + RADIUS, y1 + RADIUS),
                    fill=color,
                    outline=(0, 0, 0),
                    width=1
                )
                draw.ellipse(
                    (x2 - RADIUS, y2 - RADIUS, x2 + RADIUS, y2 + RADIUS),
                    fill=color,
                    outline=(0, 0, 0),
                    width=1
                )
            else:
                draw.ellipse(
                    (x1 - RADIUS, y1 - RADIUS, x1 + RADIUS, y1 + RADIUS),
                    fill=color,
                    outline=(0, 0, 0),
                    width=1
                )

            font = ImageFont.load_default()

            leftBbox = font.getbbox(line.leftEnd.name)
            leftTextWidth = leftBbox[2] - leftBbox[0]
            draw.text(
                (x1 - leftTextWidth / 2, height - origin.Y + 10),
                text=line.leftEnd.name,
                fill=(0, 0, 0),
                font=font
            )

            if index == len(lines) - 1 and not line.ignoreRight:
                rightBbox = font.getbbox(line.rightEnd.name)
                rightTextWidth = rightBbox[2] - rightBbox[0]
                draw.text(
                    (x2 - rightTextWidth / 2, height - origin.Y + 10),
                    text=line.rightEnd.name,
                    fill=(0, 0, 0),
                    font=font
                )

    def draw(self, plotMetadata: LineChartMetadata, solver: LineChartSolver, width: int, height: int, file: str):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Generates and saves image of line chart.

        Args:
            plotMetadata (LineChartMetadata): Metadata about the plot.
            solver (LineChartSolver): Solver containing line data.
            width (int): Width of output image in pixels.
            height (int): Height of output image in pixels.
            file (str): File path to save image.
        """
        lines = solver.GetLineData()
        origin = solver.GetOrigin()

        minimum: float = min([line.leftHeight for line in lines] + [line.rightHeight for line in lines])

        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)

        self._drawLines(plotMetadata, solver, draw, height)
        self._drawAxes(
            plotMetadata.heightScaleFactor,
            height,
            plotMetadata.xAxisValue,
            draw,
            solver.GetAxisHeight(),
            int(lines[-1].rightEnd.X),
            origin,
            int(min(minimum, 0)),
            plotMetadata.xAxisLabel,
            plotMetadata.yAxisLabel
        )
        self._writePlotTitle(draw, solver, width, plotMetadata.title)
        img.save(file)
