from itertools import tee as _tee

def pairwise(iterable):
    try:
       from itertools import pairwise 
       return pairwise(iterable)
    except Exception:
        a, b = _tee(iterable)
        next(b, None)
        return zip(a, b)
