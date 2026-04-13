
def CalculateScaleFactor(values: list[float],height: int)->float:
    """
    Compute a vertical scale factor to fit numeric values into a plot height.

    The function returns 1 when values already fall within a comfortable
    portion of the available height; otherwise it scales values so their
    maximum maps to approximately 80% of the provided `height`.

    Args:
        values (list[float]): Sequence of data values to be plotted.
        height (int): Pixel height of the plot area.

    Returns:
        float: Scale factor to multiply raw values by to convert to pixels.
    """
    scaleFactor : float = 1
    absValues = [abs(val) for val in values]
    maxValue = max(absValues,default=1)
    if not (height*0.3 <= maxValue <= height*0.7):
        scaleFactor = height*0.8/maxValue
    return scaleFactor


def RescaleList(inputList : list[float], scaleFactor : float, scaledXAxisValue: float = 0) -> list[int]:
    """
    Rescale a list of float values to integers using a scale factor and optional offset.

    Applies the formula: int(value * scaleFactor - scaledXAxisValue) to each value
    in the input list, converting them to pixel coordinates for plotting.

    Args:
        inputList (list[float]): List of float values to rescale.
        scaleFactor (float): Factor to multiply each value by.
        scaledXAxisValue (float, optional): Offset value to subtract after scaling. Defaults to 0.

    Returns:
        list[int]: List of rescaled integer values.
    """
    return [int(value*scaleFactor-scaledXAxisValue) for value in inputList]


def CreateScalesForIntervalGroup(intervals : list[tuple[float,float]])->list[float]:
    """
    Compute relative width scale factors for a group of histogram intervals.

    The smallest positive interval length maps to scale 1.0; other
    intervals are scaled relative to that minimum length.

    Args:
        intervals (list[tuple[float,float]]): List of (start, end) bin ranges.

    Returns:
        list[float]: Scale factors proportional to interval lengths.
    """
    intervalLengths : list[float] = [interval[1]-interval[0] for interval in intervals]
    minimum = min([length for length in intervalLengths if length > 0], default=1)
    scales = [length/minimum for length in intervalLengths]
    return scales

def CreateIntervalScales(intervals : list[tuple[float,float]])->list[float]:
    intervalLengths : list[float] = [interval[1]-interval[0] for interval in intervals]
    minimum = min([length for length in intervalLengths if length > 0], default=1)
    scales : list[float] = [length/minimum for length in intervalLengths]
    return scales

def RescaleListOfLists(input: list[list[float]], scaleFactor: float, scaledXAxisValue: float = 0):
    result = []
    for sublist in input:
        result.append(RescaleList(sublist,scaleFactor,scaledXAxisValue))
    return result