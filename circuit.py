''' Circuit generation and representation classes '''

import gate
from gate import Gate
import util


class Qubit(int):
    def __new__(cls, index, *args, **kwargs):
        return super().__new__(cls, index)
    def __init__(self, index, state):
        self.state = state
    def __repr__(self):
        return 'Qubit({})'.format(super().__repr__())


class QuantumCircuit:
    def __init__(self, n=0):
        self.n = n
        self.bitObjs = tuple(Qubit(i, self) for i in range(n))
        self.ancillaBits = ()
        self.availableAncillaBits = ()
        self.history = []
    def __getitem__(self, arg):
        return self.bitObjs[arg]
    def newRegister(self, n):
        newBits = tuple(Qubit(i, self) for i in range(self.n, self.n+n))
        self.bitObjs += newBits
        self.n += n
        return newBits
    def newBit(self):
        return self.newRegister(1)[0]
    def borrowAncilla(self, n):
        if n <= len(self.availableAncillaBits):
            reg = self.availableAncillaBits[:n]
            self.availableAncillaBits = self.availableAncillaBits[n:]
        else:
            newBits = self.newRegister(n - len(self.availableAncillaBits))
            self.ancillaBits += newBits
            reg = self.availableAncillaBits + newBits
            self.availableAncillaBits = ()
        return reg
    def returnAncilla(self, bits):
        ''' Bits must be returned to zero before returning.
            Return in the reverse order that they were borrowed. '''
        # TODO: Keep sorted
        self.availableAncillaBits = bits + self.availableAncillaBits

    def applyGate(self, gate, bits):
        self.history.append(gate.makeInstance(bits))

    def debugEnterSub(self, subName):
        pass
    def debugLeaveSub(self):
        pass

    def countGate(self, gateOrName):
        if isinstance(gateOrName, Gate):
            gateOrName = gateOrName.name
        return util.countMatching(self.history, lambda g: g.name == gateOrName)
    def countM(self):
        return self.countGate(gate.M)

    def writeToFileNamed(self, fName):
        with open(fName, 'w') as f:
            self.writeToFile(f)
    def writeToFile(self, f):
        for gate in s.history:
            f.write(str(gate))
            f.write('\n')

