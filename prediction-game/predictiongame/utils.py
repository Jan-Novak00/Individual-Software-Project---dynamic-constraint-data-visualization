from itertools import tee as _tee
from kiwiplots.solvers import *
from kiwiplots.plotui.plotmetadata import *

def pairwise(iterable):
    try:
       from itertools import pairwise 
       return pairwise(iterable)
    except Exception:
        a, b = _tee(iterable)
        next(b, None)
        return zip(a, b)

def GetCannonicalData(solver: ChartSolver, metadata: PlotMetadata):
    if isinstance(solver,BarChartSolver):
        assert isinstance(metadata,BarChartMetadata)
        groups = solver.GetGroupData()
        result = []
        for ig in range(len(groups)):
            result.append([])
            for rec in groups[ig]:
                height = rec.GetHeight()
                value = height/metadata.heightScaleFactor
                result[-1].append(value)
        return result
    if isinstance(solver,HistogramSolver):
        assert isinstance(metadata,HistogramMetadata)
        buckets = solver.GetBucketData()
        return [bucket.GetHeight()/metadata.heightScaleFactor for bucket in buckets]
    if isinstance(solver,LineChartSolver):
        assert isinstance(metadata,LineChartMetadata)
        lines = solver.GetLineData()
        pointHeights = [line.leftHeight for line in lines] + [lines[-1].rightHeight]
        return [height/metadata.heightScaleFactor + metadata.xAxisValue for height in pointHeights]
    if isinstance(solver,CandlestickChartSolver):
        assert isinstance(metadata,CandlesticPlotMetadata)
        candles = solver.GetCandleData()
        openings = [candle.openingCorner.Y/metadata.heightScaleFactor + metadata.xAxisValue for candle in candles]
        closings = [candle.closingCorner.Y/metadata.heightScaleFactor + metadata.xAxisValue for candle in candles]
        minima = [candle.wickBottom.Y/metadata.heightScaleFactor + metadata.xAxisValue for candle in candles]
        maxima = [candle.wickTop.Y/metadata.heightScaleFactor + metadata.xAxisValue for candle in candles]
        return [openings,closings,minima,maxima]
    assert False, "Unreachable reached"