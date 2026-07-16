from enum import Enum
class GameModes(Enum):
    """Possible game modes.
    """
    BarChart         = 1
    CandlestickChart = 2
    LineChart        = 3
    Histogram        = 4