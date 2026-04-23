from itertools import tee as _tee
import warnings

def pairwise(iterable):
    try:
       from itertools import pairwise 
       return pairwise(iterable)
    except Exception:
        a, b = _tee(iterable)
        next(b, None)
        return zip(a, b)

class MethodWithoutEffectWarning(UserWarning):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
