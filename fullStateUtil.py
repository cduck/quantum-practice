''' Useful functions for manipulating quantum state vectors '''

import itertools
import random
import numpy as np
from scipy import sparse

from gateOperators import complexDtype as stateDtype
import util


def tensorProduct(v1, *vals):
    out = v1
    for v in vals:
        out = np.kron(out, v)
    return out
def tensorProductSparse(v1, *vals):
    out = v1
    for v in vals:
        out = sparse.kron(out, v)
    return out

def createZeroState(n):
    psi = np.zeros(2**n, dtype=stateDtype)
    psi[0] = 1
    return psi
def createInitialState(*bitStates):
    ''' Bit 0 first, bit n-1 last '''
    psi = np.array([1], dtype=stateDtype)
    for psiI in bitStates:
        psi = tensorProduct(psi, psiI)
    return psi
def createUniformSuperposition(n):
    psi = np.ones(2**n, dtype=stateDtype)
    #psi /= 2**n  # Don't bother to normalize
    return psi

def expandGate(baseGate, finalN):
    baseN = baseGate.shape[0].bit_length() - 1  # Fast log2 of shape[0]
    numCopies = 2**(finalN-baseN)
    copyInterval = 2**baseN
    gate = np.zeros((2**finalN,)*2, dtype=baseGate.dtype)
    for i in range(numCopies):
        gate[i*copyInterval:(i+1)*copyInterval,i*copyInterval:(i+1)*copyInterval] = baseGate
    return gate

def swapGate(*bitMap):
    n = len(bitMap)
    gate = np.zeros((2**n,)*2, dtype=np.int)  # TODO: Sparse
    for idxs in itertools.product((0,1), repeat=n):
        x, xr = 0, 0
        for i in range(n):
            x = (x<<1) | idxs[i]
            xr = (xr<<1) | idxs[bitMap[i]]
        gate[xr, x] = 1
    return gate
def swapGates(*bitMap):
    gate = swapGate(*bitMap)
    return gate, gate.T


def apply(psi, *gates):
    for gate in gates:
        psi2 = np.dot(gate, psi)
    return psi2

def probabilityOfMeasure(psi, bitI, state=0):
    n = len(psi).bit_length() - 1
    # TODO: No temp array creation
    shapedPsi = psi.reshape((2,)*n)
    squaredPsi = (shapedPsi.conj() * shapedPsi).real
    sums = np.sum(squaredPsi, axis=tuple(i for i in range(n) if i!=bitI))
    return sums[state] / np.sum(sums)

def probabilityOfMeasureAll(psi, bitsValue):
    n = len(psi).bit_length() - 1
    a = psi[bitsValue]
    p = (a.conj() * a).real
    squaredPsi = (psi.conj() * psi).real
    return p / np.sum(squaredPsi)

def measure(psi, bitI, inPlace=False):
    n = len(psi).bit_length() - 1
    prob = probabilityOfMeasure(psi, bitI, state=0)
    measuredBit = int(random.random() >= prob)
    s = slice(None)
    if not inPlace:
        psi = psi.copy()
    psi.reshape((2,)*n)[tuple(1-measuredBit if i==bitI else s for i in range(n))] = 0
    # Don't normalize
    if inPlace:
        return measuredBit, prob
    else:
        return psi, measuredBit, prob


def exactMeasureResults(psi):
    ''' Calculate the exact probabilities that any output is measured. '''
    n = len(psi).bit_length() - 1
    counter = {}
    for bitsVal in range(2**n):
        shapedPsi = psi.reshape((2,)*n)
        squaredPsi = (shapedPsi.conj() * shapedPsi).real
        normConst = np.sum(squaredPsi)
        a = psi[bitsVal]
        p = (a.conj() * a).real
        prob = round(p / normConst, 5)
        if p / normConst > 1e-10:
            counter[bitsVal] = prob
    return {util.toTupleBE(k, n):v for k, v in counter.items()}

