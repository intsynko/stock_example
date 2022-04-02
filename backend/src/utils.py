from typing import Callable, Iterable


def iter_property(iteable: Iterable, *args: Callable):
    return ((i, *(func(i) for func in args)) for i in iteable)