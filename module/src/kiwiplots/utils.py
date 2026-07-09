from itertools import tee as _tee
import warnings

def pairwise(iterable):
    """Pairwise function. Takes iterable and returns a new iterable, where every two consecutive items from the input are in a tuple.
    If possible, pairwise function from itertools is used. If wrong version of itertools is present, the function does it by itself.

    Args:
        iterable (iterable): new iterable

    Returns:
        _type_: _description_
    """
    try:
       from itertools import pairwise 
       return pairwise(iterable)
    except Exception:
        a, b = _tee(iterable)
        next(b, None)
        return zip(a, b)

class MethodWithoutEffectWarning(UserWarning):
    """Warning for functions which are not supposed to be used and which do no return anything and have no side effects.
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

def inheritdocstring(baseMethod):
    """Decorator for inheriting documentation string

    Args:
        baseMethod : method to inherit documentation from
    """
    def decorator(method):
        if baseMethod.__doc__:
            method.__doc__ = baseMethod.__doc__
        return method
    return decorator