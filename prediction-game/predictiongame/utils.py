from itertools import tee as _tee
from kiwiplots.solvers import *
from kiwiplots.plotui.plotmetadata import *

def pairwise(iterable):
    """Returns an iterator of consecutive overlapping pairs from the iterable.

    Uses the built-in itertools.pairwise when available (Python 3.10+),
    otherwise falls back to a zip-based implementation.

    Args:
        iterable: Any iterable to pair up.

    Returns:
        An iterator of (a, b) tuples for each consecutive pair.
    """
    try:
       from itertools import pairwise 
       return pairwise(iterable)
    except Exception:
        a, b = _tee(iterable)
        next(b, None)
        return zip(a, b)

def GetCannonicalData(solver: ChartSolver, metadata: PlotMetadata):
    """Extracts normalized chart values from a solver in a canonical form.

    Converts raw solver data to real-world values by applying the metadata scale
    factor and axis offset. The return format depends on the solver type:
    - BarChartSolver: list of groups, each containing bar heights.
    - HistogramSolver: flat list of bucket heights.
    - LineChartSolver: flat list of point values.
    - CandlestickChartSolver: list of four lists [openings, closings, minima, maxima].

    Args:
        solver (ChartSolver): The solver containing the chart data.
        metadata (PlotMetadata): Metadata with the height scale factor and axis offset.

    Returns:
        Canonical data structure for the given solver type.
    """
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