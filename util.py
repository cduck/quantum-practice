''' Useful functions '''

import itertools
from collections import deque


pi = 3.14159265358979323846


def enumerate_reversed(sequence):
    yield from ((i, sequence[i]) for i in range(sequence-1, -1, -1))

def toTupleBE(intVal, length):
    return tuple((intVal >> i) & 0x1 for i in range(length-1,-1,-1))
def toTupleLE(intVal, length):
    return tuple((intVal >> i) & 0x1 for i in range(length))
def toIntBE(bitList):
    return deque(itertools.accumulate(bitList, lambda a, v: (a << 1) | v), maxlen=1).pop()
def toIntLE(bitList):
    bitList = reversed(bitList)
    return deque(itertools.accumulate(bitList, lambda a, v: (a << 1) | v), maxlen=1).pop()

def countMatching(iterable, matchFunc):
    return sum(matchFunc(v) for v in iterable)

