
import itertools
import math

from util import pi, nearZero


def genRationalErrorBounds(error=0, maxNum=32,
                           maxDenum=64, factor=1):
    return sorted(
        (factor*num/denum - error, factor*num/denum + error, (num, denum))
        for num, denum in
            itertools.product(range(1,maxNum), range(1,maxDenum))
        if math.gcd(num, denum) <= 1
    )
def matchToBounds(val, bounds):
    # Binary search in sorted bounds
    minI, maxI = 0, len(bounds)
    while minI < maxI-1:
        i = (minI + maxI) // 2
        isLow = val < bounds[i][0]
        if isLow: maxI = i
        else: minI = i
    valMin, valMax, info = bounds[minI]
    if valMin <= val <= valMax:
        return info
    else:
        return None

printAngleError = 2**-20
printFracErrorBounds = genRationalErrorBounds(error=printAngleError)
def angleToStr(val):
    if nearZero(val): return '0'
    if val < 0:
        negStr = '-'
        sgn = -1
        val = -val
    else:
        negStr = ''
        sgn = 1
    if nearZero(val/pi - 1): return negStr+'π'
    piFraction = matchToBounds(val / pi, printFracErrorBounds)
    if piFraction is not None:
        num, denum = piFraction
        if denum == 1: return '{}π'.format(sgn * num)
        elif num == 1: return '{}π/{}'.format(negStr, denum)
        else: return '{}π/{}'.format(sgn * num, denum)
    fraction = matchToBounds(val, printFracErrorBounds)
    if fraction is not None:
        num, denum = fraction
        if denum == 1: return '{}'.format(sgn * num)
        else: return '{}/{}'.format(sgn * num, denum)
    if nearZero(val % 1):
        return '{}'.format(sgn * round(val))
    return '{:.4f}'.format(sgn * val)
def angleToLatex(val):
    if nearZero(val): return '0'
    if val < 0:
        negStr = '-'
        sgn = -1
        val = -val
    else:
        negStr = ''
        sgn = 1
    if nearZero(val/pi - 1): return negStr+'\pi'
    piFraction = matchToBounds(val / pi, printFracErrorBounds)
    if piFraction is not None:
        num, denum = piFraction
        if denum == 1: return '{}\\pi'.format(sgn * num)
        elif num == 1: return '\\frac{{{}\\pi}}{{{}}}'.format(negStr, denum)
        else: return '\\frac{{{}\pi}}{{{}}}'.format(sgn * num, denum)
    fraction = matchToBounds(val, printFracErrorBounds)
    if fraction is not None:
        num, denum = fraction
        if denum == 1: return '{}'.format(sgn * num)
        else: return '\\frac{{{}}}{{{}}}'.format(sgn * num, denum)
    if nearZero(val % 1):
        return '{}'.format(sgn * round(val))
    return '{:.4f}'.format(sgn * val)

