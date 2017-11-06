''' Gate declarations '''

import collections.abc
from collections import namedtuple

import util

# Specific gate declarations at end


GateInstance = namedtuple('GateInstance', 'name, args, bits, divergent, measurement')
GateInstance.__repr__ = lambda self: (
    '{}({})'.format(self.name, ', '.join(map(str,self.bits)))  if self.args == () else
    '{}_{}({})'.format(self.name, ','.join(map(str,self.args)), ', '.join(map(str,self.bits))))
GateInstance.instanceOf = lambda self, g: self.name == g.name

class GenericGate:
    def __init__(self, name, size, numArgs, divergent=False, measurement=False):
        self.name = str(name)
        self.size = int(size)
        self.numArgs = int(numArgs)
        self.divergent = bool(divergent)
        self.measurement = bool(measurement)
    def __call__(self, *args):
        assert len(args) == self.numArgs, 'Incorrect number of arguments for generic gate'
        return Gate(self.name, self.size, args=args, divergent=self.divergent, measurement=self.measurement)

class Gate:
    __slots__ = ('name', 'size', 'args', 'divergent', 'measurement')
    def __init__(self, name, size, args=None, divergent=False, measurement=False):
        self.name = str(name)
        self.size = int(size)
        self.args = () if args is None else tuple(args)
        self.divergent = bool(divergent)
        self.measurement = bool(measurement)
    def makeInstance(self, bits):
        return GateInstance(self.name, self.args, tuple(bits), self.divergent, self.measurement)
    def applySingle(self, bits):
        assert len(bits) == self.size
        bits[0].state.applyGate(self, bits)
    def __call__(self, *bits, mask=None, littleEndian=None, bigEndian=None):
        if len(bits) == 1 and isinstance(bits[0], collections.abc.Sequence):
            bits = bits[0]
        if self.size == 1:
            if mask is None:
                mask = (1 for i in range(len(bits)))
            else:
                assert (littleEndian is None) != (bigEndian is None), 'Specify the mask endianness'
                if littleEndian is not None:
                    bitEndian = not littleEndian
                if bigEndian:
                    mask = util.toTupleBE(mask, len(bits))
                else:
                    mask = util.toTupleLE(mask, len(bits))
            for bit, m in zip(bits, mask):
                if m:
                    self.applySingle((bit,))
        else:
            self.applySingle(bits)


# Single bit measurement
M = Gate('M', 1, measurement=True)

# One bit gates
H = Gate('H', 1, divergent=True)
I1 = Gate('I1', 1)
X = Gate('X', 1)
Y = Gate('Y', 1)
Z = Gate('Z', 1)
S = Gate('S', 1)
Sd = Gate('Sd', 1)
T = Gate('T', 1)
Td = Gate('Td', 1)
Rx = GenericGate('Rx', 1, numArgs=1)
Ry = GenericGate('Ry', 1, numArgs=1)
Rz = GenericGate('Rz', 1, numArgs=1)

# Two bit gates
I2 = Gate('I2', 2)
SWAP = Gate('SWAP', 2)
CX = Gate('CX', 2); CNOT = CX
CY = Gate('CY', 2)
CZ = Gate('CZ', 2)
CS = Gate('CS', 2)
CSd = Gate('CSd', 2)
CT = Gate('CT', 2)
CTd = Gate('CTd', 2)
CRz = GenericGate('CRz', 2, numArgs=1)

# Three bit gates
I3 = Gate('I3', 3)
CSWAP = Gate('CSWAP', 3)
CCX = Gate('CCX', 3); TOFF = CCX
CCRz = GenericGate('CCRz', 3, numArgs=1)

