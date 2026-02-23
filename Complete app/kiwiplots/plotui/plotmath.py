def isNear(val1: float, val2: float, tolerance : float=5)->bool:
    """
    Returns True, if two values are near to each other with given tolerance
    """
    return abs(val1 - val2) < tolerance


def ceilToNearestTen(number: float):
    """
    Rounds a number up to the nearest ten.
    
    Args:
        number: The number to round up.
    
    Returns:
        The number rounded up to the nearest ten.
    """
    return ((number // 10) + 1) * 10

def floorToNearestTen(number: float):
    """
    Rounds a number down to the nearest ten.
    
    Args:
        number: The number to round down.
    
    Returns:
        The number rounded down to the nearest ten.
    """
    return ((number // 10) - 1) * 10

def divideInterval(low: float, high: float, parts: int):
    """
    Divides an interval into a specified number of equally spaced parts.
    
    Args:
        low: The lower bound of the interval.
        high: The upper bound of the interval.
        parts: The number of parts to divide the interval into. If less than 2, returns [low, high].
    
    Returns:
        A list of values representing the division points, including the boundaries.
    """
    if parts < 2:
        return [low, high]

    step = (high - low) // (parts - 1)
    return [low + i * step for i in range(parts)]