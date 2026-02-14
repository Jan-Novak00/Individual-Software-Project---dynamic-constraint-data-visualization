from abc import ABC
from .plotmetadata import *
from kiwiplots.solvers import *
from PIL import Image, ImageDraw, ImageFont
from .plotmath import ceilToNearestTen, divideInterval

class PictureDrawer(ABC):
    """
    Abstract class for generating image output of plots.
    """
    
    def draw(self, plotMetada : PlotMetadata, solver: ChartSolver, width: int, height: int):
        """
        Generates and saves a PNG image of the plot.
        
        This method should create an image representation of the plot,
        including all data elements, axes, and labels, and save it to a file.
        
        Args:
            plotMetada: Metadata about the plot including scale factor and axis values.
            solver: The solver containing the plot data to be rendered.
            width: The width of the output image in pixels. Corresponds to canvas width.
            height: The height of the output image in pixels. Corresponds to canvas height.
        """
        raise NotImplementedError("Method PictureDrawer.draw must ASVbe declared in subclass")



class CandlesticPictureDrawer(PictureDrawer):
    def _drawCandlesPNG(self, solver: CandlestickChartSolver, draw : ImageDraw.ImageDraw, height: int):
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
    
    def _drawAxesPNG(self, scaleFactor:float, height: int, xAxisValue: float, draw: ImageDraw.ImageDraw, maximumValue: float, leftCornerXAxis: int, origin : ValuePoint2D, minimumValue : int = 0, xAxisLabel:str = "", yAxisLabel: str = ""):  
        """
        Draws axes on the PNG output
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
    
    def _writePlotTitlePNG(self, draw: ImageDraw.ImageDraw, solver:CandlestickChartSolver, width: int):
        font = ImageFont.truetype("arialbd.ttf", 16)
        text = solver.GetTitle()
        bbox = font.getbbox(text)
        textWidth = bbox[2] - bbox[0]
        draw.text((width / 2 - textWidth, 20),text=text,font=font,fill = (0,0,0))

    def draw(self, plotMetadata: CandlesticPlotMetadata, solver: CandlestickChartSolver, width: int, height: int):
        candles = solver.GetCandleData()
        lowestWickHeight = min([candle.wickBottom.Y for candle in candles])
        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)
        self._drawCandlesPNG(solver, draw, height)
        self._drawAxesPNG(plotMetadata.scaleFactor,height, plotMetadata.xAxisValue,draw, solver.GetAxisHeight(), candles[-1].rightTop.X, solver.GetOrigin(), min(0, lowestWickHeight))
        self._writePlotTitlePNG(draw,solver,width)
        img.save(f"{solver.GetTitle()}.png")