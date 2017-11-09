''' Useful functions '''

import itertools
from collections import deque
import numpy as np


pi = 3.14159265358979323846
pi2 = 2 * pi
floatError = 2.0 ** -30


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

def floorLog2(v):
    return int(v).bit_length() - 1

def countMatching(iterable, matchFunc):
    return sum(matchFunc(v) for v in iterable)

def nearZero(v):
    return -floatError <= v <= floatError
def nearZeroWrap(v, wrap):
    v = v % wrap
    return not floatError < v < wrap - floatError
def nearZeroRad(angle):
    return nearZeroWrap(angle, pi2)

def normRad(angle):
    return (angle + pi) % pi2 - pi
def normRadPos(angle):
    return angle % pi2

@np.vectorize
def rround(v, prec=9):
    return round(v, prec)
@np.vectorize
def cround(v, prec=9):
    return complex(round(v.real, prec), round(v.imag, prec))

def isUnitary(op, allowScale=True):
    assert len(op.shape) == 2 and op.shape[0] == op.shape[1]
    n = op.shape[0]
    a = op.dot(op.conj().T)
    if allowScale and not nearZero(a[0,0]):
        a /= a[0,0]
    a -= np.identity(n)
    return nearZero(np.linalg.norm(a))  # / n

